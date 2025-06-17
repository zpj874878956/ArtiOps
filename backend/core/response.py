from rest_framework.response import Response
import time

class APIResponse(Response):
    """
    自定义API响应类，统一API响应格式
    """
    def __init__(self, data=None, code=200, message="操作成功", status=None, headers=None, **kwargs):
        response_data = {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(time.time())
        }
        # 添加额外数据
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status, headers=headers)


def success_response(data=None, message="操作成功", **kwargs):
    """
    成功响应
    """
    return APIResponse(data=data, code=200, message=message, **kwargs)


def error_response(message="操作失败", code=400, data=None, status=400, **kwargs):
    """
    错误响应
    """
    return APIResponse(data=data, code=code, message=message, status=status, **kwargs) 