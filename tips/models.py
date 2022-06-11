from datetime import timedelta
from django.db import models
from tips.mixins import BaseModelMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.contrib.auth.base_user import BaseUserManager
from django.utils.timezone import now
from django.urls import reverse

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)

    def get_by_alternate_key(self, phone_number):
        return self.get(**{self.model.ALTERNATE_KEY_FIELD: phone_number})

# Create your models here.

class User(AbstractUser):
    country = CountryField()
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True) # changes email to unique and blank to false
    REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS

    class Meta:
        verbose_name = _("User")

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return self.username


class Ticket(BaseModelMixin):
    club_image = models.URLField(max_length=500, blank=False, null=False) 
    team_name = models.CharField(max_length=255, blank=False, null=False)
    game_odds = models.FloatField(blank=False) 
    tips = models.CharField(_("Tips"),
        blank=False,
        null=False,
        max_length=50
    )
    success = models.BooleanField(_("Did Game success"), default=False)
    played = models.BooleanField(_("Has Game played"), default=False)
    postponed = models.BooleanField(_("Was game cancelled or postponed"), default=False)
    
    class meta:
        orderings = ['-data_added']
    
    def __str__(self):
            return self.team_name + " - " + str(self.game_odds)

class Tipsters(models.Model):
    country = CountryField()
    name = models.CharField(_("Name"),
        blank=False,
        null=False,
        max_length=255
    )

    tickets = models.ManyToManyField(
        to="tips.Ticket",
        verbose_name=_("Tickets"),
        blank=True,
        related_name="Tickets",
    )

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tipster', args=[str(self.id)])
    
    class meta:
        verbose_name = "Tipster"
        verbose_name_plural = "Tipsters"

class SubscriptionTicket(BaseModelMixin):
    price = models.IntegerField(blank=False, null=False) 
    currency = models.CharField(_("Currency"),
        blank=False,
        null=False,
        max_length=3
    )
    days = models.IntegerField(blank=False, null=False)

    def __str__(self) -> str:
        return str(self.days) + " Days - " + str(self.price) + " " + self.currency + " per tipster"

class Subscriptions(BaseModelMixin):
    user = models.ForeignKey(
        to="tips.User",
        verbose_name=_("User"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="user",
    )
    subscription_ticket = models.ForeignKey(
        to="tips.SubscriptionTicket",
        verbose_name=_("Subscription Ticket"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="subscription_ticket",
    )

    tipsters = models.ManyToManyField(
        to="tips.Tipsters",
        verbose_name=_("Tipsters"),
        blank=True,
        related_name="Tipsters",
    )

    
    subscription_active = models.BooleanField(default=False)

    def update_subscription_status(self):
        sub_ticket_days = self.subscription_ticket.days
        sub_expiry_date = timedelta(days=sub_ticket_days) + self.date_added 
        sub_status = not (now().date() > sub_expiry_date)
        if self.subscription_active != sub_status:
            self.subscription_active = sub_status
            super().save()
    
    def __str__(self):
        return str(self.user) + " subbed " + str(self.subscription_ticket) + " is " + str(self.subscription_active)
    class meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

class Settings(models.Model):
    key = models.CharField(max_length=20, blank=False, null=False)
    value = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self) -> str:
        return self.key + " - " + self.value 
    class meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"