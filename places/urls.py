from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('map/', views.map, name='map'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('send-message/', views.send_message, name='send_message'),
    path('success/', views.success, name='success'),
    #path('places/comment/add/', views.add_comment, name='add_comment'),
    path('like_dislike/toggle/', views.toggle_like_dislike, name='toggle_like_dislike'),
    #path('places/comment/latest/', views.latest_comments, name='latest_comments'),

]