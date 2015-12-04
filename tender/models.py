from django.db import models
from django.contrib.auth.models import User



class FZs(models.Model):

	class Meta:
		verbose_name = "FZ"

	name                = models.CharField(max_length=50)
	description         = models.CharField(max_length=1000)



class Cities(models.Model):

	class Meta:
		verbose_name = 'Citie'

	name                = models.CharField(max_length=1000)
	picture             = models.CharField(max_length=1000)
	posted              = models.DateTimeField('date published')



class Seminar_Programs(models.Model):

	class Meta:
		verbose_name = "Seminar_Program"

	program_short_name  = models.CharField(max_length=50) # matches name of html file on disk
	program_time_limit  = models.CharField(max_length=1000)
	program_top_title   = models.CharField(max_length=1000)
	#program_file        = models.CharField(max_length=1000)



class Seminars(models.Model):

	class Meta:
		verbose_name = "Seminar"

	event_date          = models.DateTimeField('event date')
	event_city          = models.ForeignKey(Cities)
	event_fz            = models.ForeignKey(FZs)
	event_program       = models.ForeignKey(Seminar_Programs)
	event_contact_phone = models.CharField(max_length=1000)
	event_contact_name  = models.CharField(max_length=1000)
	event_contact_email = models.CharField(max_length=1000)