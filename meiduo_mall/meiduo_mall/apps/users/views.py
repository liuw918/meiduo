from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import User
from . import serializers
from celery_tasks.send_mails.tasks import send_email


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """用户名数量"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """手机号数量"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)


# 指明用户序列化器
# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer


class LoginApiView(APIView):
    # 用户登录
    def post(self, request):
        data = request.data
        username = data.get("username", "")
        password = data.get("password", "")

        users = User.objects.filter(Q(username=username) | Q(mobile=username))  # queryset对象，要么有一个，要么没有
        if users:
            # 用户存在
            user = users[0]

            if user.check_password(password):
                # 颁发token
                # 生成jwttoken
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                return Response({
                    'username': user.username,
                    "user_id": user.id,
                    "token": token
                })
        return Response({"message": "用户名或密码错误"}, status=400)


class UserDetailView(RetrieveAPIView):
    """用户详情视图"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserEmailView(UpdateAPIView):
    """保存用户邮箱"""
    serializer_class = serializers.UserEmailSerializer
    perssion_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# PUT /email/
# url(r'^email/$',UserEmailApi.as_view())
class UserEmailApi(UpdateAPIView):
    serializer_class = serializers.UserEmailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


# GET  emails/verification/?token=token
# url(r'^emails/verification/$',EmailVerifyApi.as_view())
class EmailVerifyApi(APIView):
    def get(self, request):
        # 获取token
        token = request.query_params.get('token', False)
        if not token:
            return Response({'message': "必须传递token"}, status=400)

        if User.token_extract(token):
            return Response({'message': 'OK'})

        return Response({'message': "token无效"}, status=400)
