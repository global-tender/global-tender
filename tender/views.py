import os
import sys
import re
import operator
import datetime
import binascii
import json
import random
from collections import OrderedDict

from mailchimp3 import MailChimp

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.http import HttpResponseRedirect, Http404
from django.template import loader

from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.html import strip_tags
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from tender.models import FZs, Seminars, Seminar_Programs, Cities, Clients, Subscribe, Regions


def send_email_custom(subject, body, email_from, email_to):
	connection = mail.get_connection()
	connection.open()
	email = mail.EmailMessage(subject, body, email_from, email_to, headers = {'Reply-To': settings.ADMIN_EMAIL_FROM}, connection=connection)
	email.send()

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
		send_copy_email_to = request.POST.get('contact_email','')
		if send_copy_email == "yes":
			try:
				validate_email(send_copy_email_to)
			except ValidationError as e:
				send_copy_email = ''
				send_copy_email_to = ''


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
				send_copy_email_to,
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

		send_email_custom(subject, body_head + body + body_foot, settings.ADMIN_EMAIL_FROM, settings.ADMIN_EMAIL_TO)

		if send_copy_email == "yes":
			subject = 'Вами отправлена заявка на семинар: %s %s.%s.%s' % (seminar.event_city.name, seminar.event_date.strftime('%d'), seminar.event_date.strftime('%m'), seminar.event_date.year)
			body = 'Заявка на семинар отправлена, ожидайте обработки.\n\nСодержимое заявки:\n' + body

			send_email_custom(subject, body_head + body, settings.ADMIN_EMAIL_FROM, [send_copy_email_to])

		if send_copy_email_to != "":
			# Подписать контактный email адрес на рассылку по текущему региону
			if seminar.event_fz.allow_subscribe:  # разрешена подписка на этот семинар
				if seminar.event_city.region:  # поле "Регион" у города заполнено
					resp = {'error':False, 'success':[]}
					over_seminar_request = True

					resp = subscribe_logic([seminar.event_fz.short_code], seminar.event_city.region.id, send_copy_email_to, resp, over_seminar_request)


	template = loader.get_template('ajax/seminar.html')
	template_args = {
		'request': request,
		'seminar': seminar,
		'submitted': submitted,
		'send_copy_email': send_copy_email,
	}
	return StreamingHttpResponse(template.render(template_args, request))



