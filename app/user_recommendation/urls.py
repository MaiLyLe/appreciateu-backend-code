# urls for user_recommendation app
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'user_recommendation'

router = routers.SimpleRouter()
router.register(r'professors', views.ProfessorRecommendationsView, basename='professors')
router.register(r'students', views.StudentRecommendationsView, basename="students")


urlpatterns = [
    path('generalusers/', views.UserRetrieveView.as_view({'get': 'list'}), name='get'),
    path('', include(router.urls)),
    ]
