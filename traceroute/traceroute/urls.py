from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('partners/', views.PartnerListView.as_view(), name='partners'),
    # TODO: Add locations/ as locations/all.
    re_path(r'^locations/(?P<partner>[\w ]+)/$', views.LocationListView.as_view(), name='filtered_locations'),
    # TODO: Add targets/ as targets/all/all/.
    re_path(r'^targets/(?P<partner>[\w ]+)/(?P<location>[\w ]+)/$', views.TargetListView.as_view(), name='filtered_targets'),
    re_path(r'^graph/(?P<target>.+)/(?P<path>\w+)/$', views.graph_view, name='graph_view'),
]

