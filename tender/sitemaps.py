from django.utils import timezone

from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from tender.models import Seminars

class SeminarsViewSitemap(sitemaps.Sitemap):
	priority = 0.5
	changefreq = 'daily'

	def items(self):
		return Seminars.objects.filter(event_is_active=True).filter(event_date__gte=(timezone.now() + timezone.timedelta(days=-1))).order_by('event_date')


class StaticViewSitemap(sitemaps.Sitemap):
	priority = 0.5
	changefreq = 'daily'

	def items(self):
		return ['index', 'seminars', 'feedback', 'contacts']

	def location(self, item):
		if item == 'index':
			return '/'
		else:
			return '/' + item + '/'