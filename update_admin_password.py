#!/usr/bin/env python
"""
更新管理员密码脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入Django模型
from django.contrib.auth.hashers import make_password
from apps.users.models import User

def update_admin_password():
    """更新管理员密码"""
    try:
        admin = User.objects.get(username='admin')
        password = 'Admin@2023'
        
        # 使用Django的make_password函数生成密码哈希
        admin.password = make_password(password)
        admin.save()
        
        print(f"✅ 管理员密码已更新为: {password}")
        print(f"密码哈希: {admin.password}")
        return True
    except User.DoesNotExist:
        print("❌ 管理员用户不存在")
        return False
    except Exception as e:
        print(f"❌ 更新密码时出错: {e}")
        return False

if __name__ == "__main__":
    update_admin_password() 