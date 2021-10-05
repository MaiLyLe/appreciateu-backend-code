from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'useradministration'

router = routers.SimpleRouter()
router.register(r'register', views.CreateUserWithRoleAndAddCoursesView,
                basename='register')

urlpatterns = [
    path('list-institute/', views.InstituteListView.as_view({'get': 'list'}), name='list_institutes'),
    path('list-fields/', views.FieldOfStudiesListView.as_view({'get': 'list'}), name='list_fields'),
    path('list-courses/', views.CoursesListView.as_view({'get': 'list'}), name='list_courses'),
    path('list-fields-by-institute/',
         views.FieldOfStudiesListViewFiltered.as_view({'get': 'list'}),
         name='list_fields_by_institute'),
    path('', include(router.urls)),
]