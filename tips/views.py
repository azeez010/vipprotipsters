import datetime, random
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, ListView, CreateView
from django.views.decorators.cache import cache_page
from tips import forms, models, mixins, utils
from django.conf import settings
from django.http import Http404
from pathlib import Path
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required 
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect(reverse("home"))

        else:
            messages.error(request, "wrong password or email Address")
            return redirect(reverse("home"))


def signup_view(request):
    if request.method == "POST":
        user_sign_up = forms.SignUp(request.POST)
        if user_sign_up.is_valid():
            user = user_sign_up.save()
            user.set_password(user.password)
            messages.success(request, "Signup Successful")
            return redirect(reverse("home"))
        else:
            messages.error(request, f"{user_sign_up.errors}" )
            return redirect(reverse("home"))

def subscription_view(request):
    if request.method == "POST":
        user_sign_up = forms.SignUp(request.POST)
        if user_sign_up.is_valid():
            user = user_sign_up.save()
            user.set_password(user.password)
            messages.success(request, "Signup Successful")
            return redirect(reverse("home"))
        else:
            messages.error(request, f"{user_sign_up.errors}" )
            return redirect(reverse("home"))

    sub_ticket = models.Subscriptions.objects.filter(user_id=request.user.id).last()
    if sub_ticket: sub_ticket.update_subscription_status()
    print(sub_ticket.tipsters.all(), "kjsk")
    context = {
        "sub_ticket": sub_ticket
    }
    return render(request, "subscription_page.html", context)

class FreeTipsView(TemplateView):
    # template_name = 'templates/form_template.html'
    template_name = "free_tips.html"
    extra_context = {}
    @cache_page(60)
    def get(self, *args, **kwargs):
        # form = self.form_class(initial=self.initial)
        # time.sleep(60)
        ra = random.randrange(0, 1000000000)
        my_key = f'hello, world! at {ra}'
        self.extra_context["my_key"] = my_key
    
    # @method_decorator(getc)
    # def dispatch(self, *args, **kwargs):
    # # @cache_page(60)
    #     return super().dispatch(*args, **kwargs)
    
    # def getc(self, request, *args, **kwargs):
    #     # form = self.form_class(initial=self.initial)
    #     # time.sleep(60)
    #     ra = random.randrange(0, 1000000000)
    #     my_key = f'hello, world! at {ra}'
        # return render(request, self.template_name, {"my_key": my_key} )
    # extra_context = {}
    # my_key = cache.get('my_key')
    # print(my_key)
    # if my_key:
    #     extra_context["my_key"] = my_key 
    # else:
    #     time.sleep(60)
    #     ra = random.randrange(0, 1000000000)
    #     my_key = f'hello, world! at {ra}'
    #     cache.set('my_key', my_key, 30)
    #     extra_context["my_key"] = my_key

    # extra_context["d"] = "my_key"
# @cache_page(60)

@staff_member_required
def select_tips(request, *args, **kwargs):
    template_name = "select_tips.html"
    cur_date_time = datetime.datetime.now()
    
    if request.method == "POST":
        ls = list(request.POST.values())
        folder = utils.get_folder("paid")
        file_name = f"{cur_date_time.date()}-paid.csv"
        csv = mixins.CSV.readCSV(folder, file_name)
        games_to_select = []
        
        for line in csv:
            if f"{line[2]} {line[3]}" in ls:
                line[0] = True
                games_to_select.append(line)
            else:
                line[0] = False
    
        tickets = models.Ticket.objects
        tickets.filter(date_added=cur_date_time).delete()
        for d in games_to_select:        
            obj_data = {
                "club_image": d[1],
                "team_name": d[2],
                "tips": d[3],
                "game_odds": d[4]
            }
            
            if obj_data.get("game_odds") != "-":
                ticket = tickets.create(**obj_data)
                ticket.save()  
                
        mixins.CSV.addCsv(file_name, folder, csv)
        return redirect(reverse("select-tips"))

    path = Path(settings.PAID_CSV_STATIC_URL + f"{cur_date_time.date()}-paid.csv")
    if path.exists():
        folder = utils.get_folder("paid")
        file_name = f"{cur_date_time.date()}-paid.csv"
        tips = mixins.CSV.readCSV(folder, file_name)
    else:
        tips = []
    utils.generate_predictions()
    return render(request, template_name, {"tips": tips})

def paid_view(request, *args, **kwargs):
    template_name = "paid_tips.html"
    
    tipsters = models.Tipsters.objects.all()
    sign_up = forms.SignUp()
    login = forms.Login()
    return render(request, template_name, {"sign_up": sign_up, "login": login, "tipsters": tipsters })

            
