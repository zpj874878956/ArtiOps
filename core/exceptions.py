from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
import logging
import traceback
import time

logger = logging.getLogger('apps')

def custom_exception_handler(exc, context):
    """
    自定义异常处理函数，统一API响应格式
    """
    # 调用DRF默认的异常处理程序
    response = exception_handler(exc, context)
    
    # 如果是未处理的异常
    if response is None:
        logger.error(f'未处理异常: {exc}\n{traceback.format_exc()}')
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': '服务器内部错误',
            'data': None,
            'timestamp': int(time.time())
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 处理Http404异常
    if isinstance(exc, Http404):
        return Response({
            'code': status.HTTP_404_NOT_FOUND,
            'message': '请求的资源不存在',
            'data': None,
            'timestamp': int(time.time())
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 处理验证错误
    if hasattr(exc, 'detail'):
        return Response({
            'code': response.status_code,
            'message': '请求参数错误',
            'data': exc.detail,
            'timestamp': int(time.time())
        }, status=response.status_code)
    
    # 其他异常
    return Response({
        'code': response.status_code,
        'message': str(exc),
        'data': None,
        'timestamp': int(time.time())
    }, status=response.status_code) 