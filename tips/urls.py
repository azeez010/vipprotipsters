from django.urls import path, include
from tips import views, func_views, payment
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.freetips_view, name="home"),
    path('tipsters', views.paid_view, name="paid"),
    path('change-password', views.change_password_view, name="change-password"),
    path('tipster/<int:pk>', views.Tipster.as_view(), name="tipster"),
    path('payment/', login_required(views.Payment.as_view()), name="payment"),
    path('login-user', views.login_view, name="login-view"),
    path('git-update', func_views.git_update, name="git-update"),
    path('signup-user', views.signup_view, name="signup-view"),
    path('', include('django.contrib.auth.urls')),
    path('save', func_views.save_csv, name="save-csv"),
    path('result', func_views.result, name="result"),
    path('select-tips', views.select_tips, name="select-tips"),
    # path('subcription-page', views.subscription_view, name="subcription-page"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal-return/', payment.PaypalReturnView.as_view(), name='paypal-return'),
    path('paypal-cancel/', payment.PaypalCancelView.as_view(), name='paypal-cancel'),
]