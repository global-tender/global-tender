from django.conf.urls import patterns, url, include
from django.http import StreamingHttpResponse

from tender import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^seminars/?$', views.seminars, name='seminars'),
	url(r'^seminars/(?P<arg>\d+)/?$', views.seminar_detail, name='seminar_detail'),

	url(r'^feedback/?$', views.feedback, name='feedback'),
	url(r'^contacts/?$', views.contacts, name='contacts'),
	url(r'^lektors/?$', views.lektors, name='lektors'),
	url(r'^services/?$', views.services, name='services'),

	url(r'^robots.txt$', views.robots, name='robots.txt'),
	url(r'^sitemap.xml$', views.sitemap_xml, name='sitemap.xml'),
	url(r'^humans.txt$', views.humans, name='humans.txt'),
)