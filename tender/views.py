import os
import re
import operator
import datetime
import binascii
import json
from collections import OrderedDict

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

from tender.models import FZs, Seminars, Seminar_Programs, Cities, Banners, Clients



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
		page_title = 'Расписание семинаров'
	else:
		seminars = Seminars.objects.filter(event_is_active=True).filter(event_date__lt=(timezone.now() + timezone.timedelta(days=-1))).order_by('-event_date')
		page_title = 'Список недавно проведенных семинаров'

	seminars_all = {}

	for seminar in seminars:

		if seminar.event_fz.name in seminars_all:
			seminars_all[seminar.event_fz.name]['seminars'].append(seminar)
		else:
			seminars_all[seminar.event_fz.name] = {'seminars': [seminar], 'description': seminar.event_fz.description, 'sort': seminar.event_fz.sort}

	seminars_all_sorted = OrderedDict(sorted(seminars_all.items(), key=lambda v: v[1]['sort'], reverse=False))
	seminars_all_sorted = list(seminars_all_sorted.items())

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
			send_copy_email_to = request.POST.get('contact_email','')
			try:
				validate_email(send_copy_email_to)
			except ValidationError as e:
				send_copy_email = ''


		form_act = request.POST.get('org_acting', '')
		form_act_type = ''
		if ( form_act != '' ):
			if ( form_act == 'ustav' ):
				form_act_type = "устава"
			if ( form_act == 'polozhenie' ):
				form_act_type = "положения"

		ur_addr_matches = request.POST.get('ur_addr_matches')
		ur_addr_matches_val = 'нет'
		if ( ur_addr_matches == 'yes' ):
			ur_addr_matches_val = 'да'


		body_head = "Семинар: %s %s.%s.%s\n\n" % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
		body = """
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
		""" % (strip_tags(seminar.event_fz.description),
				request.POST.get('org_name',''),
				form_act_type,
				request.POST.get('org_inn',''),
				request.POST.get('org_kpp',''),
				request.POST.get('org_account',''),
				request.POST.get('org_bank',''),
				request.POST.get('org_kor_account',''),
				request.POST.get('org_bik',''),
				request.POST.get('p_addr_zip_code',''),
				request.POST.get('p_addr_region',''),
				request.POST.get('p_addr_city',''),
				request.POST.get('p_addr_addr',''),
				ur_addr_matches_val,
				request.POST.get('ur_addr_zip_code',''),
				request.POST.get('ur_addr_region',''),
				request.POST.get('ur_addr_city',''),
				request.POST.get('ur_addr_addr',''),
				request.POST.get('head_fio',''),
				request.POST.get('head_post',''),
				request.POST.get('contact_name',''),
				request.POST.get('contact_post',''),
				request.POST.get('contact_email',''),
				request.POST.get('contact_phone',''),
				request.POST['comment'],
				request.POST.get('visitors_amount',''),
		)
		
		visitors_fio = request.POST.getlist('visitors_fio[]', [])
		visitors_post = request.POST.getlist('visitors_post[]', [])
		visitors_phone = request.POST.getlist('visitors_phone[]', [])

		if visitors_fio[0]:
			body += """
		6. Список участников семинара:\n
			"""
			for i in range(len(visitors_fio)):
				body += """
			Ф.И.О.: %s\n
			Должность: %s\n
			Телефон: %s\n
			======================\n
				""" % (visitors_fio[i],
						visitors_post[i],
						visitors_phone[i]
				)
		############################################################
		############################################################
		subject = 'Заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
		body_foot = ''
		if send_copy_email == "yes":
			body_foot = "\nКопия заявки отправлена на E-Mail адрес контактного лица.\n"

		connection = mail.get_connection()
		connection.open()
		
		email = mail.EmailMessage(subject, body_head + body + body_foot, settings.ADMIN_EMAIL_FROM,
			settings.ADMIN_EMAIL_TO, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)
		
		email.send()


		if send_copy_email == "yes":
			subject = 'Вами отправлена заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
			body = 'Заявка на семинар отправлена, ожидайте обработки.\n\nСодержимое заявки:\n' + body

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
			error = "Не введено имя!"
		if gt_email == '':
			error = "Неверный E-Mail адрес!"
		if gt_message == '':
			error = "Не введено сообщение!"

		if not error:
			if gt_phone == '' or gt_phone == '+7':
				gt_phone = 'не указан'

			body_head = "Вам отправлен вопрос с сайта global-tender.ru.\n"
			body = """
Имя: %s
Телефон: %s
E-Mail: %s\n
Сообщение:
%s\n\n\nСообщение сформировано автоматически.
			""" % (gt_name,
					gt_phone,
					gt_email,
					gt_message,
			)


			subject = "Задан вопрос на сайте global-tender.ru"

			connection = mail.get_connection()
			connection.open()

			email = mail.EmailMessage(subject, body_head + body, settings.ADMIN_EMAIL_FROM,
				settings.ADMIN_EMAIL_TO, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)

			email.send()


			# Send copy:
			subject = "Копия: Задан вопрос на сайте global-tender.ru"
			body_head = "Копия вашего вопроса с сайта global-tender.ru.\n\nСообщение доставлено, ожидайте ответа.\n"

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





