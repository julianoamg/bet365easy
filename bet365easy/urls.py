from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings

from core import views

admin_path = 'admin' if settings.DEBUG else '09a88272-a76a-471a-a18e-f10894e62896'

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('', views.IndexView.as_view(), name='index'),
    path('tip/<identifier>/', views.TipView.as_view(), name='tip'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('is-authenticated/', views.IsAuthenticatedView.as_view(), name='is-authenticated'),
    path('send-tip/', views.SendTipView.as_view(), name='send-tip'),
    path(admin_path, admin.site.urls)
]
