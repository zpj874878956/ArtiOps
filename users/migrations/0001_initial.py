# Generated by Django 4.2 on 2025-07-04 03:25

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('admin', '管理员'), ('operator', '运维员'), ('readonly', '只读用户')], default='readonly', max_length=20, verbose_name='用户类型')),
                ('phone', models.CharField(blank=True, max_length=11, null=True, verbose_name='手机号')),
                ('department', models.CharField(blank=True, max_length=50, null=True, verbose_name='部门')),
                ('position', models.CharField(blank=True, max_length=50, null=True, verbose_name='职位')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='头像')),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='最后登录IP')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'ordering': ['-date_joined'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserLoginLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(auto_now_add=True, verbose_name='登录时间')),
                ('login_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='登录IP')),
                ('login_type', models.CharField(default='web', max_length=20, verbose_name='登录类型')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('is_success', models.BooleanField(default=True, verbose_name='是否成功')),
                ('fail_reason', models.CharField(blank=True, max_length=100, null=True, verbose_name='失败原因')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_logs', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '登录日志',
                'verbose_name_plural': '登录日志',
                'ordering': ['-login_time'],
            },
        ),
    ]
