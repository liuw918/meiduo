from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TS

from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
    """用户模型类"""
    #
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')
    email_active = models.BooleanField(default=False, verbose_name="用户邮箱")

    class Meta:
        db_table = "tb_user"
        verbose_name = "用户"

    # token生成
    # token解密

    # user.create_email_token(self)
    def create_email_token(self):
        data = {
            'user_id': self.id,
            'email': self.email
        }

        ts = TS(settings.SECRET_KEY, expires_in=60 * 60 * 2)

        token = ts.dumps(data).decode()
        return token

    @staticmethod
    def token_extract(token):
        ts = TS(settings.SECRET_KEY, expires_in=60 * 60 * 2)

        try:
            data = ts.loads(token)
        except Exception:
            return False

        user_id = data['user_id']
        email = data['email']

        try:
            user = User.objects.get(id=user_id, email=email)
        except Exception:
            return False

        user.email_active = True
        user.save()
        return True


class Address(BaseModel):
    """
    用户地址
    """
    # user.address_set.all()
    # user.addresses.all()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    # models.ForeignKey('areas.Areas')
    # 'areas.Areas' 子应用名称.模型类名字
    # province.address_set.all()
    # province.province_addresses.all()
    province = models.ForeignKey('areas.Areas', on_delete=models.PROTECT, related_name='province_addresses',
                                 verbose_name='省')
    # city.address_set.all()
    # city.city_addresses.all()
    city = models.ForeignKey('areas.Areas', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    # ds.address_set.all()
    # ds.district_addresses.all()
    district = models.ForeignKey('areas.Areas', on_delete=models.PROTECT, related_name='district_addresses',
                                 verbose_name='区')

    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
