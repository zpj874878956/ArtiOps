from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import CommandExecution, ExecutionLog


@receiver(pre_save, sender=CommandExecution)
def handle_execution_status_change(sender, instance, **kwargs):
    """
    处理命令执行状态变更
    
    当命令执行状态发生变化时，自动设置开始时间和结束时间
    """
    # 获取数据库中的原始对象
    try:
        old_instance = CommandExecution.objects.get(pk=instance.pk)
        old_status = old_instance.status
    except CommandExecution.DoesNotExist:
        # 新创建的对象
        old_status = None
    
    # 状态变更为 'running'，设置开始时间
    if instance.status == 'running' and old_status != 'running':
        if not instance.start_time:
            instance.start_time = timezone.now()
    
    # 状态变更为 'success', 'failed', 'canceled'，设置结束时间
    if instance.status in ['success', 'failed', 'canceled'] and old_status not in ['success', 'failed', 'canceled']:
        if not instance.end_time:
            instance.end_time = timezone.now()


@receiver(post_save, sender=CommandExecution)
def log_execution_status_change(sender, instance, created, **kwargs):
    """
    记录命令执行状态变更日志
    
    当命令执行状态发生变化时，自动创建相应的日志记录
    """
    if created:
        # 新创建的命令执行，记录创建日志
        ExecutionLog.objects.create(
            execution=instance,
            host='system',
            level='info',
            content=f'命令执行任务 "{instance.name}" 已创建'
        )
    else:
        # 获取数据库中的原始对象
        try:
            old_instance = CommandExecution.objects.get(pk=instance.pk)
            old_status = old_instance.status
        except CommandExecution.DoesNotExist:
            return
        
        # 状态发生变化，记录状态变更日志
        if instance.status != old_status:
            status_map = {
                'pending': '等待执行',
                'running': '正在执行',
                'success': '执行成功',
                'failed': '执行失败',
                'canceled': '已取消'
            }
            
            status_text = status_map.get(instance.status, instance.status)
            
            ExecutionLog.objects.create(
                execution=instance,
                host='system',
                level='info' if instance.status in ['success', 'pending', 'running'] else 'error',
                content=f'命令执行状态变更为: {status_text}'
            )