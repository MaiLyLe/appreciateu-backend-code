from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
from . import views

app_name = 'user'

router = routers.SimpleRouter()
router.register(r'professors', views.ProfessorView, basename='professors')
router.register(r'students', views.StudentView, basename="students")


urlpatterns = [
    path('generalusers/', views.UserRetrieveView.as_view({'get': 'list'}), name='get'),
    path('verifyaccess/', views.VerifyAccessView.as_view(), name='verify_access'),
    path('currentuser/', views.CurrentUserView.as_view(), name='current_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    ]
