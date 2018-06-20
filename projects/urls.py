from django.urls import path

from . import views

app_name='projects'

urlpatterns = [
    path('<int:graph_ID>/', views.projects, name='projects'),
]