from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.mystery_list, name='mystery_list'),
    path('<int:pk>/', views.mystery_detail, name='mystery_detail'),
    path('<int:pk>/add_review/', views.add_review, name='add_review'),
]
