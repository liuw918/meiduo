from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from .search_indexes import SKUIndex
from .models import SKU


class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'comments', 'default_image_url']


class SKUSearchSerializer(HaystackSerializer):
    class Meta:
        # 添加索引类
        index_classes = [SKUIndex]

        fields = [
            "text", 'price', 'id', 'comments', 'default_image_url'
        ]
