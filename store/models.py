from __future__ import unicode_literals

import datetime

from django.db import models


class AbstractInvoice(models.Model):
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    debt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    v_date = models.DateField(default=datetime.date.today)
    memo = models.TextField(blank=True, null=True)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.debt = self.total - self.discount - self.amount

        super(AbstractInvoice, self).save()


class Client(models.Model):
    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=45, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    inv_debt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    del_debt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cash = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    photo = models.ImageField(blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.name, self.saldo)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.saldo = self.inv_debt +self.del_debt - self.cash

        super(Client, self).save(force_insert, force_update,
                                 using, update_fields)


class Invoice(AbstractInvoice):
    client = models.ForeignKey(Client)

    class Meta(AbstractInvoice.Meta):
        db_table = 'store_invoice'


class Delivery(AbstractInvoice):
    client = models.ForeignKey(Client)

    class Meta(AbstractInvoice.Meta):
        db_table = 'store_delivery'


class Sell(AbstractInvoice):

    class Meta(AbstractInvoice.Meta):
        db_table = 'store_sell'


class Part(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    def __unicode__(self):
        return '%s %12.2f' % (self.name, self.price)


class Store(models.Model):
    part = models.OneToOneField(Part)
    p_income = models.IntegerField(default=0)
    by_inv_count = models.IntegerField(default=0)
    sell_count = models.IntegerField(default=0)
    p_count = models.IntegerField(default=0)
    s_sum = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    m_timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s %f" % (self.part.name, self.part.price)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.p_count = self.p_income - self.by_inv_count - self.sell_count
        self.s_sum = self.p_count * self.part.price
        super(Store, self).save(force_insert, force_update, using, update_fields)


class StoreIncome(models.Model):
    part = models.ForeignKey(Part)
    p_count = models.IntegerField(default=0)
    v_date = models.DateField(default=datetime.date.today)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s %f' % (self.part, self.p_count)


class AbstractSell(models.Model):
    part = models.ForeignKey(Part, related_name='%(class)s')
    p_count = models.IntegerField(default=0)
    total = models.DecimalField(default=0, max_digits=14, decimal_places=2)
    v_date = models.DateField(default=datetime.date.today)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s %12.2f' % (self.part, self.total)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.total = self.p_count * self.part.price

        super(AbstractSell, self).save(force_insert, force_update, using)


class InvoiceOut(AbstractSell):
    sell = models.ForeignKey(Invoice)

    class Meta:
        db_table = 'store_invoice_out'


class DeliveryPart(AbstractSell):
    sell = models.ForeignKey(Delivery)

    class Meta:
        db_table = 'store_delivery_part'


class StoreSell(AbstractSell):
    sell = models.ForeignKey(Sell)

    class Meta:
        db_table = 'store_store_sell'


class ClientCash(models.Model):
    client = models.ForeignKey(Client)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    v_date = models.DateField(default=datetime.date.today)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)


class Cash(models.Model):
    client = models.OneToOneField(Client, null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    v_date = models.DateField(default=datetime.date.today)
    v_timestamp = models.DateTimeField(auto_now_add=True)
    m_timestamp = models.DateTimeField(auto_now=True)



#ToDo total field read only