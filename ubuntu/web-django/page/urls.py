from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('edit/<sensors_id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('temp/<int:id>', views.temp, name='temp'),
]