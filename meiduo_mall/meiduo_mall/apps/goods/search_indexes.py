from haystack import indexes

from goods.models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    text = indexes.CharField(document=True, model_attr='name')
    # text = indexes.CharField(document=True, use_template=True)
    price = indexes.DecimalField(model_attr='price')
    id = indexes.IntegerField(model_attr='id')
    comments = indexes.IntegerField(model_attr='comments')
    default_image_url = indexes.CharField(model_attr='default_image_url')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
