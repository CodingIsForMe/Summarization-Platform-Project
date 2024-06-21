from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('howitworks', views.howitworks, name='howitworks'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='signup'),
    path('', views.base, name='base'),
    path('', views.main, name='main'),
    path('UPLOAD', views.upload_document, name='upload_document'),
    path('summary', views.summarization, name='summary'),
    path('question', views.question, name='question'),
    path('answer_generation', views.answer_generation, name='answer_generation'),
    path('logout', views.logout_view, name='logout'),
    path('home', views.home, name='home'),
    
]