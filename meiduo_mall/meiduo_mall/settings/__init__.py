from django.db.models.signals import post_delete, post_save


# 定义信号接收者
def static_list(sender, **kwargs):
    print(sender)
    print(kwargs)
    # 1.判断sender 是否是goodsCategory
    # 2.发送生成list静态的任务给celery
    if getattr(sender, '__name__', 'none') == "GoodsCategory":
        from celery_tasks.htmls.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()

post_save.connect(static_list)
post_delete.connect(static_list)
