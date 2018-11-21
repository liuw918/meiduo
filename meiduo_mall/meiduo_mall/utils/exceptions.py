import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from django.db import DatabaseError
from redis.exceptions import RedisError

logger = logging.getLogger("django")


def exception_handler(exc, context):
    # 1.drf 处理异常
    # 2. 自己处理异常
    """
    :param exc: 异常的对象
    :param context: 异常的内容
    :return:
    """
    response = drf_exception_handler(exc, context)

    # 判断是否已经处理完成
    if not response:
        # 手动处理
        logging.error("[%s] %s" % (context['view'], exc))
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            return Response({'error': "服务器内部异常"}, status=507)
    return response
