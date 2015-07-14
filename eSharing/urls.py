from django.conf.urls import patterns, include, url
from workNshare import views
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eSharing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^signup/$',views.register,name='registration page'),
    url(r'^login/$', views.login,name='login page'),
    url(r'^$', views.home_page,name='home or welcome page '),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^update_profile/$',views.update_profile,name='update profile'),
   url(r'^guess_users/$', views.guess_users,name='auto-complete user objects'),

url(r'^find/\?*$',views.find,name='find user'),
url(r'^profile/(?P<searched_username>\w+)/$',views.show_profile,name='show selected user profile'),
url(r'^shareit/$',views.share,name="sharing process"),
   url(r'^guess_friends/$', views.guess_friends,name='auto-complete friends'),
   url(r'^update_profile_picture/$',views.update_profile_picture,name='update profile picture'),
)
handler404 = views.error404
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
