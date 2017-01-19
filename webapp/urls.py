from django.conf.urls import url, patterns, include
from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^startthread/$', views.add_post, name='startthread'),
    url(r'^thread/(?P<slug>[-\w]+)/$', views.view_post, name='blog_post_detail'),
    url(r'^thread/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^thread/(?P<pk>\d+)/delete/$', views.delete_new, name='delete_new'),
    url(r'^response/(?P<pk>\d+)/delete/$', views.delete_response, name='delete_response'),
    url(r'^response/(?P<pk>\d+)/edit/$', views.response_edit, name='response_edit'),
    url(r'^userprofile/(?P<author>[\w|\W]+)/$', views.userprofile, name='userprofile'),
    url(r'^yourfeed/$', views.your_post, name='your_post'),
    url(r'^tinymce/', include('tinymce.urls')),
]