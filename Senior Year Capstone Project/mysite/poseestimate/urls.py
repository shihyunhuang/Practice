from .views import home, pose, videocutting, learning
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path, include
from django.views.static import serve

urlpatterns = [
    path('home/', home, name='home'),
    #path('youtube/', youtube, name='youtube'),
    #path('upload/', upload, name='upload'),
    path('pose/', pose, name='pose'),
    path('videocutting/', videocutting, name='videocutting'),
    path('learning/', learning, name='learning'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







