# -*- coding: utf-8 -*-
from django.db.models.aggregates import Sum, Count
from django.db.models import F
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete

from store.models import StoreIncome, Store, InvoiceOut, StoreSell, Sell, Delivery, Invoice, ClientInvoiceDebt, SellDebt, \
    Income, IncomeDebt, DeliveryDebt, ClientDeliveryDebt, DeliveryPart, ClientDebt, General


def signal_store_upd(sender, instance, **kwargs):

    raw = kwargs.get('raw', True)
    created = kwargs.get('created', False)

    if created or not raw:
        parts = sender.objects.filter(part=instance.part).aggregate(count=Coalesce(Sum('p_count'), 0))
        total = sender.objects.filter(parent=instance.parent).aggregate(total=Coalesce(Sum('total'), 0))

        if sender == InvoiceOut:
            parts = dict(p_outgo=parts.get('count'))
            obj, bool = Store.objects.update_or_create(part=instance.part, defaults=parts)
            obj.save()
        elif sender == StoreSell:
            parts = dict(p_sell=parts.get('count'))
            obj, bool = Store.objects.update_or_create(part=instance.part, defaults=parts)
            obj.save()
        elif sender == StoreIncome:
            parts = dict(p_income=parts.get('count'))
            obj, bool = Store.objects.update_or_create(part=instance.part, defaults=parts)
            obj.save()

        instance.parent.total = total.get('total')
        instance.parent.save()


post_save.connect(signal_store_upd, sender=StoreSell)
post_delete.connect(signal_store_upd, sender=StoreSell)
post_save.connect(signal_store_upd, sender=InvoiceOut)
post_delete.connect(signal_store_upd, sender=InvoiceOut)
post_save.connect(signal_store_upd, sender=DeliveryPart)
post_delete.connect(signal_store_upd, sender=DeliveryPart)
post_save.connect(signal_store_upd, sender=StoreIncome)
post_delete.connect(signal_store_upd, sender=StoreIncome)


def client_debt_upd(sender, instance, created, raw, **kwargs):
    """
    on Delivery set debt to Me and To Client
    on Invoice set debt to Client
    on Sell Set debt to Sell
    """

    if created or not raw:
        if sender == Invoice:
            debt, bool = ClientInvoiceDebt.objects.update_or_create(client=instance.client, debt=instance)
            debt.total = instance.debt
            debt.amount = instance.amount
            debt.save()
        elif sender == Sell:
            debt, bool = SellDebt.objects.update_or_create(debt=instance)
            debt.total = instance.debt
            debt.amount = instance.amount
            debt.save()
        elif sender == Income:
            debt, bool = IncomeDebt.objects.update_or_create(debt=instance)
            debt.total = instance.debt
            debt.amount = instance.amount
            debt.save()
        elif sender == Delivery:
            debt_inc, bool = DeliveryDebt.objects.update_or_create(debt=instance)
            debt_inc.total = instance.debt
            debt_inc.save()
            debt_clt, bool = ClientDeliveryDebt.objects.update_or_create(client=instance.client, debt=instance)
            debt_clt.total = instance.debt
            debt_clt.amount = instance.amount
            debt_clt.save()


post_save.connect(client_debt_upd, sender=Delivery)
post_save.connect(client_debt_upd, sender=Income)
post_save.connect(client_debt_upd, sender=Invoice)
post_save.connect(client_debt_upd, sender=Sell)


def general_upd(sender, instance, **kwargs):
    total = ClientDebt.objects.filter(client=instance.client).aggregate(total=Coalesce(Sum('total'), 0))
    amount = ClientDebt.objects.filter(client=instance.client).aggregate(amount=Coalesce(Sum('amount'), 0))

    instance.client.saldo = total.get('total') - amount.get('amount')
    instance.client.save()


post_save.connect(general_upd, sender=ClientInvoiceDebt)
post_save.connect(general_upd, sender=ClientDebt)
post_save.connect(general_upd, sender=ClientDeliveryDebt)
post_delete.connect(general_upd, sender=ClientInvoiceDebt)
post_delete.connect(general_upd, sender=ClientDebt)
post_delete.connect(general_upd, sender=ClientDeliveryDebt)



#todo Расчет и показ долгов