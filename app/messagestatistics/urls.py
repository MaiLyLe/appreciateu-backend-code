from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'messagestatistics'

router = DefaultRouter()
router.register(r'messagestatistics', views.MessageStatisticsView)


urlpatterns = [
    path('', include(router.urls)),
]
