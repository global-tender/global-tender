# -*- coding: utf-8 -*-
import os
import re
import operator
import datetime

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.http import HttpResponseRedirect, Http404
from django.template import loader

from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.html import strip_tags
from django.core import mail

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from tender.models import FZs, Seminars, Seminar_Programs, Cities, Banners



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
	return StreamingHttpResponse(template.render(template_args, request))


@xframe_options_exempt
def seminars(request):

	if 'seminars_completed' not in request.path:
		seminars = Seminars.objects.filter(event_is_active=True).filter(event_date__gte=(timezone.now() + timezone.timedelta(days=-1))).order_by('event_date')
		page_title = u'Расписание семинаров'
	else:
		seminars = Seminars.objects.filter(event_is_active=True).filter(event_date__lt=(timezone.now() + timezone.timedelta(days=-1))).order_by('-event_date')
		page_title = u'Список недавно проведенных семинаров'

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
		'title': page_title,
		'menu_color_class': 'menu-black',
		'menu_inner': 'menu-inner-seminars',

		'seminars': seminars_all_sorted,
	}
	return StreamingHttpResponse(template.render(template_args, request))


@xframe_options_exempt
def seminar_detail(request, arg):

	seminar = Seminars.objects.filter(id=arg)

	if seminar:
		seminar = seminar[0]
	else:
		return HttpResponseRedirect('/seminars/')

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
	return StreamingHttpResponse(template.render(template_args, request))


