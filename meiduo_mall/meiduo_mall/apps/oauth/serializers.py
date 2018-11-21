import re
from rest_framework import serializers
from django_redis import get_redis_connection

from .models import OAuthQQUser
from users.models import User
from .utils import check_save_user_token


class QQAuthUserSerializer(serializers.Serializer):
    """客户端提交的数据"""
    password = serializers.CharField(label="密码", write_only=True, min_length=8, max_length=20)
    mobile = serializers.CharField(label="手机号码", write_only=True)
    sms_code = serializers.CharField(label="验证码", write_only=True)
    access_token = serializers.CharField(label="openid", write_only=True)

    def validate_mobile(self, value):
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("手机格式不正确")

        return value

    def validate(self, attrs):
        """需要校验的数据　ama_code access_token"""

        # 通过手机号获取库中的验证码
        mobile = attrs["mobile"]
        redis_conn = get_redis_connection("verifications")  # 链接到redis
        real_sms_code = redis_conn.get("sms_%s" % mobile)  # bytes
        # 判断库中是否有没有
        if not real_sms_code:
            raise serializers.ValidationError("验证码无效")

        # 判断是否相等
        sms_code = attrs["sms_code"]
        if sms_code != real_sms_code.decode():
            raise serializers.ValidationError("验证码无效")

        access_token = attrs["access_token"]

        # 通过access_token获取openid
        openid = check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError("access_token无效")

        try:
            # 如果用户存在，校验密码是否匹配
            user = User.objects.get(mobile=mobile)
            if not user.check_password(attrs["password"]):
                raise serializers.ValidationError("密码不正确")
        except Exception:
            user = User()
            user.username = mobile
            user.mobile = mobile
            # user.password = attrs["password"]  保存的是明文密码
            user.set_password(attrs["password"])

            user.save()

        attrs["openid"] = openid
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        openid = validated_data["openid"]

        oauth_user = OAuthQQUser()
        oauth_user.user=user
        oauth_user.openid = openid
        oauth_user.save()

        return oauth_user