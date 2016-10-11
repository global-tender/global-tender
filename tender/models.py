from django.db import models
from django.contrib.auth.models import User



class Regions(models.Model):

	class Meta:
		verbose_name_plural = 'Сайт: Регионы'

	def __str__(self):
		return str(self.region_name)

	region_name         = models.CharField(max_length=255, blank=False, null=False)



class FZs(models.Model):

	class Meta:
		verbose_name_plural = "Тендер: Федеральные законы"

	def __str__(self):
		return self.name

	name                = models.CharField(max_length=1000)
	description         = models.CharField(max_length=1000)
	top_description     = models.CharField(max_length=255, default="", blank=True, null=True)
	short_code          = models.CharField(max_length=255, default="", blank=False, null=False)
	allow_subscribe     = models.BooleanField(default=False)
	sort                = models.IntegerField(default=0)



class Cities(models.Model):

	class Meta:
		verbose_name_plural = 'Тендер: Города'

	def __str__(self):
		return 'Город: ' + self.name

	name                = models.CharField(max_length=1000)
	region              = models.ForeignKey(Regions, default=1)
	picture             = models.FileField(upload_to='city_pictures/')
	posted              = models.DateTimeField('date published')



class Seminar_Programs(models.Model):

	class Meta:
		verbose_name_plural = "Тендер: Программы семинаров"

	def __str__(self):
		return self.program_short_name

	program_short_name  = models.CharField(max_length=50) # matches name of html file on disk
	program_time_limit  = models.CharField(max_length=1000)
	program_top_title   = models.CharField(max_length=1000, blank=True)
	program_file        = models.FileField(upload_to='seminar_programs/', blank=True, null=True)



class Seminars(models.Model):

	class Meta:
		verbose_name_plural = "Тендер: Семинары"

	def __str__(self):
		return self.event_city.name + ': ' + str(self.event_date.year) + '-' + str(self.event_date.month) + '-' + str(self.event_date.day)

	def get_absolute_url(self):
		return '/seminars/' + str(self.id) + '/'

	event_date          = models.DateTimeField('event date')
	event_city          = models.ForeignKey(Cities)
	event_fz            = models.ForeignKey(FZs)
	event_program       = models.ForeignKey(Seminar_Programs)
	event_contact_phone = models.CharField(max_length=1000)
	event_contact_name  = models.CharField(max_length=1000)
	event_contact_email = models.CharField(max_length=1000)
	event_price_person  = models.CharField(max_length=1000, default="", blank=True, null=True)
	event_title         = models.CharField(max_length=1000, default="", blank=True, null=True)
	event_is_active     = models.BooleanField(default=True)
	event_urgent_info   = models.CharField(max_length=1000, default="", blank=True, null=True)



class Clients(models.Model):

	class Meta:
		verbose_name_plural = 'Клиенты: Клиент'

	def __str__(self):
		return 'ID: ' + str(self.id) + ' | Пользователь: ' + self.user.email

	user                = models.ForeignKey(User)

	email_confirmed     = models.BooleanField(default=False)  # Был ли подтвержден E-Mail
	email_confirm_code  = models.CharField(max_length=255, blank=True, null=True)  # Код потверждения E-Mail адреса



class Subscribe(models.Model):

	class Meta:
		verbose_name_plural = 'Сайт: Подписки на рассылки'

	def __str__(self):
		return 'ID: ' + str(self.id) + ' | Email: ' + self.email

	email               = models.CharField(max_length=255, blank=False, null=False)
	region              = models.ForeignKey(Regions, default=1)
	seminar_type        = models.ForeignKey(FZs, default=1)