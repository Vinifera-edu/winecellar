from django.urls import path
from . import views
from .views import create_admin

from django.conf import settings
from django.conf.urls.static import static

# App Namespace
app_name = 'wine'

urlpatterns = [
    path('', views.index),
    path('wine/', views.WinesView.as_view(), name='wine_list'),
    path('wine/delete/<int:pk>', views.DeleteView.as_view(), name='wine_delete'),
    path('wine/new/', views.createWine, name='create_wine'),
    path('wine/edit/<int:pk>', views.updateWine, name='update_wine'),
    path('wine/copy/<int:pk>', views.copyWine, name='copy_wine'),
    path('about/', views.about),
    path('info/', views.info),
    path('wine/export/', views.export_csv),
    path('wine/export_xls/', views.export_xls),
    path('wine/full/', views.FullView.as_view(), name='wine_fullview'),
    path('wine/log/', views.WineLog.as_view(), name='wine_log'),
    path('wine/detail/<int:pk>', views.WineLogDetail, name='wine_log_detail'),
    path('create-admin/', create_admin),
    path('wine/analyze/', views.analyze_wine_image, name='analyze_wine_image'),
]

# Obsługa mediów w trybie DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
