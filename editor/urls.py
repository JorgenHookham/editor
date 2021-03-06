from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'editor.views.welcome', name='welcome'),
    url(r'^authorize/$', 'editor.views.authorize', name='authorize'),
    url(r'^authorize/callback/$', 'editor.views.authorize_callback', name='authorize_callback'),

    url(r'^home/(?P<key>\w+)/$', 'editor.views.authenticated_home', name='authenticated_home'),
    url(r'^home/(?P<key>\w+)/reports/pie/$', 'editor.views.pie_chart'),
    url(r'^home/(?P<key>\w+)/reports/line/$', 'editor.views.line_chart'),
    url(r'^home/(?P<key>\w+)/reports/counter/$', 'editor.views.report_counter'),

    url(r'^admin/', include(admin.site.urls)),
)
