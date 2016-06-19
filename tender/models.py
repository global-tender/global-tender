# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User



class FZs(models.Model):

	class Meta:
		verbose_name = "FZ"

	def __unicode__(self):
		return u'' + self.name

	name                = models.CharField(max_length=50)
	description         = models.CharField(max_length=1000)
	sort                = models.IntegerField(default=0)



class Cities(models.Model):

	class Meta:
		verbose_name = 'Citie'

	def __unicode__(self):
		return u'Город: ' + self.name

	name                = models.CharField(max_length=1000)
	picture             = models.FileField(upload_to='city_pictures/')
	posted              = models.DateTimeField('date published')



class Seminar_Programs(models.Model):

	class Meta:
		verbose_name = "Seminar_Program"

	def __unicode__(self):
		return u'' + self.program_short_name

	program_short_name  = models.CharField(max_length=50) # matches name of html file on disk
	program_time_limit  = models.CharField(max_length=1000)
	program_top_title   = models.CharField(max_length=1000, blank=True)
	program_file        = models.FileField(upload_to='seminar_programs/', blank=True, null=True)



class Seminars(models.Model):

	class Meta:
		verbose_name = "Seminar"

	def __unicode__(self):
		return u'' + self.event_city.name + ': ' + str(self.event_date.year) + '-' + str(self.event_date.month) + '-' + str(self.event_date.day)

	def get_absolute_url(self):
		return '/seminars/' + str(self.id) + '/'

	event_date          = models.DateTimeField('event date')
	event_city          = models.ForeignKey(Cities)
	event_fz            = models.ForeignKey(FZs)
	event_program       = models.ForeignKey(Seminar_Programs)
	event_contact_phone = models.CharField(max_length=1000)
	event_contact_name  = models.CharField(max_length=1000)
	event_contact_email = models.CharField(max_length=1000)
	event_price_person  = models.CharField(max_length=1000, default="",blank=True, null=True)
	event_is_active     = models.BooleanField(default=True)



class Banners(models.Model):

	class Meta:
		verbose_name_plural = "Banners"

	def __unicode__(self):
		return u'' + str(self.id)

	banner_name         = models.CharField(max_length=1000)
	click_count         = models.IntegerField(default=0)
	last_click          = models.DateTimeField('last click date/time', blank=True, null=True)
