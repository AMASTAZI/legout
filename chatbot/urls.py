from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.assistant_page, name='assistant'),
    path('api/message/', views.chat_api, name='api_message'),
]
