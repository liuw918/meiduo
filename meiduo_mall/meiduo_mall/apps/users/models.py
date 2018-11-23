from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TS


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")

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
