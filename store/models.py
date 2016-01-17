from __future__ import unicode_literals

import datetime


from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class Client(models.Model):
    name = models.CharField(max_length=40, verbose_name=_('client_name'))
    phone = models.CharField(max_length=45, blank=True, null=True, verbose_name=_('phone'))
    memo = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('memo'))
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('debt'))
    photo = models.ImageField(blank=True, null=True, verbose_name=_('photo'))

    def __unicode__(self):
        return "%s - %s" % (self.name, self.saldo)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Client, self).save(force_insert, force_update,
                                 using, update_fields)

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")


class MainInvoice(models.Model):
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("total"))
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("discount"))
    debt = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("debt"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("amount"))
    v_date = models.DateField(default=datetime.date.today, verbose_name=_("date"))
    memo = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('memo'))
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.debt = self.total - self.discount

        super(MainInvoice, self).save()


class Invoice(MainInvoice):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("client"))

    class Meta:
        verbose_name = _("sell from store")
        verbose_name_plural = _("sales from store")


class Delivery(MainInvoice):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("client"))

    class Meta:
        verbose_name = _("direct delivery")
        verbose_name_plural = _("direct deliveries")


class Sell(MainInvoice):

    class Meta:
        verbose_name = _("sell from shop")
        verbose_name_plural = _("sales from shop")


class Income(MainInvoice):

    class Meta:
        verbose_name = _("delivery to store")
        verbose_name_plural = _("deliveries to store")


class General(models.Model):
    MY_DEBT = 1
    CLIENT_DEBT = 2
    SELL_DEBT = 3

    DEBT_CHOICES = (
        (MY_DEBT, _("My debt")),
        (CLIENT_DEBT, _("Client debt")),
        (SELL_DEBT, _("Sell debt")),
    )

    type = models.PositiveIntegerField(choices=DEBT_CHOICES, default=1, verbose_name=_("debt_type"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("total"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_("amount"))
    v_date = models.DateField(default=datetime.date.today, verbose_name=_("date"))
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return _("Total: %14.2f, Amount: %14.2f, Date: %s") % (self.total, self.amount, self.v_date)

    class Meta:
        verbose_name = _("general")
        verbose_name_plural = _("generals")


class DeliveryAmount(General):

    @property
    def debt_amount(self):
        total = DeliveryAmount.objects.aggregate(total=Coalesce(Sum('total'), 0))
        amount = DeliveryAmount.objects.aggregate(amount=Coalesce(Sum('amount'), 0))
        return total.get('total', 0) - amount.get('amount', 0)

    class Meta:
        verbose_name = _("delivery amount")
        verbose_name_plural = _("delivery amounts")


class DeliveryDebt(DeliveryAmount):
    debt = models.OneToOneField(Delivery, on_delete=models.CASCADE, verbose_name=_("debt"))

    class Meta:
        verbose_name = _("delivery debt")
        verbose_name_plural = _("delivery debts")


class IncomeAmount(General):

    @property
    def debt_amount(self):
        total = IncomeAmount.objects.aggregate(total=Coalesce(Sum('total'), 0))
        amount = IncomeAmount.objects.aggregate(amount=Coalesce(Sum('amount'), 0))
        return total.get('total', 0) - amount.get('amount', 0)

    class Meta:
        verbose_name = _("income amount")
        verbose_name_plural = _("income amounts")


class IncomeDebt(IncomeAmount):
    debt = models.OneToOneField(Income, on_delete=models.CASCADE, verbose_name=_("debt"))

    class Meta:
        verbose_name = _("income debt")
        verbose_name_plural = _("income debts")


class ClientDebt(General):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("client"))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.type = General.CLIENT_DEBT
        super(ClientDebt, self).save(force_insert, force_update,
                                     using, update_fields)

    class Meta:
        verbose_name = _("client debt")
        verbose_name_plural = _("client debts")


class ClientDeliveryDebt(ClientDebt):
    debt = models.OneToOneField(Delivery, on_delete=models.CASCADE, verbose_name=_("debt"))

    class Meta:
        verbose_name = _("client debt for delivery")
        verbose_name_plural = _("client debts for delivery")


class ClientInvoiceDebt(ClientDebt):
    debt = models.OneToOneField(Invoice, on_delete=models.CASCADE, verbose_name=_("debt"))

    class Meta:
        verbose_name = _("client debt for invoice")
        verbose_name_plural = _("client debts for invoice")


class SellDebt(General):
    debt = models.OneToOneField(Sell, on_delete=models.CASCADE, verbose_name=_("debt"))

    @property
    def debt_amount(self):
        total = SellDebt.objects.aggregate(total=Coalesce(Sum('total'), 0))
        amount = SellDebt.objects.aggregate(amount=Coalesce(Sum('amount'), 0))
        return total.get('total', 0) - amount.get('amount', 0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.type = General.SELL_DEBT
        super(SellDebt, self).save(force_insert, force_update,
                                   using,update_fields)

    class Meta:
        verbose_name = _("sell debt")
        verbose_name_plural = _("sell debts")


class Part(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    def __unicode__(self):
        return '%s %12.2f' % (self.name, self.price)

    class Meta:
        verbose_name = _("part")
        verbose_name_plural = _("parts")


class Store(models.Model):
    part = models.OneToOneField(Part, on_delete=models.CASCADE)
    p_income = models.IntegerField(default=0)
    p_outgo = models.IntegerField(default=0)
    p_sell = models.IntegerField(default=0)
    p_count = models.IntegerField(default=0)
    s_sum = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    m_timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s %f" % (self.part.name, self.part.price)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.p_count = self.p_income - self.p_outgo - self.p_sell
        self.s_sum = self.p_count * self.part.price
        super(Store, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("part on store")
        verbose_name_plural = _("parts on store")


class MainSell(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='%(class)s')
    p_count = models.IntegerField(default=0)
    total = models.DecimalField(default=0, max_digits=14, decimal_places=2)
    v_date = models.DateField(default=datetime.date.today)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s %12.2f' % (self.part, self.total)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.total = self.p_count * self.part.price

        super(MainSell, self).save(force_insert, force_update, using)


class StoreIncome(MainSell):
    parent = models.ForeignKey(Income, on_delete=models.CASCADE)


class InvoiceOut(MainSell):
    parent = models.ForeignKey(Invoice, on_delete=models.CASCADE)


class DeliveryPart(MainSell):
    parent = models.ForeignKey(Delivery, on_delete=models.CASCADE)


class StoreSell(MainSell):
    parent = models.ForeignKey(Sell, on_delete=models.CASCADE)


#ToDo total field read only