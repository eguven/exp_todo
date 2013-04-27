from django.conf.urls import patterns, url


urlpatterns = patterns('todo_api.views',
   url(r'^(?P<pk>\d+)$', 'handle_rest_call', name='handle_rest_call_id'),
   url(r'^$', 'handle_rest_call', name='handle_rest_call'),
)
