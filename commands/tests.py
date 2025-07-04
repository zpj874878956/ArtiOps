from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import json
import re

from .models import CommandTemplate, CommandExecution, ExecutionLog, DangerousCommand
from .utils import CommandChecker, CommandExecutor


User = get_user_model()


class CommandTemplateModelTest(TestCase):
    """命令模板模型测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试命令模板
        self.template = CommandTemplate.objects.create(
            name='测试模板',
            type='shell',
            content='echo "Hello World"',
            description='测试描述',
            is_public=True,
            created_by=self.user
        )
    
    def test_template_creation(self):
        """测试命令模板创建"""
        self.assertEqual(self.template.name, '测试模板')
        self.assertEqual(self.template.type, 'shell')
        self.assertEqual(self.template.content, 'echo "Hello World"')
        self.assertEqual(self.template.description, '测试描述')
        self.assertTrue(self.template.is_public)
        self.assertEqual(self.template.created_by, self.user)
    
    def test_template_str_method(self):
        """测试命令模板字符串表示"""
        self.assertEqual(str(self.template), '测试模板')


class CommandExecutionModelTest(TestCase):
    """命令执行模型测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试命令模板
        self.template = CommandTemplate.objects.create(
            name='测试模板',
            type='shell',
            content='echo "Hello World"',
            description='测试描述',
            is_public=True,
            created_by=self.user
        )
        
        # 创建测试命令执行
        self.execution = CommandExecution.objects.create(
            name='测试执行',
            execution_type='shell',
            command='echo "Hello World"',
            template=self.template,
            target_hosts='localhost',
            parameters=json.dumps({'timeout': 30}),
            status='pending',
            created_by=self.user
        )
    
    def test_execution_creation(self):
        """测试命令执行创建"""
        self.assertEqual(self.execution.name, '测试执行')
        self.assertEqual(self.execution.execution_type, 'shell')
        self.assertEqual(self.execution.command, 'echo "Hello World"')
        self.assertEqual(self.execution.template, self.template)
        self.assertEqual(self.execution.target_hosts, 'localhost')
        self.assertEqual(json.loads(self.execution.parameters), {'timeout': 30})
        self.assertEqual(self.execution.status, 'pending')
        self.assertEqual(self.execution.created_by, self.user)
    
    def test_execution_str_method(self):
        """测试命令执行字符串表示"""
        self.assertEqual(str(self.execution), '测试执行')
    
    def test_execution_duration(self):
        """测试命令执行持续时间"""
        # 未完成的执行持续时间应为None
        self.assertIsNone(self.execution.duration)
        
        # 设置开始和结束时间
        import datetime
        from django.utils import timezone
        
        now = timezone.now()
        self.execution.start_time = now
        self.execution.end_time = now + datetime.timedelta(seconds=10)
        self.execution.save()
        
        # 检查持续时间是否为10秒
        self.assertEqual(self.execution.duration, 10)


class ExecutionLogModelTest(TestCase):
    """执行日志模型测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试命令执行
        self.execution = CommandExecution.objects.create(
            name='测试执行',
            execution_type='shell',
            command='echo "Hello World"',
            target_hosts='localhost',
            parameters=json.dumps({'timeout': 30}),
            status='pending',
            created_by=self.user
        )
        
        # 创建测试执行日志
        self.log = ExecutionLog.objects.create(
            execution=self.execution,
            host='localhost',
            level='info',
            content='命令开始执行'
        )
    
    def test_log_creation(self):
        """测试执行日志创建"""
        self.assertEqual(self.log.execution, self.execution)
        self.assertEqual(self.log.host, 'localhost')
        self.assertEqual(self.log.level, 'info')
        self.assertEqual(self.log.content, '命令开始执行')
    
    def test_log_str_method(self):
        """测试执行日志字符串表示"""
        expected = f'[localhost][info] 命令开始执行'
        self.assertEqual(str(self.log), expected)


class DangerousCommandModelTest(TestCase):
    """危险命令模型测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试危险命令
        self.dangerous_cmd = DangerousCommand.objects.create(
            pattern='rm -rf /',
            match_type='exact',
            description='删除根目录',
            action='forbid',
            created_by=self.user
        )
    
    def test_dangerous_command_creation(self):
        """测试危险命令创建"""
        self.assertEqual(self.dangerous_cmd.pattern, 'rm -rf /')
        self.assertEqual(self.dangerous_cmd.match_type, 'exact')
        self.assertEqual(self.dangerous_cmd.description, '删除根目录')
        self.assertEqual(self.dangerous_cmd.action, 'forbid')
        self.assertEqual(self.dangerous_cmd.created_by, self.user)
    
    def test_dangerous_command_str_method(self):
        """测试危险命令字符串表示"""
        self.assertEqual(str(self.dangerous_cmd), 'rm -rf /')