######################
### User views
######################

def get_referer(request):

	referer = request.META.get('HTTP_REFERER', '/')

	host = (request.is_secure() and 'https://' or 'http://') + request.META['HTTP_HOST']

	if not referer.startswith(host):
		referer = '/'

	return referer

@xframe_options_exempt
def signin(request):

	if request.method == 'GET':
		return HttpResponseRedirect('/')

	json_resp = {}
	json_resp['status'] = True
	json_resp['redirectURL'] = get_referer(request)

	if request.user.is_authenticated():
		return StreamingHttpResponse(json.dumps(json_resp, indent=4), content_type="application/vnd.api+json")

	email = request.POST.get('email', '').strip()
	password = request.POST.get('password', '').strip()

	if email and password:

		account = authenticate(email=email, password=password)
		if account is not None:
			if account.is_active:
				login(request, account)
				json_resp['responseText'] = ''
			else:
				json_resp['responseText'] = 'Пользователь неактивирован, Email адрес ожидает подтверждения.'
				json_resp['redirectURL'] = ''
		else:
			json_resp['responseText'] = 'Неверный email или пароль'
			json_resp['redirectURL'] = ''
	return StreamingHttpResponse(json.dumps(json_resp, indent=4), content_type="application/vnd.api+json")

@xframe_options_exempt
def signup(request):

	if request.method == 'GET':
		return HttpResponseRedirect('/')

	json_resp = {}
	json_resp['status'] = True
	json_resp['redirectURL'] = get_referer(request)

	if request.user.is_authenticated():
		return StreamingHttpResponse(json.dumps(json_resp, indent=4), content_type="application/vnd.api+json")

	email = request.POST.get('email', '').strip()
	password = request.POST.get('password', '').strip()
	password_verify = request.POST.get('password_verify', '').strip()

	if email and password and password_verify and password == password_verify:

		check_user = User.objects.filter(email__exact=email).first()
		if check_user:
			json_resp['responseText'] = 'Пользователь с указанным email адресом уже существует'
			json_resp['redirectURL'] = ''
		else:
			user = User.objects.create_user(
				username=email,
				email=email,
				password=password,
				is_active=False)
			client = Clients(
				user=user,
				email_confirmed=False,
				email_confirm_code=binascii.hexlify(os.urandom(25)).decode('utf-8'),
			)
			client.save()

			##### SEND EMAIL WITH CONFIRMATION CODE #####
			connection = mail.get_connection()
			connection.open()

			subject = "Пожалуйста, подтвердите свой адрес электронной почты - global-tender.ru"
			body = """Добро пожаловать на global-tender.ru.\nЧтобы завершить регистрацию, вам необходимо подтвердить свой адрес электронной почты.\n
Подтвердить по ссылке: {0}/confirm_email/?confirm_code={1}\n
Спасибо,
Команда PTPGO\n""".format(get_referer(request), client.email_confirm_code)

			email = mail.EmailMessage(subject, body, settings.ADMIN_EMAIL_FROM,
								  [email], connection=connection)

			email.send()
			connection.close()

			# Change popup
			json_resp['redirectURL'] = ''
			json_resp['confirmEmail'] = True

	else:
		json_resp['responseText'] = 'Ошибка введенных данных'
		json_resp['redirectURL'] = ''

	return StreamingHttpResponse(json.dumps(json_resp, indent=4), content_type="application/vnd.api+json")

@xframe_options_exempt
def confirm_email(request):

	email_confirmed = False

	confirm_code = request.GET.get('confirm_code', None)
	if not confirm_code:
		return HttpResponseRedirect('/')

	client = Clients.objects.filter(email_confirm_code=confirm_code).first()
	if client:
		Clients.objects.filter(id=client.id).update(email_confirm_code="")
		Clients.objects.filter(id=client.id).update(email_confirmed=True)
		User.objects.filter(id=client.user.id).update(is_active=True)

		email_confirmed = True
	else:
		return HttpResponseRedirect('/')

	template = loader.get_template('router.html')
	template_args = {
		'content': 'static/confirm_email.html',
		'request': request,
		'title': 'Подтверждение Email адреса',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
		'email_confirmed': email_confirmed,
	}
	return StreamingHttpResponse(template.render(template_args, request))

@xframe_options_exempt
def signout(request):

	referer = get_referer(request)

	if not request.user.is_authenticated():
		return HttpResponseRedirect(referer)


	logout(request)
	return HttpResponseRedirect(referer)
