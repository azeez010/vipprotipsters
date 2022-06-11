from django.shortcuts import get_object_or_404
from tips import models
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        custom_data = ipn.custom
        data = custom_data.split("|")
        data_len = len(data)
        user_id = data[data_len - 1]
        subscription_id = data[data_len - 2]
        tipsters = data[:data_len - 2]
        # payment was successful
        sub_ticket = get_object_or_404(models.SubscriptionTicket, id=subscription_id)
        user = get_object_or_404(models.User, id=user_id)
        new_sub = models.Subscriptions.objects.create(user=user, subscription_ticket=sub_ticket, subscription_active=True)
        for tipster_id in tipsters:
            tipster = get_object_or_404(models.Tipsters, id=tipster_id)
            new_sub.tipsters.add(tipster)
        
        new_sub.save()