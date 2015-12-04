from django.conf.urls import patterns, url, include
from django.http import StreamingHttpResponse

from tender import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^seminars/?$', views.seminars, name='seminars'),
	#url(r'^seminars/?$', views.seminars, name='seminars'),

	url(r'^reviews/?$', views.reviews, name='reviews'),
	url(r'^contacts/?$', views.contacts, name='contacts'),

	url(r'^robots.txt$', lambda r: StreamingHttpResponse("User-agent: *\nDisallow: ", content_type="text/plain")),
)