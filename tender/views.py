# -*- coding: utf-8 -*-
import os
import re
import operator
import datetime

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, Http404

from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core import mail

from tender.models import FZs, Seminars, Seminar_Programs, Cities



@xframe_options_exempt
def index(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/index.html',
		'request': request,
		'title': '',
		'menu_color_class': 'menu-white',
		'menu_inner': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def seminars(request):

	seminars = Seminars.objects.filter(event_is_active=True).filter(event_date__gte=(timezone.now() + timezone.timedelta(days=-1))).order_by('event_date')

	seminars_all = {}

	for seminar in seminars:

		if seminar.event_fz.name in seminars_all:
			seminars_all[seminar.event_fz.name]['seminars'].append(seminar)
		else:
			seminars_all[seminar.event_fz.name] = {'seminars': [seminar], 'description': seminar.event_fz.description, 'sort': seminar.event_fz.sort}

	seminars_all_sorted = sorted(seminars_all.iteritems(), key=lambda (k, v): v['sort'], reverse=False)

	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/seminars.html',
		'request': request,
		'title': 'Расписание семинаров',
		'menu_color_class': 'menu-black',
		'menu_inner': 'menu-inner-seminars',

		'seminars': seminars_all_sorted,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

@xframe_options_exempt
def seminar_detail(request, arg):

	seminar = Seminars.objects.filter(id=arg)

	if seminar:
		seminar = seminar[0]

	status = 'active'
	if seminar.event_date <= (timezone.now() + timezone.timedelta(days=-1)):
		status = 'completed'
	if seminar.event_is_active == False:
		status = 'canceled'

	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/seminar.html',
		'request': request,
		'title': '%s %s.%s.%s - %s' % (seminar.event_city.name, seminar.event_date.day, seminar.event_date.month, seminar.event_date.year, seminar.event_fz.name),
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',

		'seminar': seminar,
		'seminar_program_template': "seminar_programs/" + seminar.event_program.program_short_name + ".html",
		'status': status,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

@xframe_options_exempt
@csrf_exempt
def ajax_seminar(request, arg):

	seminar = Seminars.objects.filter(id=arg)
	if seminar:
		seminar = seminar[0]

	submitted = False
	if request.method == 'POST':
		submitted = True

		form_contact_email = request.POST.get('contact-email', '')


		connection = mail.get_connection()
		connection.open()
		body = u"пусто, email: %s" % (form_contact_email)
		subject = u'Заявка "Глобал-Тендер": %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.day, seminar.event_date.month, seminar.event_date.year)
		email = mail.EmailMessage(subject, body, 'info@ihptru.net',
						  ['ihptru@yandex.ru'], headers = {'Reply-To': 'info@ihptru.net'}, connection=connection)
		email.send()
		connection.close()


	template = loader.get_template('ajax/seminar.html')
	template_args = {
		'request': request,
		'seminar': seminar,
		'submitted': submitted,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def feedback(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/feedback.html',
		'request': request,
		'title': 'Отзывы',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def contacts(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/contacts.html',
		'request': request,
		'title': 'Контактная информация',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

@xframe_options_exempt
def lektors(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/lektors.html',
		'request': request,
		'title': 'Наши лекторы',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

@xframe_options_exempt
def services(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/services.html',
		'request': request,
		'title': 'Сопровождение по 44-ФЗ и 223-ФЗ',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))





######################
### Service views
######################

def robots(request):
	template = loader.get_template('static/robots.txt')
	template_args = {
		'request': request,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context), content_type='text/plain')

def humans(request):
	template = loader.get_template('static/humans.txt')
	template_args = {
		'request': request,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context), content_type='text/plain')

def sitemap_xml(request):
	template = loader.get_template('static/sitemap.xml')
	template_args = {
		'request': request,
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context), content_type='text/xml')

def sitemap_html(request):
	pass

def handle404(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'static/404.html',
		'request': request,
		'title': 'Страница не найдена',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	context = RequestContext(request, template_args)
	return HttpResponseNotFound(template.render(context))