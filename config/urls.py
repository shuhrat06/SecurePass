from django.contrib import admin
from django.urls import path, include
from main.views import *
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

urlpatterns = [
    path('kjeshfkajh4aajfalajsdfjkj1546asf41dfs/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('users.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )