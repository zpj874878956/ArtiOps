import re
import os
import json
import time
import logging
import subprocess
from datetime import datetime
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import CommandExecution, ExecutionLog, DangerousCommand

# 配置日志记录器
logger = logging.getLogger('commands')

class CommandChecker:
    """
    命令安全检查工具，用于检查命令是否匹配危险命令规则
    """
    
    @staticmethod
    def check_command(command, command_type='shell'):
        """
        检查命令是否匹配危险命令规则
        
        Args:
            command (str): 要检查的命令内容
            command_type (str): 命令类型，可选值：shell, ansible, sql
            
        Returns:
            dict: 包含检查结果的字典，格式如下：
                {
                    'is_dangerous': bool,  # 是否为危险命令
                    'action': str,  # 处理动作：forbid, warn, log
                    'message': str,  # 提示信息
                    'matched_rule': dict or None  # 匹配的规则详情
                }
        """
        # 获取所有危险命令规则
        dangerous_commands = DangerousCommand.objects.all().order_by('created_at')
        
        # 检查命令是否匹配任何规则
        for rule in dangerous_commands:
            if CommandChecker._match_rule(command, rule):
                return {
                    'is_dangerous': True,
                    'action': rule.action,
                    'message': rule.description or f'命令匹配危险规则：{rule.pattern}',
                    'matched_rule': {
                        'id': rule.id,
                        'pattern': rule.pattern,
                        'match_type': rule.match_type,
                        'action': rule.action,
                        'description': rule.description
                    }
                }
        
        # 未匹配任何规则，命令安全
        return {
            'is_dangerous': False,
            'action': None,
            'message': '命令安全，可以执行',
            'matched_rule': None
        }
    
    @staticmethod
    def _match_rule(command, rule):
        """
        检查命令是否匹配指定规则
        
        Args:
            command (str): 要检查的命令内容
            rule (DangerousCommand): 危险命令规则对象
            
        Returns:
            bool: 是否匹配
        """
        pattern = rule.pattern
        match_type = rule.match_type
        
        if match_type == 'exact':
            return command.strip() == pattern
        elif match_type == 'contains':
            return pattern in command
        elif match_type == 'startswith':
            return command.strip().startswith(pattern)
        elif match_type == 'endswith':
            return command.strip().endswith(pattern)
        elif match_type == 'regex':
            try:
                return bool(re.search(pattern, command))
            except re.error:
                logger.error(f"正则表达式错误: {pattern}")
                return False
        
        return False


