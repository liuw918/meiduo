from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")

    email_active = models.BooleanField(default=False,verbose_name="用户邮箱")
    class Meta:
        db_table = "tb_user"
        verbose_name = "用户"

