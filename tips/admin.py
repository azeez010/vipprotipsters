from django.contrib import admin
from tips import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Ticket)
admin.site.register(models.Settings)
admin.site.register(models.Tipsters)
admin.site.register(models.Subscriptions)
admin.site.register(models.SubscriptionTicket)