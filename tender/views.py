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

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
		'title': '%s %s.%s.%s - %s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year, seminar.event_fz.name),
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
	send_copy_email = ''

	seminar = Seminars.objects.filter(id=arg)
	if seminar:
		seminar = seminar[0]

	submitted = False
	if request.method == 'POST':
		submitted = True

		############################################################
		send_copy_email = request.POST.get('send-copy-email', '')
		if send_copy_email == "yes":
			send_copy_email_to = unicode(request.POST.get('contact-email',''))
			try:
				validate_email(send_copy_email_to)
			except ValidationError as e:
				send_copy_email = ''


		form_uri = request.POST.get('uri', '')
		if ( form_uri != '' ):
			form_uri = u" - совпадает с юридическим "

		form_act = request.POST.get('act', '')
		form_act_type = ''
		if ( form_act != '' ):
			if ( form_act == 'ustav' ):
				form_act_type = u" устава "
			if ( form_act == 'polozhenie' ):
				form_act_type = u" положения "

		form_pol = request.POST.get('act', '')
		if ( form_pol != '' ):
			form_pol = " положения "

		body_head = u"Семинар: %s  %s.%s.%s\n\n" % (unicode(seminar.event_city.name), seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
		body = u"""
		1. Организация: %s \n
			Название организации (краткое): %s \n
			ИНН: %s \n
			КПП: %s \n\n
			Почтовый адрес: %s, %s, %s, %s, %s  %s \n\n
		2. Руководитель (для оформления договора): %s \n
			Должность: %s \n
			Руководитель действует на основании: %s \n
		3. Количество участников семинара: %s \n
		4. Контактные лицо: %s \n
			Должность: %s \n
			email: %s \n
			Телефон: %s \n
		5. Комментарий: %s \n
		""" % (unicode(request.POST.get('org-name','')),
				unicode(request.POST.get('org-short','')),
				unicode(request.POST.get('inn','')),
				unicode(request.POST.get('kpp','')),
				unicode(request.POST.get('zip-code','')),
				unicode(request.POST.get('region','')),
				unicode(request.POST.get('city','')),
				unicode(request.POST.get('street','')),
				unicode(request.POST.get('home','')),
				unicode(form_uri),
				unicode(request.POST.get('fio','')),
				unicode(request.POST.get('post','')),
				unicode(form_act_type),
				unicode(request.POST.get('amount','')),
				unicode(request.POST.get('contact-name','')),
				unicode(request.POST.get('contact-post','')),
				unicode(request.POST.get('contact-email','')),
				unicode(request.POST.get('contact-phone','')),
				unicode(request.POST['comment'])
		)
		############################################################
		
		subject = u'Заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)


		connection = mail.get_connection()
		connection.open()
		
		email = mail.EmailMessage(subject, body_head + body, settings.ADMIN_EMAIL_FROM,
			settings.ADMIN_EMAIL_TO, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)

		email.send()


		if send_copy_email == "yes":
			subject = u'Вами отправлена заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
			body = u'Заявка на семинар отправлена, ожидайте обработки.\n\nСодержимое заявки:\n\n' + body

			email = mail.EmailMessage(subject, body_head + body, settings.ADMIN_EMAIL_FROM,
				[send_copy_email_to], headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)

			email.send()


		connection.close()


	template = loader.get_template('ajax/seminar.html')
	template_args = {
		'request': request,
		'seminar': seminar,
		'submitted': submitted,
		'send_copy_email': send_copy_email,
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