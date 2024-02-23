"""
URL configuration for aerc_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('home', views.home, name='home'),
    path('vehicle', views.vehicle, name='vehicle'),
    path('house', views.house, name='house'),
    path('crypto', views.crypto, name='crypto'),
    path('stock', views.stock, name='stock'),
    path('user', views.user, name='user'),
    path('asset', views.asset, name='asset'),
    re_path(r'^stock_search/(?P<stock_ticker>[^/]+)/$', views.stock_search, name='stock-search'),
]