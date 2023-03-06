from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('is-authenticated/', views.IsAuthenticatedView.as_view(), name='is-authenticated'),
    path('send-tip/', views.SendTipView.as_view(), name='send-tip'),
    path('admin', admin.site.urls),
]
