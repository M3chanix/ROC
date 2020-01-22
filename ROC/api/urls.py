from django.urls import path

from . import views

urlpatterns = [
    path('test', views.filter_entries),
    path('normalize', views.normalize),
    path('append', views.class_and_append)
]

