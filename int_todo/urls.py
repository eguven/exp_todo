
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    # Admin interface setup
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Delivery of the static client
    url(r'^$', login_required(direct_to_template),
        {'template': 'todo_client/index.html'}, name='client'),
    # built-in django login/logout
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),

    # REST API endpoints
    url(r'^rest/todo/', include('todo_api_piston.urls')),
    url(r'^rest-empty/todo/', include('todo_api.urls', namespace='todo_api')),
)
