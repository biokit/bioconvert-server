from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^api/', include('bioconvertapi.urls')),
    url(r'^', include('webui.urls')),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
