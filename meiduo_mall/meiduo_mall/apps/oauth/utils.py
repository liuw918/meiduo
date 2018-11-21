from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData
from django.conf import settings


def generate_save_user_token(openid):
    """
    生成保存用户数据的token
    :param openid: 用户的openid
    :return: token
    """
    # 构建加密工具
    serializer = Serializer(settings.SECRET_KEY, expires_in=300)
    # 构建数据
    data = {'openid': openid}
    # 数据加密,返回bytes
    token = serializer.dumps(data)
    # 把bytes转为字符串
    return token.decode()


def check_save_user_token(access_token):
    """
    检验保存用户数据的token
    :param token: token
    :return: openid or None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=300)
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        return data.get('openid')