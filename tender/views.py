# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.http import StreamingHttpResponse
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, Http404

def index(request):
	template = loader.get_template('index.html')
	template_args = {
		'content': 'index_content.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

def seminars(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'seminars.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

def reviews(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'reviews.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))

def contacts(request):
	template = loader.get_template('inner_page.html')
	template_args = {
		'content': 'contacts.html',
		'request': request,
		'title': '',
	}
	context = RequestContext(request, template_args)
	return StreamingHttpResponse(template.render(context))