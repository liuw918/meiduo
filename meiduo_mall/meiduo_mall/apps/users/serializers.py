import re

from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User, Address
from celery_tasks.send_mails.tasks import send_email


class CreateUserSerializer(serializers.ModelSerializer):
    """
    提交字段
    1. username
    2. password
    3. password2
    4. mobile
    5. sms_code
    6. allow
    返回字段
    1.id
    2. usrname
    3. moble
    4.jwt token
    """

    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="验证码", write_only=True)
    # ture
    allow = serializers.CharField(label="是否同意协议", write_only=True)
    token = serializers.CharField(label="token", read_only=True)  # 此处是JWT加密，增加token字段

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow', 'token']

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 32,
            },
            'username': {
                'min_length': 5,
                'max_length': 20,
            }

        }

    def validate_mobile(self, value):
        # 校验手机号码
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')
        return value

    def validate_allow(self, value):
        # 判断用户是否勾选同意协议
        if value != 'true':
            raise serializers.ValidationError('请同意协议')
        return value

    def validate_username(self, value):
        # 判断用户名是否存在
        if User.objects.filter(username=value):
            raise serializers.ValidationError('用户名已经存在')
        return value

    def validate(self, attrs):
        """校验密码"""
        password = attrs['password']
        password2 = attrs['password2']
        if password != password2:
            raise serializers.ValidationError('密码不匹配')

        mobile = attrs['mobile']
        redis_conn = get_redis_connection('verifications')  # 获取保存验证码的库

        real_sms_code = redis_conn.get('sms_%s' % mobile)  # bytes 类型
        if not real_sms_code:
            raise serializers.ValidationError('验证码无效')

        sms_code = attrs['sms_code']  # 客户端发来的验证码
        if sms_code != real_sms_code.decode():
            raise serializers.ValidationError('验证码无效')

        return attrs

    def create(self, validated_data):
        """创建用户"""

        del validated_data["password2"]
        del validated_data["sms_code"]
        del validated_data['allow']

        user = super().create(validated_data)

        user.set_password(validated_data['password'])  # 把加密后的密码保存
        user.save()

        # 补充生成记录登录状态的JWT token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""

    class Meta:
        model = User
        fields = ["id", "username", "mobile", "email", "email_active"]


# 更新邮箱序列化器
class UserEmailSerializer(serializers.Serializer):
    email = serializers.CharField(label='email', write_only=True)

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()

        token = instance.create_email_token()
        send_email.delay(instance.email, token)
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(label='省份名称', read_only=True)
    city = serializers.StringRelatedField(label='市区名称', read_only=True)
    district = serializers.StringRelatedField(label="县名称", read_only=True)

    province_id = serializers.IntegerField(label='省份id', write_only=True)
    city_id = serializers.IntegerField(label='城市id', write_only=True)
    district_id = serializers.IntegerField(label='县id', write_only=True)

    class Meta:
        model = Address
        exclude = ['user', 'is_deleted', 'create_time', 'update_time']

    # 数据校验
    #     title: '', 标题
    #     receiver: '', 收货人
    #     province_id: '', 省份id
    #     city_id: '', 市id
    #     district_id: '', 县id
    #     place: '', 地址
    #     mobile: '', 手机号码
    #     tel: '', 座机
    #     email: '', 邮箱

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')
        return value

    def create(self, validated_data):
        #     title: '', 标题
        #     receiver: '', 收货人
        #     province_id: '', 省份id
        #     city_id: '', 市id
        #     district_id: '', 县id
        #     place: '', 地址
        #     mobile: '', 手机号码
        #     tel: '', 座机
        #     email: '', 邮箱
        #     user:
        return Address.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # title: '', 标题
        # receiver: '', 收货人
        # province_id: '', 省份id
        # city_id: '', 市id
        # district_id: '', 县id
        # place: '', 地址
        # mobile: '', 手机号码
        # tel: '', 座机
        # email: '', 邮箱
        instance.title = validated_data.get('title', '')
        instance.receiver = validated_data.get('receiver', '')
        instance.province_id = validated_data.get('province_id', '')
        instance.city_id = validated_data.get('city_id', '')
        instance.district_id = validated_data.get('district_id', '')
        instance.place = validated_data.get('place', '')
        instance.mobile = validated_data.get('mobile', '')
        instance.tel = validated_data.get('tel', '')
        instance.email = validated_data.get('email', '')
        instance.save()

        return instance
