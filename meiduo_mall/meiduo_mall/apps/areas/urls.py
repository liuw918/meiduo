from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = [
#     url(r'^areas/$', views.AreasApiView.as_view({'get': 'list'})),
#     url(r'^areas/(?P<pk>\d+)/$', views.AreasApiView.as_view({'get': 'retieve'}))
]

router = SimpleRouter()
router.register('areas', views.AreasApiView, base_name='areas')

urlpatterns += router.urls