# Function
def subscribe_logic(seminar_types, region_id, email_addr, resp, over_seminar_request=False):
	try:
		client = MailChimp('Globaltender', settings.MAILCHIMP_API_KEY)

		region = Regions.objects.filter(id=region_id).first()  # Объект региона

		for seminar_short_code in seminar_types:

			sem_type = FZs.objects.filter(short_code=seminar_short_code).first()  # Объект семинара

			# Our DB:
			subscr_user = Subscribe.objects.filter(email=email_addr,region=region,seminar_type=sem_type)
			if not subscr_user:
				subscr_new = Subscribe(
					email=email_addr,
					region=region,
					seminar_type=sem_type,
				)
				subscr_new.save()

			# mailchimp DB:

			# Проверим существования Списка по указанной подписке, если нету, создадим.
			list_id = False
			lists = client.list.all(count=100000, fields="lists.name,lists.id")
			for lst in lists['lists']:
				if lst['name'] == 'global-tender.ru: %s, %s' % (region.region_name, sem_type.name):
					list_id = lst['id']
					break
			if not list_id:
				resp_cli = client.list.create({
					'name': 'global-tender.ru: %s, %s' % (region.region_name, sem_type.name),
					'contact': {
						'company': 'Глобал-Тендер',
						'address1': 'г. Ростов-на-Дону, Серафимовича 58а',
						'city': 'Ростов-на-Дону',
						'state': '',
						'zip': '344002',
						'country': 'RU',
						'phone': ''
					},
					'permission_reminder': 'Вы получили письмо так как подписались на рассылку на сайте https://global-tender.ru',
					'use_archive_bar': True,
					'campaign_defaults' : {
						'from_name': 'Глобал-Тендер',
						'from_email': 'zakupki.gov@global-tender.ru',
						'subject': '',
						'language': 'ru'
					},
					'notify_on_subscribe': '',
					'notify_on_unsubscribe': '',
					'email_type_option': False,
					'visibility': 'pub'
				})
				list_id = resp_cli['id']

			# Получили ID Списка. Проверим существует ли подписчик в этом списке. Если нет, добавим
			member_email_subscribed = False
			members = client.member.all(list_id, count=100000, offset=0, fields="members.email_address")
			for member in members['members']:
				if member['email_address'] == email_addr:
					member_email_subscribed = email_addr
					resp['success'].append('Вы уже подписаны на рассылку:<br /><span>%s, %s</span>' % (region.region_name, sem_type.name))
					break
			if not member_email_subscribed:
				resp_cli = client.member.create(list_id, {
					'email_address': email_addr,
					'status': 'subscribed',
					'status_if_new': 'subscribed'
				})
				if resp_cli['id']:
					resp['success'].append('Подписка на рассылку создана:<br /><span>%s, %s</span>' % (region.region_name, sem_type.name))

					# Отправить уведомление администратору на почту
					subject = "Новая подписка на рассылку на сайте global-tender.ru"
					body = "Пользователь подписался на рассылку на сайте global-tender.ru.\n\nE-Mail: %s\nРегион: %s\nСеминар: %s\n" % (email_addr, region.region_name, sem_type.name)
					if over_seminar_request:
						subject += ", через заявку на семинар"
						body += "\nПодписка автоматическая, через подачу заявки на участие в семинаре.\n"
					send_email_custom(subject, body, settings.ADMIN_EMAIL_FROM, settings.ADMIN_EMAIL_TO)
				else:
					# Не удалось подписать пользователя по неизвестной причине
					raise Exception('Failed to create member for list: %s.' % list_id)
	except Exception as e:
		resp['error'] = "Ошибка, не удалось подписать на рассылку.<br />Мы уже уведомлены о возникшем инциденте!"
		err_lst = ''

		if 'lists' in vars():
			err_lst += str(lists)
		if 'members' in vars():
			err_lst += str(members)

		subject = "Ошибка подписки на рассылку global-tender.ru"
		body = "Возник инцидент при попытке подписать пользователя на рассылку.\nВведенные данные:\n\nE-Mail: %s\nРегион: %s\nСеминар: %s\n\nДетальная информация об исключении:\n\n%s\n\n%s" % (email_addr, region.region_name, sem_type.name, str(sys.exc_info()), err_lst)
		if over_seminar_request:
			subject += ", через заявку на семинар"
			body += "\n\nПодписка автоматическая, через подачу заявки на участие в семинаре.\n"
		send_email_custom(subject, body, settings.ADMIN_EMAIL_FROM, settings.ADMIN_EMAIL_TO)
		print(body)
	return resp



@xframe_options_exempt
@csrf_exempt
def subscribe(request):
	resp = {'error':False, 'success':[]}

	fz_list = FZs.objects.filter(allow_subscribe=True)
	regions_list = Regions.objects.all()

	if request.method == 'POST':

		seminar_types = request.POST.getlist('seminar_type', None)
		region_id = request.POST.get('region_id', None)
		email_addr = request.POST.get('gt_email', None)

		if not seminar_types:
			resp['error'] = "Не выбрано ни одного семинара!"
		elif not region_id:
			resp['error'] = "Не указан регион!"
		elif not email_addr:
			resp['error'] = "Не указан E-Mail адрес!"
		else:
			try:
				validate_email(email_addr)
			except ValidationError as e:
				resp['error'] = "Неверный формат E-Mail адреса!"

		if not resp['error']:

			resp = subscribe_logic(seminar_types, region_id, email_addr, resp)


	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/subscribe.html',
		'request': request,
		'success': resp['success'],
		'error': resp['error'],
		'fz_list': fz_list,
		'regions_list': regions_list,
		'title': 'Подписка на рассылку о новых семинарах',
		'menu_color_class': 'menu-white',
		'menu_inner': 'menu-inner',
	}
	return StreamingHttpResponse(template.render(template_args, request))



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

@xframe_options_exempt
def service(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/service.html',
		'request': request,
		'title': 'Подготовим гибкое положение по 223-ФЗ в соответствии с законными требованиями.',
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

	#host = (request.is_secure() and 'https://' or 'http://') + request.META['HTTP_HOST']
	host = 'https://' + request.META['HTTP_HOST']

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
			json_resp['responseText'] = 'Неверный Email или пароль'
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
Команда global-tender\n""".format('https://'+request.META['HTTP_HOST'], client.email_confirm_code)

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
