from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AccessLog, ExternalSystem, UserFavorite


@receiver(post_save, sender=AccessLog)
def update_system_score_on_access(sender, instance, created, **kwargs):
    """
    当创建新的访问日志时，更新系统的评分
    """
    if created:
        system = instance.system
        # 系统访问计数已在视图中更新，这里只需要重新计算评分
        system.calculate_score()
        system.save(update_fields=['score'])


@receiver(post_save, sender=UserFavorite)
def update_system_score_on_favorite(sender, instance, created, **kwargs):
    """
    当用户收藏系统时，更新系统的评分
    """
    if created:
        system = instance.system
        system.calculate_score()
        system.save(update_fields=['score'])


@receiver(post_delete, sender=UserFavorite)
def update_system_score_on_unfavorite(sender, instance, **kwargs):
    """
    当用户取消收藏系统时，更新系统的评分
    """
    try:
        system = instance.system
        system.calculate_score()
        system.save(update_fields=['score'])
    except ExternalSystem.DoesNotExist:
        # 如果系统已被删除，则忽略
        pass