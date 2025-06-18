#!/usr/bin/env python
"""
登录测试脚本
用于验证用户是否存在并测试密码验证
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入Django模型
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from apps.users.models import User, Role

def test_user_exists(username):
    """测试用户是否存在"""
    try:
        user = User.objects.get(username=username)
        print(f"✅ 用户 {username} 存在")
        return user
    except User.DoesNotExist:
        print(f"❌ 用户 {username} 不存在")
        return None

def test_password(user, password):
    """测试密码是否正确"""
    if user:
        if check_password(password, user.password):
            print(f"✅ 密码正确")
            return True
        else:
            print(f"❌ 密码错误")
            # 打印存储的密码哈希值，用于调试
            print(f"存储的密码哈希: {user.password}")
            return False
    return False

def print_user_details(user):
    """打印用户详细信息"""
    if user:
        print("\n用户详细信息:")
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"超级用户: {user.is_superuser}")
        print(f"工作人员: {user.is_staff}")
        print(f"激活状态: {user.is_active}")
        print(f"真实姓名: {user.real_name}")
        print(f"电子邮件: {user.email}")
        print(f"电话: {user.phone}")
        print(f"状态: {getattr(user, 'status', 'N/A')}")
        print(f"最后登录IP: {getattr(user, 'last_login_ip', 'N/A')}")
        print(f"最后登录时间: {user.last_login}")
        
        # 检查数据库中是否有position和avatar字段
        if hasattr(user, 'position'):
            print(f"职位: {user.position}")
        else:
            print("职位字段不存在")
            
        if hasattr(user, 'avatar'):
            print(f"头像: {user.avatar}")
        else:
            print("头像字段不存在")
        
        # 检查角色
        if user.role:
            print(f"角色: {user.role.name}")
        else:
            print("未分配角色")

def main():
    """主函数"""
    username = "admin"
    password = "Admin@2023"
    
    print("=== 登录测试 ===")
    user = test_user_exists(username)
    if user:
        test_password(user, password)
        print_user_details(user)
    
    print("\n=== 数据库用户列表 ===")
    users = User.objects.all()
    print(f"总用户数: {users.count()}")
    for i, u in enumerate(users):
        print(f"{i+1}. {u.username} (ID: {u.id}, 超级用户: {u.is_superuser})")

if __name__ == "__main__":
    main() 