from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'googlecontact'

router = DefaultRouter()
router.register(r'googlecontact', views.GoogleContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
