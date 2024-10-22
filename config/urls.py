from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from environs import Env


env = Env()
env.read_env()
DEBUG = env.bool("DJANGO_DEBUG", default=False)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('equipment.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if DEBUG == True:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]