from django.urls import path

from . import views

app_name='forms'

urlpatterns = [
    path('edit_task_group/<int:task_ID>/', views.edit_task_group, name='edit_task_group'),
    path('edit_task_details/<int:task_ID>/', views.edit_task_details, name='edit_task_details'),
    path('remove_task/<int:task_ID>/', views.remove_task, name='remove_task'),
    path('create_project/', views.create_project, name='create_project'),
    path('edit_project/<int:graph_ID>', views.edit_project, name='edit_project'),
    path('remove_project/<int:graph_ID>', views.remove_project, name='remove_project'),
]