from django.db.models.aggregates import Sum, Count
from django.db.models import F
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete

from store.models import StoreIncome, Store, InvoiceOut, StoreSell, Sell, Delivery, Invoice


def signal_store_income(sender, **kwargs):
    instance = kwargs.get('instance', False)
    if instance:
        parts = StoreIncome.objects.filter(part=instance.part).aggregate(p_income=Sum('p_count'))
        if not parts.get('p_income'):
            parts['p_income'] = 0
        Store.objects.update_or_create(part=instance.part, defaults=parts)

post_save.connect(signal_store_income, sender=StoreIncome)
post_delete.connect(signal_store_income, sender=StoreIncome)


def signal_store_sell(sender, **kwargs):
    instance = kwargs.get('instance', False)

    if instance:
        parts = sender.objects.filter(part=instance.part).aggregate(count=Coalesce(Sum('p_count'), 0))
        total = sender.objects.filter(sell=instance.sell).aggregate(total=Coalesce(Sum('total'), 0))

        if sender == InvoiceOut:
            parts = dict(by_inv_count=parts.get('count'))
            Store.objects.update_or_create(part=instance.part, defaults=parts.get('count'))
        elif sender == Sell:
            parts = dict(sell_count=parts.get('count'))
            Store.objects.update_or_create(part=instance.part, defaults=parts.get('count'))

        instance.sell.total = total.get('total')
        instance.sell.save()


post_save.connect(signal_store_sell, sender=StoreSell)
post_delete.connect(signal_store_sell, sender=StoreSell)
post_save.connect(signal_store_sell, sender=InvoiceOut)
post_delete.connect(signal_store_sell, sender=InvoiceOut)
post_save.connect(signal_store_sell, sender=Delivery)
post_delete.connect(signal_store_sell, sender=Delivery)


def client_debt_upd(sender, **kwargs):
    instance = kwargs.get('instance', False)
    debt_field = False

    if instance:
        debt = sender.objects.filter(client=instance.client).aggregate(debt=Coalesce(Sum('debt'), 0))
        if sender == Invoice:
            instance.client.inv_debt = debt.get('debt')
        elif sender == Delivery:
            instance.client.del_debt = debt.get('debt')

        instance.client.save()

post_save.connect(client_debt_upd, sender=Invoice)
post_save.connect(client_debt_upd, sender=Delivery)

#Todo Add cash income auto