class CommandExecutor:
    """
    命令执行器，用于执行Shell或Ansible命令
    """
    
    def __init__(self, execution_id):
        """
        初始化命令执行器
        
        Args:
            execution_id (int): 命令执行记录ID
        """
        self.execution_id = execution_id
        self.execution = CommandExecution.objects.get(id=execution_id)
        self.process = None
        self.is_running = False
        self.lock = Lock()
        self.start_time = None
        self.end_time = None
    
    def execute(self):
        """
        执行命令
        
        Returns:
            bool: 执行是否成功启动
        """
        # 检查命令是否已经在运行
        if self.is_running:
            return False
        
        # 更新执行状态为运行中
        with transaction.atomic():
            self.execution.status = 'running'
            self.execution.start_time = timezone.now()
            self.execution.save(update_fields=['status', 'start_time'])
        
        # 记录开始时间
        self.start_time = time.time()
        
        # 根据执行类型选择执行方法
        if self.execution.execution_type == 'shell':
            # 启动线程执行Shell命令
            thread = Thread(target=self._execute_shell)
            thread.daemon = True
            thread.start()
        elif self.execution.execution_type == 'ansible':
            # 启动线程执行Ansible命令
            thread = Thread(target=self._execute_ansible)
            thread.daemon = True
            thread.start()
        else:
            # 不支持的执行类型
            self._log_execution(f"不支持的执行类型: {self.execution.execution_type}", level='error')
            self._update_execution_status('failed', f"不支持的执行类型: {self.execution.execution_type}")
            return False
        
        return True
    
    def _execute_shell(self):
        """
        执行Shell命令
        """
        with self.lock:
            self.is_running = True
        
        try:
            # 解析目标主机
            target_hosts = json.loads(self.execution.target_hosts)
            
            # 解析执行参数
            params = json.loads(self.execution.execution_params) if self.execution.execution_params else {}
            concurrency = params.get('concurrency', 5)  # 默认并发数为5
            timeout = params.get('timeout', 300)  # 默认超时时间为300秒
            fail_policy = params.get('fail_policy', 'continue')  # 默认失败策略为继续执行
            
            # 记录执行信息
            self._log_execution(f"开始执行Shell命令，目标主机数量: {len(target_hosts)}，并发数: {concurrency}")
            self._log_execution(f"命令内容: {self.execution.command_content}")
            
            # 使用线程池并发执行命令
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for host in target_hosts:
                    futures.append(executor.submit(self._execute_shell_on_host, host, timeout))
                
                # 等待所有任务完成
                failed_hosts = []
                for future in futures:
                    try:
                        host, success = future.result()
                        if not success and fail_policy == 'abort':
                            # 如果失败策略为中止，则取消所有未完成的任务
                            for f in futures:
                                if not f.done():
                                    f.cancel()
                            failed_hosts.append(host)
                            break
                        elif not success:
                            failed_hosts.append(host)
                    except Exception as e:
                        self._log_execution(f"执行任务时发生异常: {str(e)}", level='error')
            
            # 更新执行状态
            if failed_hosts:
                if len(failed_hosts) == len(target_hosts):
                    self._update_execution_status('failed', f"所有主机执行失败")
                else:
                    self._update_execution_status('partial', f"{len(failed_hosts)}/{len(target_hosts)} 个主机执行失败")
            else:
                self._update_execution_status('success', "所有主机执行成功")
        
        except Exception as e:
            self._log_execution(f"执行Shell命令时发生异常: {str(e)}", level='error')
            self._update_execution_status('failed', f"执行异常: {str(e)}")
        
        finally:
            with self.lock:
                self.is_running = False
    
    def _execute_shell_on_host(self, host, timeout):
        """
        在指定主机上执行Shell命令
        
        Args:
            host (dict): 主机信息，包含id, name, ip等字段
            timeout (int): 命令执行超时时间（秒）
            
        Returns:
            tuple: (host, success) 主机信息和执行是否成功
        """
        host_id = host.get('id')
        host_name = host.get('name', 'Unknown')
        host_ip = host.get('ip', 'Unknown')
        
        self._log_execution(f"开始在主机 {host_name}({host_ip}) 上执行命令", host_id=host_id)
        
        try:
            # 这里应该根据实际情况实现SSH连接并执行命令
            # 以下为模拟实现，实际项目中应替换为真实的SSH连接和命令执行逻辑
            
            # 模拟命令执行
            command = self.execution.command_content
            self._log_execution(f"执行命令: {command}", host_id=host_id)
            
            # 模拟执行结果
            # 在实际项目中，这里应该使用paramiko等库建立SSH连接并执行命令
            time.sleep(2)  # 模拟命令执行时间
            
            # 随机模拟成功或失败（实际项目中应根据真实执行结果判断）
            import random
            success = random.choice([True, True, True, False])  # 75%概率成功
            
            if success:
                self._log_execution(f"命令执行成功", host_id=host_id)
                return host, True
            else:
                self._log_execution(f"命令执行失败: 模拟的执行错误", host_id=host_id, level='error')
                return host, False
        
        except Exception as e:
            self._log_execution(f"在主机 {host_name}({host_ip}) 上执行命令时发生异常: {str(e)}", 
                               host_id=host_id, level='error')
            return host, False
    
    def _execute_ansible(self):
        """
        执行Ansible命令
        """
        with self.lock:
            self.is_running = True
        
        try:
            # 解析目标主机
            target_hosts = json.loads(self.execution.target_hosts)
            host_ids = [host.get('id') for host in target_hosts]
            host_names = [host.get('name', 'Unknown') for host in target_hosts]
            
            # 解析执行参数
            params = json.loads(self.execution.execution_params) if self.execution.execution_params else {}
            timeout = params.get('timeout', 600)  # 默认超时时间为600秒
            
            # 记录执行信息
            self._log_execution(f"开始执行Ansible命令，目标主机: {', '.join(host_names)}")
            self._log_execution(f"命令内容: {self.execution.command_content}")
            
            # 创建临时主机清单文件
            inventory_file = self._create_ansible_inventory(target_hosts)
            
            # 构建Ansible命令
            ansible_cmd = self._build_ansible_command(inventory_file)
            
            # 执行Ansible命令
            self._log_execution(f"执行Ansible命令: {' '.join(ansible_cmd)}")
            
            # 启动子进程执行命令
            self.process = subprocess.Popen(
                ansible_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # 行缓冲
            )
            
            # 读取标准输出和标准错误
            stdout_thread = Thread(target=self._read_output, args=(self.process.stdout, 'info'))
            stderr_thread = Thread(target=self._read_output, args=(self.process.stderr, 'error'))
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待命令执行完成或超时
            try:
                return_code = self.process.wait(timeout=timeout)
                
                # 等待输出线程结束
                stdout_thread.join()
                stderr_thread.join()
                
                # 根据返回码更新执行状态
                if return_code == 0:
                    self._update_execution_status('success', "Ansible命令执行成功")
                else:
                    self._update_execution_status('failed', f"Ansible命令执行失败，返回码: {return_code}")
            
            except subprocess.TimeoutExpired:
                # 命令执行超时，终止进程
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                
                self._log_execution(f"命令执行超时（{timeout}秒）", level='error')
                self._update_execution_status('timeout', f"命令执行超时（{timeout}秒）")
            
            # 清理临时文件
            if os.path.exists(inventory_file):
                os.remove(inventory_file)
        
        except Exception as e:
            self._log_execution(f"执行Ansible命令时发生异常: {str(e)}", level='error')
            self._update_execution_status('failed', f"执行异常: {str(e)}")
        
        finally:
            with self.lock:
                self.is_running = False
    
    def _create_ansible_inventory(self, hosts):
        """
        创建Ansible临时主机清单文件
        
        Args:
            hosts (list): 主机列表
            
        Returns:
            str: 临时主机清单文件路径
        """
        # 创建临时目录（如果不存在）
        temp_dir = os.path.join(settings.BASE_DIR, 'tmp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建临时主机清单文件
        inventory_file = os.path.join(temp_dir, f"inventory_{self.execution_id}_{int(time.time())}.ini")
        
        with open(inventory_file, 'w') as f:
            f.write("[targets]\n")
            
            for host in hosts:
                host_ip = host.get('ip')
                host_name = host.get('name', host_ip)
                ssh_port = host.get('ssh_port', 22)
                ssh_user = host.get('ssh_user', 'root')
                
                # 添加主机到清单文件
                f.write(f"{host_name} ansible_host={host_ip} ansible_port={ssh_port} ansible_user={ssh_user}\n")
        
        return inventory_file
    
    def _build_ansible_command(self, inventory_file):
        """
        构建Ansible命令
        
        Args:
            inventory_file (str): 主机清单文件路径
            
        Returns:
            list: Ansible命令参数列表
        """
        # 解析命令内容
        command_content = self.execution.command_content.strip()
        
        # 解析执行参数
        params = json.loads(self.execution.execution_params) if self.execution.execution_params else {}
        
        # 构建基本命令
        cmd = ['ansible', '-i', inventory_file, 'targets']
        
        # 判断命令类型（ad-hoc命令或playbook）
        if command_content.endswith('.yml') or command_content.endswith('.yaml'):
            # 如果命令内容是YAML文件路径，则使用ansible-playbook命令
            cmd = ['ansible-playbook', '-i', inventory_file]
            cmd.append(command_content)
        else:
            # 否则使用ansible ad-hoc命令
            # 解析模块和参数
            if ' ' in command_content:
                module, args = command_content.split(' ', 1)
                cmd.extend(['-m', module, '-a', args])
            else:
                cmd.extend(['-m', command_content])
        
        # 添加额外参数
        if 'extra_vars' in params:
            for key, value in params['extra_vars'].items():
                cmd.extend(['--extra-vars', f"{key}={value}"])
        
        if 'verbose' in params and params['verbose']:
            cmd.append('-v')
        
        return cmd
    
    def _read_output(self, pipe, level):
        """
        读取命令输出并记录日志
        
        Args:
            pipe: 子进程输出管道
            level (str): 日志级别
        """
        for line in pipe:
            line = line.strip()
            if line:
                self._log_execution(line, level=level)
    
    def cancel(self):
        """
        取消命令执行
        
        Returns:
            bool: 是否成功取消
        """
        with self.lock:
            if not self.is_running:
                return False
            
            if self.process:
                # 尝试终止进程
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                    
                    self._log_execution("命令执行已取消", level='warning')
                    self._update_execution_status('canceled', "命令执行已取消")
                    return True
                except Exception as e:
                    self._log_execution(f"取消命令执行时发生异常: {str(e)}", level='error')
                    return False
            else:
                # 如果没有进程对象（例如Shell命令），则只更新状态
                self._log_execution("命令执行已取消", level='warning')
                self._update_execution_status('canceled', "命令执行已取消")
                return True
    
    def _log_execution(self, message, host_id=None, level='info'):
        """
        记录执行日志
        
        Args:
            message (str): 日志消息
            host_id (int, optional): 主机ID
            level (str): 日志级别，可选值：info, warning, error, debug
        """
        # 创建执行日志记录
        ExecutionLog.objects.create(
            execution=self.execution,
            host_id=host_id,
            log_level=level,
            log_content=message,
            log_time=timezone.now()
        )
        
        # 同时记录到系统日志
        log_method = getattr(logger, level, logger.info)
        log_method(f"[Execution #{self.execution_id}] {message}")
    
    def _update_execution_status(self, status, result=None):
        """
        更新命令执行状态
        
        Args:
            status (str): 执行状态
            result (str, optional): 执行结果
        """
        # 计算执行时间
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time if self.start_time else 0
        
        # 更新执行记录
        with transaction.atomic():
            self.execution.status = status
            self.execution.result = result
            self.execution.end_time = timezone.now()
            self.execution.execution_time = execution_time
            self.execution.save(update_fields=['status', 'result', 'end_time', 'execution_time'])


# 命令执行器实例字典，用于存储正在运行的命令执行器
execution_instances = {}

def get_executor(execution_id):
    """
    获取命令执行器实例
    
    Args:
        execution_id (int): 命令执行记录ID
        
    Returns:
        CommandExecutor: 命令执行器实例，如果不存在则返回None
    """
    return execution_instances.get(execution_id)

def create_executor(execution_id):
    """
    创建命令执行器实例
    
    Args:
        execution_id (int): 命令执行记录ID
        
    Returns:
        CommandExecutor: 命令执行器实例
    """
    executor = CommandExecutor(execution_id)
    execution_instances[execution_id] = executor
    return executor

def remove_executor(execution_id):
    """
    移除命令执行器实例
    
    Args:
        execution_id (int): 命令执行记录ID
        
    Returns:
        bool: 是否成功移除
    """
    if execution_id in execution_instances:
        del execution_instances[execution_id]
        return True
    return False