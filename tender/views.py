# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.http import StreamingHttpResponse
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, Http404

from django.views.decorators.clickjacking import xframe_options_exempt



@xframe_options_exempt
def index(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/index.html',
		'request': request,
		'title': '',
		'menu_color_class': 'menu-white',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def seminars(request):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/seminars.html',
		'request': request,
		'title': 'Расписание семинаров',
		'menu_color_class': 'menu-black',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

@xframe_options_exempt
def seminar_detail(request, arg):
	template = loader.get_template('router.html')
	template_args = {
		'content': 'pages/seminar.html',
		'request': request,
		'title': '',
		'menu_color_class': 'menu-white',
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