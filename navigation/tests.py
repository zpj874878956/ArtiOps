from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import SystemCategory, ExternalSystem, UserFavorite

User = get_user_model()


class SystemCategoryModelTest(TestCase):
    """
    系统分类模型测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
    
    def test_category_creation(self):
        """
        测试分类创建
        """
        self.assertEqual(self.category.name, '测试分类')
        self.assertEqual(self.category.description, '测试分类描述')
        self.assertEqual(self.category.order, 1)
        self.assertEqual(self.category.created_by, self.user)
        self.assertTrue(self.category.is_active)


class ExternalSystemModelTest(TestCase):
    """
    外部系统模型测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
        self.system = ExternalSystem.objects.create(
            name='测试系统',
            system_type='monitoring',
            category=self.category,
            description='测试系统描述',
            base_url='https://example.com',
            api_base_url='https://api.example.com',
            order=1,
            created_by=self.user
        )
    
    def test_system_creation(self):
        """
        测试系统创建
        """
        self.assertEqual(self.system.name, '测试系统')
        self.assertEqual(self.system.system_type, 'monitoring')
        self.assertEqual(self.system.category, self.category)
        self.assertEqual(self.system.description, '测试系统描述')
        self.assertEqual(self.system.base_url, 'https://example.com')
        self.assertEqual(self.system.api_base_url, 'https://api.example.com')
        self.assertEqual(self.system.order, 1)
        self.assertEqual(self.system.created_by, self.user)
        self.assertTrue(self.system.is_active)
        self.assertEqual(self.system.access_count, 0)
        self.assertEqual(self.system.score, 0)
    
    def test_calculate_score(self):
        """
        测试评分计算
        """
        # 初始评分为0
        self.assertEqual(self.system.score, 0)
        
        # 增加访问次数
        self.system.access_count = 10
        self.system.calculate_score()
        self.system.save()
        
        # 评分应该大于0
        self.assertGreater(self.system.score, 0)


class UserFavoriteModelTest(TestCase):
    """
    用户收藏模型测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
        self.system = ExternalSystem.objects.create(
            name='测试系统',
            system_type='monitoring',
            category=self.category,
            description='测试系统描述',
            base_url='https://example.com',
            api_base_url='https://api.example.com',
            order=1,
            created_by=self.user
        )
        self.favorite = UserFavorite.objects.create(
            user=self.user,
            system=self.system
        )
    
    def test_favorite_creation(self):
        """
        测试收藏创建
        """
        self.assertEqual(self.favorite.user, self.user)
        self.assertEqual(self.favorite.system, self.system)


class SystemCategoryAPITest(APITestCase):
    """
    系统分类API测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
        self.url = reverse('system-category-list')
    
    def test_list_categories(self):
        """
        测试获取分类列表
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_category(self):
        """
        测试创建分类
        """
        data = {
            'name': '新分类',
            'description': '新分类描述',
            'order': 2
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SystemCategory.objects.count(), 2)


class ExternalSystemAPITest(APITestCase):
    """
    外部系统API测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
        self.system = ExternalSystem.objects.create(
            name='测试系统',
            system_type='monitoring',
            category=self.category,
            description='测试系统描述',
            base_url='https://example.com',
            api_base_url='https://api.example.com',
            order=1,
            created_by=self.user
        )
        self.url = reverse('external-system-list')
    
    def test_list_systems(self):
        """
        测试获取系统列表
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_system(self):
        """
        测试创建系统
        """
        data = {
            'name': '新系统',
            'system_type': 'deployment',
            'category': self.category.id,
            'description': '新系统描述',
            'base_url': 'https://new.example.com',
            'api_base_url': 'https://api.new.example.com',
            'order': 2
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExternalSystem.objects.count(), 2)
    
    def test_record_access(self):
        """
        测试记录访问
        """
        url = reverse('external-system-record-access', args=[self.system.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 重新获取系统实例
        self.system.refresh_from_db()
        self.assertEqual(self.system.access_count, 1)


class UserFavoriteAPITest(APITestCase):
    """
    用户收藏API测试
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.category = SystemCategory.objects.create(
            name='测试分类',
            description='测试分类描述',
            order=1,
            created_by=self.user
        )
        self.system = ExternalSystem.objects.create(
            name='测试系统',
            system_type='monitoring',
            category=self.category,
            description='测试系统描述',
            base_url='https://example.com',
            api_base_url='https://api.example.com',
            order=1,
            created_by=self.user
        )
        self.url = reverse('user-favorite-list')
    
    def test_create_favorite(self):
        """
        测试创建收藏
        """
        data = {
            'system': self.system.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserFavorite.objects.count(), 1)
    
    def test_my_favorites(self):
        """
        测试获取我的收藏
        """
        # 创建收藏
        UserFavorite.objects.create(
            user=self.user,
            system=self.system
        )
        
        url = reverse('user-favorite-my-favorites')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
