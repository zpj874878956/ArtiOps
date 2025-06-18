from django.utils.deprecation import MiddlewareMixin

class SwaggerPermissionMiddleware(MiddlewareMixin):
    """
    为Swagger路径禁用认证的中间件
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 处理所有Swagger相关路径
        if request.path.startswith('/swagger/'):
            setattr(request, '_swagger_path', True)
            
        # 处理format=openapi的请求
        if 'format=openapi' in request.GET.urlencode():
            setattr(request, '_swagger_path', True)
            
        return None 