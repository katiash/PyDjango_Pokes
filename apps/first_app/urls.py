from django.conf.urls import url
##from django.contrib import admin
from . import views

urlpatterns = [
  url(r'^$', views.main, name='main'),
  url(r'^pokes$', views.pokes, name='pokes'),
  url(r'^register$', views.register, name='register'),
  url(r'^login$', views.login, name='login'),
  url(r'^logout$', views.logout, name='logout'),
  url(r'^poke/(?P<id>\d+)$', views.poke, name='poke'),
]