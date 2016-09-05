from django.contrib import admin

from tender.models import FZs
from tender.models import Cities
from tender.models import Seminar_Programs
from tender.models import Seminars
from tender.models import Banners
from tender.models import Clients
from tender.models import Subscribe

admin.site.register(FZs)
admin.site.register(Cities)
admin.site.register(Seminar_Programs)
admin.site.register(Seminars)
admin.site.register(Banners)
admin.site.register(Clients)
admin.site.register(Subscribe)