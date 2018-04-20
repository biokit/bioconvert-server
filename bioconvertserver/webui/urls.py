# Create your views here.
from django.conf.urls import url

from webui import views

app_name = 'webui'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^job/(?P<identifier>[0-9A-Za-z]{32,32})/$', views.BioConvertJobDetailView.as_view(), name='results'),
    url(r'^(?P<in_fmt>\w+)/(?P<out_fmt>\w+)/$', views.convert, name='bioconvert'),
]
