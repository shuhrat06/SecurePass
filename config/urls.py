from django.contrib import admin
from django.urls import path, include
from main.views import *
from django.conf import settings
from django.conf.urls.static import static
from main.views import *
from django.urls import re_path

urlpatterns = [
    path('kjeshfkajh4aajfalajsdfjkj1546asf41dfs/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('users.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        }),
    ]