from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import app
from itsdangerous import TimedJSONWebSignatureSerializer as TS


@app.task(name="send_email")
def send_email(email, token):
    """
    发送验证邮件
    :param email: 　收件人邮箱
    :param token: 　验证链接
    :return: 　None
    """
    subject = '美多商城邮箱验证'
    message = ''
    from_email = settings.EMAIL_FROM
    recipient_list = [email]
    html_message = '''
       尊敬的用户您好！</br>

       感谢您使用美多商城。</br>

       您的邮箱为：%s 。请点击此链接激活您的邮箱：</br>

       <a href='http://www.meiduo.site:8080/success_verify_email.html?token=%s'>http://www.meiduo.site:8080/success_verify_email.html?token=%s</a>

       ''' % (email, token, token)
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
