from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import User, Address
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


class UserAddressApiView(GenericViewSet):
    permission_classes = (IsAuthenticated,)


    # 获取地址列表
    def list(self, request):
        # 获取当前用户
        user = self.request.user
        # 获取当前用户所有地址
        addresses = user.addresses.filter(is_deleted=False)
        # 序列化输出
        serializer = serializers.UserAddressSerializer(addresses, many=True)
        data = {
            'addresses': serializer.data,
            'limit': 15,
            'default_address_id': user.default_address.id if user.default_address else 0
        }
        return Response(data)


    # 新建
    def create(self, request):
        # 获取提交的数据
        # 构建序列化器对象
        # 校验数据
        # 保存对象
        # 序列化输出
        data = request.data
        serializer = serializers.UserAddressSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data)


    # 更新
    def update(self, request, pk):
        # 获取要更细的地址
        # 获取提交的数据
        # 构建序列化器
        # 校验数据
        # 保存
        # 序列化输出
        address = Address.objects.get(pk=pk)
        data = request.data
        serializer = serializers.UserAddressSerializer(instance=address, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    # 删除
    def destroy(self, request, pk):
        # 获取要删除的地址
        # 执行删除
        address = Address.objects.get(pk=pk)
        address.is_deleted = True
        address.save()

        return Response(status=204)


    # 默认地址
    @action(methods=['put'], detail=True)  # addresses/<pk>/status/
    def status(self, request, pk):
        # 获取地址
        # 把当前用户default_address改为获取的地址
        address = Address.objects.get(pk=pk)
        user = self.request.user
        user.default_address = address
        user.save()

        return Response({'message': 'OK'})


    # 更新标题
    @action(methods=['put'], detail=True)  # addresses/<pk>/title/
    def title(self, request, pk):
        # 获取地址
        # 获取title
        # 更新title
        # 序列化输出
        address = Address.objects.get(pk=pk)
        title = request.data.get('title', '')
        address.title = title
        address.save()
        return Response(serializers.UserAddressSerializer(address).data)
