import random

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        """
        # 1.校验短信是否发送过
        # 2.如果发送，返回已经发送的信息
        # 3.生成随机验证码
        # 4.保存验证码到redis中  sms_{mobile}
        # 5.保存已经发送的状态  smsflag{mobile}
        # 6.给用户发送短信
        # 7.返回客户端发送成功

        :param request:
        :param mobile:
        :return:
        """
        redis_conn = get_redis_connection("verifications")  # 链接到redis数据库中

        send_flag = redis_conn.get("smsflag_%s" % mobile)  # 获取短信发送状态
        # 短信已经发送过
        if send_flag:
            return Response({"message": "短信发送频繁"},status=400)
        # 没有发送，需要生成
        sms_code = random.randint(10000, 99999)

        # redis_conn.sex(key,exprie,value)
        # # 保存验证码
        # redis_conn.setex("sms_%s" % mobile, 5 * 60, sms_code)
        # # 保存发送状态
        # redis_conn.setex('smsflag_%s' % mobile, 60, 1)

        # 获取管道对象（代替上面的代码）
        pipeline = redis_conn.pipeline()
        # 往管道中添加命令
        pipeline.setex("sms_%s" % mobile, 5 * 60, sms_code)
        pipeline.setex('smsflag_%s' % mobile, 60, 1)

        # 执行管道中的所有命令
        pipeline.execute()

        # 发送短信给手机
        # 发布任务，立即返回
        send_sms_code.delay(mobile, sms_code, 5)

        print(send_sms_code)
        # 发送短信给手机
        return Response({'message': 'OK',"消息为 ": sms_code})


