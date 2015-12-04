# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.http import StreamingHttpResponse
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, Http404

from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def index(request):
	template = loader.get_template('index.html')
	template_args = {
		'content': 'index_content.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def seminars(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'seminars.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def reviews(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'reviews.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))


@xframe_options_exempt
def contacts(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'contacts.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))