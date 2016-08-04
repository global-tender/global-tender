import urllib
from django import template

register = template.Library()

def rus_month(value):
	months = {
		1: 'января',
		2: 'февраля',
		3: 'марта',
		4: 'апреля',
		5: 'мая',
		6: 'июня',
		7: 'июля',
		8: 'августа',
		9: 'сентября',
		10: 'октября',
		11: 'ноября',
		12: 'декабря',
	}
	return months[value]
register.filter('rus_month', rus_month)

def year_short(value):
	return str(value)[2:]
register.filter('year_short', year_short)

def unescape(value):
	return urllib.unquote(value)
register.filter('unescape', unescape)