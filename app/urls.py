from django.urls import path
from django.contrib.auth.views import LogoutView

from DjangoGramm import settings
from .views import *



app_name = 'app'

urlpatterns = [
    path('followers/', followers, name='followers'),
    path('following/', following, name='following'),
    path('subscribe/', subscribe, name='subscribe'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('registration/', signup, name='registration'),
    path('add_content/', add_content, name="add_content"),
    path('', view_content, name="view_content"),
    path('view_content/<str:content>', post, name="view_post"),
    path('view_profile/<str:username>/', view_profile, name="view_profile"),
    path('tag/', tag, name="tag"),
    path('view_tag/', view_tag, name="view_tag"),
    path('like/', like_content, name="like_content"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         activate, name='activate'),
    path('profile/create_user_profile', profile, name='create_user_profile'),
    ]