def freetips_view(request, *args, **kwargs):
    template_name = "free_tips.html"
    date = request.GET.get("date")
    
    cur_date_time = datetime.datetime.now()
    page_date = cur_date_time.strftime(r'%A, %d %B %Y')
    prev = ""
    next = ""
    one_day_diff = datetime.timedelta(days=1)
    if date:
        name = f"{date}-freebet.csv"
        try:
            date_time = datetime.datetime.strptime(date, r'%Y-%m-%d')
            prev_pred = date_time - one_day_diff
            next_pred = date_time + one_day_diff
            all_files = utils.get_all_csv("freebet")
            if f"{prev_pred.date()}-freebet.csv" in all_files:
                prev = f"/?date={prev_pred.date()}"
            if f"{next_pred.date()}-freebet.csv" in all_files:
                next = f"/?date={next_pred.date()}"
            
            path = Path(settings.CSV_STATIC_URL + f"{date_time.date()}-freebet.csv")
            page_date = date_time.strftime(r'%A, %d %B %Y')
                
        except Exception as exc:
            print(exc)
            now = cur_date_time.date()
            name = f"{now}-freebet.csv"
            prev_pred = cur_date_time - one_day_diff
            next_pred = cur_date_time  + one_day_diff
            path = Path(settings.CSV_STATIC_URL + f"{now}-freebet.csv")
            all_files = utils.get_all_csv("freebet")
            if f"{prev_pred.date()}-freebet.csv" in all_files:
                prev = f"/?date={prev_pred.date()}"
            if f"{next_pred.date()}-freebet.csv" in all_files:
                next = f"/?date={next_pred.date()}"
            
    else:
        now = cur_date_time.date()
        name = f"{now}-freebet.csv"
        path = Path(settings.CSV_STATIC_URL + f"{now}-freebet.csv")
        all_files = utils.get_all_csv("freebet")
        
        prev_pred = cur_date_time - one_day_diff
        next_pred = cur_date_time + one_day_diff
        if f"{prev_pred.date()}-freebet.csv" in all_files:
            prev = f"/?date={prev_pred.date()}"
        if f"{next_pred.date()}-freebet.csv" in all_files:
            next = f"/?date={next_pred.date()}"
            
    if path.exists():
        folder = utils.get_folder("freebet")
        free_tips = mixins.CSV.readCSV(folder, name)
    else:
        free_tips = []

    next_and_prev = {
        "prev": prev,
        "next": next,
        "page_date": page_date
    }   
    return render(request, template_name, {"free_tips": free_tips, **next_and_prev} )

# class ManageGames(DetailView, ListView, mixins.CSVmixin):
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data(object=self.object)
#         return self.render_to_response(context)

    pass


class Tipster(DetailView):
    model = models.Tipsters



class Subscriptions(ListView):
    model = models.Tipsters
    template_name: str = "tips/user_subscription.html"

    def get_queryset(self):
        # self.queryset = self.model.objects.filter(user_id).first().
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False."), {
                        "class_name": self.__class__.__name__,
                    }
                )

        # order_id = request.session.get('order_id')
        # order = get_object_or_404(Order, id=order_id)
        host = request.get_host()

        _settings = models.Settings.objects.all() 
        save_settings = {}
        for setting in _settings:
            save_settings[setting.key] = setting.value

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '',
            'item_name': 'User{}'.format(request.user.id),
            "bn": "Vipprotipsters",             
            "custom": "",
            'currency_code': f'{save_settings["currency"]}',
            'notify_url': 'https://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'https://{}{}'.format(host,
                                            reverse('paypal-return')),
            'cancel_return': 'https://{}{}'.format(host,
                                                reverse('paypal-cancel')),
        }

        # str(order.id)
        form = PayPalPaymentsForm(initial=paypal_dict)

        subscription_types = models.SubscriptionTicket.objects.all()
        context = self.get_context_data()
        context["subscription_types"] = subscription_types
        context["form"] = form
        return self.render_to_response(context)

class Payment(ListView):
    model = models.Tipsters
    template_name: str = "tips/payment.html"

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False."), {
                        "class_name": self.__class__.__name__,
                    }
                )

        # order_id = request.session.get('order_id')
        # order = get_object_or_404(Order, id=order_id)
        host = request.get_host()

        _settings = models.Settings.objects.all() 
        save_settings = {}
        for setting in _settings:
            save_settings[setting.key] = setting.value

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '',
            'item_name': 'User{}'.format(request.user.id),
            "bn": "Vipprotipsters",             
            "custom": "",
            'currency_code': f'{save_settings["currency"]}',
            'notify_url': 'https://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'https://{}{}'.format(host,
                                            reverse('paypal-return')),
            'cancel_return': 'https://{}{}'.format(host,
                                                reverse('paypal-cancel')),
        }

        # str(order.id)
        form = PayPalPaymentsForm(initial=paypal_dict)

        subscription_types = models.SubscriptionTicket.objects.all()
        context = self.get_context_data()
        context["subscription_types"] = subscription_types
        context["form"] = form
        return self.render_to_response(context)
