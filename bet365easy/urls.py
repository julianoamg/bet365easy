from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('is-authenticated/', views.IsAuthenticatedView.as_view(), name='is-authenticated'),
    path('send-tip/', views.SendTipView.as_view(), name='send-tip'),
    path('09a88272-a76a-471a-a18e-f10894e62896', admin.site.urls),
]
Preciso desenvolver um sistema de gestão escolar que contemple registro de faltas + relatórios e notificações por e-mail e cadastro de matérias + professores.
