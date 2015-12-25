from django.conf.urls import patterns, url, include
from django.http import StreamingHttpResponse

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, SeminarsViewSitemap

from tender import views

sitemaps = {
	'static': StaticViewSitemap,
	'seminars': SeminarsViewSitemap,
}

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^seminars/?$', views.seminars, name='seminars'),
	url(r'^seminars/(?P<arg>\d+)/?$', views.seminar_detail, name='seminar_detail'),
	url(r'^seminars/(?P<arg>\d+)/print/?$', views.seminar_detail_print, name='seminar_detail_print'),

	url(r'^feedback/?$', views.feedback, name='feedback'),
	url(r'^contacts/?$', views.contacts, name='contacts'),
	url(r'^lektors/?$', views.lektors, name='lektors'),
	url(r'^services/?$', views.services, name='services'),

	url(r'^robots.txt$', views.robots, name='robots.txt'),
	url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	url(r'^humans.txt$', views.humans, name='humans.txt'),

	url(r'^ajax/seminar/(?P<arg>\d+)/?$', views.ajax_seminar, name='ajax_seminar'),

	url(r'^.*$', views.handle404, name='handle404'),
)