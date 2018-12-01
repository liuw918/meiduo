import json

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView


class UserCartView(APIView):
    def perform_authentication(self, request):
        pass

    def post(self, request):
        # 获取数据
        data = request.data
        sku_id = data['sku_id']
        count = data['count']
        selected = data.get('selected', False)

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 异常说明用户未登录
            user = None
        if user is not None and user.is_authenticated:
            # 操作redis
            conn = get_redis_connection('cart')
            cart_id = 'cart_%d' % user.id
            cart_selected_id = 'cart_selected_%d' % user.id
            pipeline = conn.pipeine()
            # 修改商品数量
            pipeline.hincrby(cart_id, sku_id, count)

            if selected:
                # 添加选中状态
                pipeline.sadd(cart_selected_id, sku_id)
            else:
                # 　移除选中状态
                pipeline.srem(cart_selected_id, sku_id)
            pipeline.execute()
            return Response(data, status=201)
        else:
            # 操作cookie
            cart_cookie = request.COOKIES.get('cart', None)
        if cart_cookie:
            cart = json.loads(cart_cookie)
        else:
            cart = {}

        # 修改购物车数量
        if sku_id in cart:
            cart[sku_id]['count'] += count
        else:
            cart[sku_id] = {
                'count': count
            }

        # 修改是否选中
        if selected:
            cart[sku_id]['selected'] = True
        else:
            cart[sku_id]['selected'] = False

        response = Response(data, status=201)
        response.set_cookie('cart', json.dumps(cart), max_age=60 * 60 * 24 * 365)

        return response
