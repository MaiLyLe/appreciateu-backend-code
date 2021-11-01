# urls for google_contact app
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'google_contact'

router = DefaultRouter()
router.register(r'googlecontact', views.GoogleContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
