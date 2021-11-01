# urls for message_statistics app
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'message_statistics'

router = DefaultRouter()
router.register(r'messagestatistics', views.MessageStatisticsView, basename='statistics')


urlpatterns = [
    path('', include(router.urls)),
]
