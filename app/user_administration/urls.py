# urls for user_administration class
from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'user_administration'

router = routers.SimpleRouter()
router.register(r'register', views.CreateUserWithRoleAndAddCoursesView,
                basename='register')
router.register(r'update', views.UpdateUserWithRoleAndAddCoursesView,
                basename='update')
router.register(r'profilestudent', views.StudentWithCoursesView, basename='student')
router.register(r'profileprof', views.ProfessorWithCoursesView, basename='professor')

urlpatterns = [
    path('list-institute/', views.InstituteListView.as_view({'get': 'list'}),
         name='list_institutes'),
    path('list-fields/', views.FieldOfStudiesListView.as_view({'get': 'list'}), name='list_fields'),
    path('list-courses/', views.CoursesListView.as_view({'get': 'list'}), name='list_courses'),
    path('list-fields-by-institute/',
         views.FieldOfStudiesListViewFiltered.as_view({'get': 'list'}),
         name='list_fields_by_institute'),
    path('', include(router.urls)),
]
