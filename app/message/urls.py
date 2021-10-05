from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'message'

router = DefaultRouter()
router.register(r'messages', views.CreateListMessageView)


urlpatterns = [
    path('', include(router.urls)),
]
