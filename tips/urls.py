from django.urls import path, include
from tips import views, func_views, payment


urlpatterns = [
    path('', views.getc, name="home"),
    path('tipster/<int:pk>', views.Tipster.as_view(), name="tipster"),
    path('payment/', views.Payment.as_view(), name="payment"),
    path('login-user', views.login_view, name="login-view"),
    path('signup-user', views.signup_view, name="signup-view"),
    path('', include('django.contrib.auth.urls')),
    path('save', func_views.save_csv, name="save-csv"),
    path('result', func_views.result, name="result"),
    path('select-tips', views.select_tips, name="select-tips"),
    path('subcription-page', views.subscription_view, name="subcription-page"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal-return/', payment.PaypalReturnView.as_view(), name='paypal-return'),
    path('paypal-cancel/', payment.PaypalCancelView.as_view(), name='paypal-cancel'),
]