@xframe_options_exempt
def seminar_detail_print(request, arg):

	seminar = Seminars.objects.filter(id=arg)

	if seminar:
		seminar = seminar[0]
	else:
		return HttpResponseRedirect('/seminars/')

	status = 'active'
	if seminar.event_date <= (timezone.now() + timezone.timedelta(days=-1)):
		status = 'completed'
	if seminar.event_is_active == False:
		status = 'canceled'

	template = loader.get_template('router_print.html')
	template_args = {
		'content': 'pages/seminar_print.html',
		'request': request,
		'title': '%s %s.%s.%s - %s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year, seminar.event_fz.name),

		'seminar': seminar,
		'seminar_program_template': "seminar_programs/" + seminar.event_program.program_short_name + ".html",
		'status': status,
	}
	return StreamingHttpResponse(template.render(template_args, request))


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
		############################################################
		send_copy_email = request.POST.get('send_copy_email', '')
		if send_copy_email == "yes":
			send_copy_email_to = unicode(request.POST.get('contact_email',''))
			try:
				validate_email(send_copy_email_to)
			except ValidationError as e:
				send_copy_email = ''


		form_act = request.POST.get('org_acting', '')
		form_act_type = ''
		if ( form_act != '' ):
			if ( form_act == 'ustav' ):
				form_act_type = u"устава"
			if ( form_act == 'polozhenie' ):
				form_act_type = u"положения"

		ur_addr_matches = request.POST.get('ur_addr_matches')
		ur_addr_matches_val = u'нет'
		if ( ur_addr_matches == 'yes' ):
			ur_addr_matches_val = u'да'


		body_head = u"Семинар: %s %s.%s.%s\n\n" % (unicode(seminar.event_city.name), seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
		body = u"""
		Тема: %s\n
		1. Организация: %s\n
			Действует на основании: %s\n
			ИНН: %s\n
			КПП: %s\n
			Расчетный счет: %s\n
			Название и адрес банка: %s\n
			Кор/счет банка: %s\n
			БИК: %s\n\n
			Почтовый адрес: %s, %s, %s, %s\n\n
			Юридический адрес совпадает с почтовым: %s\n\n
			Юридический адрес: %s, %s, %s, %s\n\n
		2. Руководитель (для оформления договора): %s\n
			Должность: %s\n\n
		3. Контактные лицо: %s\n
			Должность: %s\n
			E-mail: %s\n
			Телефон: %s\n\n
		4. Комментарий: %s\n\n
		5. Количество участников семинара: %s\n
		""" % (unicode(strip_tags(seminar.event_fz.description)),
				unicode(request.POST.get('org_name','')),
				unicode(form_act_type),
				unicode(request.POST.get('org_inn','')),
				unicode(request.POST.get('org_kpp','')),
				unicode(request.POST.get('org_account','')),
				unicode(request.POST.get('org_bank','')),
				unicode(request.POST.get('org_kor_account','')),
				unicode(request.POST.get('org_bik','')),
				unicode(request.POST.get('p_addr_zip_code','')),
				unicode(request.POST.get('p_addr_region','')),
				unicode(request.POST.get('p_addr_city','')),
				unicode(request.POST.get('p_addr_addr','')),
				unicode(ur_addr_matches_val),
				unicode(request.POST.get('ur_addr_zip_code','')),
				unicode(request.POST.get('ur_addr_region','')),
				unicode(request.POST.get('ur_addr_city','')),
				unicode(request.POST.get('ur_addr_addr','')),
				unicode(request.POST.get('head_fio','')),
				unicode(request.POST.get('head_post','')),
				unicode(request.POST.get('contact_name','')),
				unicode(request.POST.get('contact_post','')),
				unicode(request.POST.get('contact_email','')),
				unicode(request.POST.get('contact_phone','')),
				unicode(request.POST['comment']),
				unicode(request.POST.get('visitors_amount','')),
		)
		
		visitors_fio = request.POST.getlist('visitors_fio[]', [])
		visitors_post = request.POST.getlist('visitors_post[]', [])
		visitors_phone = request.POST.getlist('visitors_phone[]', [])

		if visitors_fio[0]:
			body += u"""
		6. Список участников семинара:\n
			"""
			for i in range(len(visitors_fio)):
				body += u"""
			Ф.И.О.: %s\n
			Должность: %s\n
			Телефон: %s\n
			======================\n
				""" % (unicode(visitors_fio[i]),
						unicode(visitors_post[i]),
						unicode(visitors_phone[i])
				)
		############################################################
		############################################################
		subject = u'Заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
		body_foot = ''
		if send_copy_email == "yes":
			body_foot = u"\nКопия заявки отправлена на E-Mail адрес контактного лица.\n"

		connection = mail.get_connection()
		connection.open()
		
		email = mail.EmailMessage(subject, body_head + body + body_foot, settings.ADMIN_EMAIL_FROM,
			settings.ADMIN_EMAIL_TO, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)
		
		email.send()


		if send_copy_email == "yes":
			subject = u'Вами отправлена заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
			body = u'Заявка на семинар отправлена, ожидайте обработки.\n\nСодержимое заявки:\n' + body

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
	return StreamingHttpResponse(template.render(template_args, request))



@xframe_options_exempt
@csrf_exempt
def ajax_banner(request, arg):

	banner = Banners.objects.filter(id=arg).first()
	if banner:
		click_count = int(banner.click_count) + 1
		Banners.objects.filter(id=arg).update(click_count=click_count)
		Banners.objects.filter(id=arg).update(last_click=timezone.now())

	return StreamingHttpResponse("", content_type="application/vnd.api+json", status=200)



@xframe_options_exempt
@csrf_exempt
def ajax_question(request):

	submitted = False
	error = False
	if request.method == 'POST':
		submitted = True


		gt_name = request.POST.get('gt_name', '')
		gt_phone = request.POST.get('gt_phone', '')
		gt_email = request.POST.get('gt_email', '')
		gt_message = request.POST.get('gt_message', '')

		try:
			validate_email(gt_email)
		except ValidationError as e:
			gt_email = ''

		if gt_name == '':
			error = u"Не введено имя!"
		if gt_email == '':
			error = u"Неверный E-Mail адрес!"
		if gt_message == '':
			error = u"Не введено сообщение!"

		if not error:
			if gt_phone == '' or gt_phone == '+7':
				gt_phone = u'не указан'

			body_head = u"Вам отправлен вопрос с сайта global-tender.ru.\n"
			body = u"""
Имя: %s
Телефон: %s
E-Mail: %s\n
Сообщение:
%s\n\n\nСообщение сформировано автоматически.
			""" % (unicode(gt_name),
					unicode(gt_phone),
					unicode(gt_email),
					unicode(gt_message),
			)


			subject = u"Задан вопрос на сайте global-tender.ru"

			connection = mail.get_connection()
			connection.open()

			email = mail.EmailMessage(subject, body_head + body, settings.ADMIN_EMAIL_FROM,
				settings.ADMIN_EMAIL_TO, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)

			email.send()


			# Send copy:
			subject = u"Копия: Задан вопрос на сайте global-tender.ru"
			body_head = u"Копия вашего вопроса с сайта global-tender.ru.\n\nСообщение доставлено, ожидайте ответа.\n"

			email = mail.EmailMessage(subject, body_head + body, settings.ADMIN_EMAIL_FROM,
				[gt_email], headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)

			email.send()

			connection.close()


	template = loader.get_template('ajax/question.html')
	template_args = {
		'request': request,
		'submitted': submitted,
		'error': error,
	}
	return StreamingHttpResponse(template.render(template_args, request))



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
	return StreamingHttpResponse(template.render(template_args, request))


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
	return StreamingHttpResponse(template.render(template_args, request))

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
	return StreamingHttpResponse(template.render(template_args, request))

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
	return StreamingHttpResponse(template.render(template_args, request))





######################
### Service views
######################

def robots(request):
	template = loader.get_template('static/robots.txt')
	template_args = {
		'request': request,
	}
	return StreamingHttpResponse(template.render(template_args, request), content_type='text/plain')

def humans(request):
	template = loader.get_template('static/humans.txt')
	template_args = {
		'request': request,
	}
	return StreamingHttpResponse(template.render(template_args, request), content_type='text/plain')

def handle404(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'static/404.html',
		'request': request,
		'title': 'Страница не найдена',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	return HttpResponseNotFound(template.render(template_args, request))