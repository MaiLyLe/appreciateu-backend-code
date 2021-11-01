# global url config file, one url usually maps to an app
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('message/', include('message.urls', namespace='message')),
    path('googlecontact/', include('google_contact.urls', namespace='google_contact')),
    path('messagestatistics/', include('message_statistics.urls', namespace='message_statistics')),
    path('useradministration/', include('user_administration.urls',
         namespace='user_administration')),
    path('userrecommendation/', include('user_recommendation.urls',
         namespace='user_recommendation')),
    path('authentication/', include('token_authentication.urls',
         namespace='token_authentication'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