class CommandCheckerTest(TestCase):
    """命令检查器测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试危险命令
        DangerousCommand.objects.create(
            pattern='rm -rf /',
            match_type='exact',
            description='删除根目录',
            action='forbid',
            created_by=self.user
        )
        
        DangerousCommand.objects.create(
            pattern='rm -rf',
            match_type='contains',
            description='删除文件',
            action='warn',
            created_by=self.user
        )
        
        DangerousCommand.objects.create(
            pattern='^sudo.*reboot',
            match_type='regex',
            description='重启服务器',
            action='log',
            created_by=self.user
        )
        
        # 创建命令检查器
        self.checker = CommandChecker()
    
    def test_exact_match(self):
        """测试精确匹配"""
        result = self.checker.check_command('rm -rf /')
        self.assertTrue(result['is_dangerous'])
        self.assertEqual(result['action'], 'forbid')
        self.assertEqual(result['description'], '删除根目录')
    
    def test_contains_match(self):
        """测试包含匹配"""
        result = self.checker.check_command('rm -rf /tmp/test')
        self.assertTrue(result['is_dangerous'])
        self.assertEqual(result['action'], 'warn')
        self.assertEqual(result['description'], '删除文件')
    
    def test_regex_match(self):
        """测试正则匹配"""
        result = self.checker.check_command('sudo systemctl reboot')
        self.assertTrue(result['is_dangerous'])
        self.assertEqual(result['action'], 'log')
        self.assertEqual(result['description'], '重启服务器')
    
    def test_safe_command(self):
        """测试安全命令"""
        result = self.checker.check_command('ls -la')
        self.assertFalse(result['is_dangerous'])


class CommandExecutorTest(TestCase):
    """命令执行器测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试命令执行
        self.execution = CommandExecution.objects.create(
            name='测试执行',
            execution_type='shell',
            command='echo "Hello World"',
            target_hosts='localhost',
            parameters=json.dumps({'timeout': 30, 'concurrency': 1}),
            status='pending',
            created_by=self.user
        )
        
        # 创建命令执行器
        self.executor = CommandExecutor(self.execution)
    
    def test_executor_initialization(self):
        """测试执行器初始化"""
        self.assertEqual(self.executor.execution, self.execution)
        self.assertEqual(self.executor.command, 'echo "Hello World"')
        self.assertEqual(self.executor.hosts, ['localhost'])
        self.assertEqual(self.executor.timeout, 30)
        self.assertEqual(self.executor.concurrency, 1)
    
    def test_parse_parameters(self):
        """测试参数解析"""
        params = {'timeout': 60, 'concurrency': 5, 'fail_policy': 'continue'}
        self.execution.parameters = json.dumps(params)
        self.execution.save()
        
        executor = CommandExecutor(self.execution)
        self.assertEqual(executor.timeout, 60)
        self.assertEqual(executor.concurrency, 5)
        self.assertEqual(executor.fail_policy, 'continue')
    
    def test_parse_hosts(self):
        """测试主机解析"""
        # 测试逗号分隔的主机列表
        self.execution.target_hosts = 'host1,host2,host3'
        self.execution.save()
        
        executor = CommandExecutor(self.execution)
        self.assertEqual(executor.hosts, ['host1', 'host2', 'host3'])
        
        # 测试换行分隔的主机列表
        self.execution.target_hosts = 'host1\nhost2\nhost3'
        self.execution.save()
        
        executor = CommandExecutor(self.execution)
        self.assertEqual(executor.hosts, ['host1', 'host2', 'host3'])


class APIViewTest(APITestCase):
    """API视图测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试命令模板
        self.template = CommandTemplate.objects.create(
            name='测试模板',
            type='shell',
            content='echo "Hello World"',
            description='测试描述',
            is_public=True,
            created_by=self.user
        )
        
        # 创建测试命令执行
        self.execution = CommandExecution.objects.create(
            name='测试执行',
            execution_type='shell',
            command='echo "Hello World"',
            template=self.template,
            target_hosts='localhost',
            parameters=json.dumps({'timeout': 30}),
            status='pending',
            created_by=self.user
        )
        
        # 创建测试危险命令
        self.dangerous_cmd = DangerousCommand.objects.create(
            pattern='rm -rf /',
            match_type='exact',
            description='删除根目录',
            action='forbid',
            created_by=self.user
        )
    
    def test_command_template_list(self):
        """测试命令模板列表"""
        url = reverse('command-template-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_command_template_create(self):
        """测试创建命令模板"""
        url = reverse('command-template-list')
        data = {
            'name': '新模板',
            'type': 'ansible',
            'content': 'ping',
            'description': '新描述',
            'is_public': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommandTemplate.objects.count(), 2)
    
    def test_command_execution_list(self):
        """测试命令执行列表"""
        url = reverse('command-execution-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_command_execution_create(self):
        """测试创建命令执行"""
        url = reverse('command-execution-list')
        data = {
            'name': '新执行',
            'execution_type': 'shell',
            'command': 'ls -la',
            'target_hosts': 'localhost',
            'parameters': {'timeout': 30}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommandExecution.objects.count(), 2)
    
    def test_dangerous_command_check(self):
        """测试危险命令检查"""
        url = reverse('dangerous-command-check')
        data = {'command': 'rm -rf /'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_dangerous'])
        self.assertEqual(response.data['action'], 'forbid')
    
    def test_execution_log_list(self):
        """测试执行日志列表"""
        # 创建测试日志
        ExecutionLog.objects.create(
            execution=self.execution,
            host='localhost',
            level='info',
            content='命令开始执行'
        )
        
        url = reverse('execution-log-list')
        response = self.client.get(url, {'execution_id': self.execution.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
