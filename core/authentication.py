from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    自定义JWT认证类，为Swagger路径禁用认证
    """
    def authenticate(self, request):
        # 检查是否是Swagger相关的路径
        path = request.path
        swagger_paths = [
            '/swagger/',
            '/swagger/swagger-ui',
            '/swagger/swagger-ui.css',
            '/swagger/swagger-ui-bundle',
            '/swagger/swagger-ui-standalone-preset',
            '/swagger/favicon-32x32.png',
            '/swagger/favicon-16x16.png',
        ]
        
        # 如果路径是Swagger相关或包含format=openapi参数，则跳过认证
        if (getattr(request, '_swagger_path', False) or 
            path.startswith('/swagger/') or 
            any(path.startswith(p) for p in swagger_paths) or
            'format=openapi' in request.GET.urlencode()):
            return None
            
        return super().authenticate(request) 