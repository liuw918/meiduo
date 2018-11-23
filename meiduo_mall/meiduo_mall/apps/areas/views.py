from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from . import serializers
from .models import Areas

from rest_framework_extensions.cache.decorators import cache_response

# Create your views here.

# 获取省份列表
# url(r'^areas/$',AreasApiView.as_view({'get':'list'}))

# 获取下一级地区列表
# url(r'^areas/(?P<pk>\d+)/$',AreasApiView.as_view({'get':'retrieve'}))

class AreasApiView(ViewSet):
    @cache_response(timeout=60, cache='default')
    def list(self, request):
        # 获取所有省份
        # 序列化输出
        provinces = Areas.objects.filter(parent=None)
        pses = serializers.AreasSerializer(provinces, many=True)
        return Response(pses.data)

    # 获取下一级地区列表
    # url(r'^areas/(?P<pk>\d+)/$',AreasApiView.as_view({'get':'retrieve'}))
    @cache_response(timeout=60, cache='default')
    def retieve(self, request, pk):
        # 获取当前地区对象
        areas_obj = Areas.objects.get(pk=pk)
        # 序列化输出
        serializer = serializers.AreasSubsSerializer(areas_obj)

        return Response(serializer.data)
