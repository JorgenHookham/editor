from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^authorize/$', 'editor.views.authorize', name='authorize'),
    url(r'^authorize/callback/$', 'editor.views.authorize_callback', name='authorize_callback'),
    url(r'^$', 'editor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
