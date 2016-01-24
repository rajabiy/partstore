# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.decorators import register
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from store.models import Part, StoreIncome, Store, InvoiceOut, StoreSell, Sell, General, Invoice, Delivery, Client, \
    DeliveryPart, Income, ClientDebt, ClientDeliveryDebt, ClientInvoiceDebt, IncomeDebt, DeliveryDebt, SellDebt, \
    IncomeAmount, DeliveryAmount


class StoreSaleInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    ordering = ['-v_date']
    model = StoreSell


class InvoiceOutInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    ordering = ['-v_date']
    model = InvoiceOut


class StoreIncomeInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    ordering = ['-v_date']
    model = StoreIncome


class ClientDebtInline(admin.TabularInline):
    fields = ('total', 'amount', 'v_date', 'details_url',)
    readonly_fields = ('total', 'details_url')
    exclude = ('type',)
    list_display = ('client', 'v_date', 'total', 'amount', 'details_url',)
    ordering = ['-v_date']
    model = ClientDebt

    def details_url(self, obj=False):
        template = '<a href="%s?_to_field=id&_popup=1" onclick="return showAddAnotherPopup(this);">%s</a>'
        if hasattr(obj, 'clientdeliverydebt'):
            url = reverse_lazy('admin:%s_%s_change' % (obj.clientdeliverydebt.debt._meta.app_label,
                                                       obj.clientdeliverydebt.debt._meta.model_name),
                               args=(obj.clientdeliverydebt.debt.id,))
            return template % (url, _("details"))
        elif hasattr(obj, 'clientinvoicedebt'):
            url = reverse_lazy('admin:%s_%s_change' % (obj.clientinvoicedebt.debt._meta.app_label,
                                                       obj.clientinvoicedebt.debt._meta.model_name),
                               args=(obj.clientinvoicedebt.debt.id,))
            return template % (url, _("details"))
        else:
            return ''

    details_url.allow_tags = True
    details_url.short_description = _("details")


class DeliveryPartInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    ordering = ['-v_date']
    model = DeliveryPart


@register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('client', ('total', 'discount', 'debt',), ('v_date', 'amount',),),}),
        (_("memo"), {'classes': ('collapse',), 'fields': ('memo',)}),
    )

    readonly_fields = ('total', 'v_date', 'debt',)
    list_display = ('client', 'amount', 'total', 'discount', 'debt', 'v_date', 'memo',)
    date_hierarchy = 'v_date'
    ordering = ['-v_date']
    inlines = [DeliveryPartInline]

    
@register(Income)
class IncomeAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Price"), {'fields': (('total', 'discount', 'debt',), ('v_date', 'amount',),),}),
        (_("memo"), {'classes': ('collapse',), 'fields': ('memo',)}),
    )
    readonly_fields = ('total', 'v_date', 'debt',)
    list_display = ('amount', 'total', 'discount', 'debt', 'v_date', 'memo',)
    date_hierarchy = 'v_date'
    ordering = ['-v_date']
    inlines = [StoreIncomeInline]

    
@register(Sell)
class SellAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Price"), {'fields': (('total', 'discount', 'debt',), ('v_date', 'amount',),),}),
        (_("memo"), {'classes': ('collapse',), 'fields': ('memo',)}),
    )
    readonly_fields = ('total', 'v_date', 'debt',)
    list_display = ('amount', 'total', 'discount', 'debt', 'v_date', 'memo',)
    date_hierarchy = 'v_date'
    ordering = ['-v_date']
    inlines = [StoreSaleInline]


@register(Invoice)    
class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('client', ('total', 'discount', 'debt',), ('v_date', 'amount',),),}),
        (_("memo"), {'classes': ('collapse',), 'fields': ('memo',)}),
    )
    readonly_fields = ('total', 'v_date', 'debt',)
    list_display = ('client', 'debt', 'total', 'discount', 'amount', 'v_date', 'memo',)
    date_hierarchy = 'v_date'
    ordering = ['-v_date']
    inlines = [InvoiceOutInline]


@register(Store)
class StoreAdmin(admin.ModelAdmin):
    readonly_fields = ('p_income', 'p_outgo', 'p_sell', 'p_count', 's_sum', 'price')
    list_display = ('part', 'p_count', 'price', 's_sum')
    actions = ("update_counts", "update_all_counts",)

    def update_counts(self, request, queryset):
        for obj in queryset:
            obj.update_counts()

    update_counts.short_description = _("update part counts")

    def update_all_counts(self, request, queryset):
        all = Store.objects.all()
        for obj in all:
            obj.update_counts()

    update_all_counts.short_description = _("update all part counts")


@register(Part)
class PartAdmin(admin.ModelAdmin):
    fields = ('name', 'price')
    list_display = ('name', 'price')


@register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'phone', 'saldo',), }),
        (_("memo"), {'classes': ('collapse',), 'fields': (('memo', 'photo',), )}),
    )
    readonly_fields = ('saldo',)
    list_display = ('name', 'saldo', 'phone',)
    inlines = [ClientDebtInline]


@register(IncomeAmount, DeliveryAmount)
class IncomeAmountAdmin(admin.ModelAdmin):
    list_display = ('v_date', 'total', 'amount', 'details_url', 'debt_amount',)
    date_hierarchy = 'v_date'
    exclude = ('debt', 'type',)
    readonly_fields = ('total', 'debt_amount', 'details_url',)
    ordering = ['-v_date']

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        elif hasattr(obj, 'deliverydebt') or hasattr(obj, 'incomedebt'):
            return False
        else:
            return True

    def details_url(self, obj=False):
        template = '<a href="%s?_to_field=id&_popup=1" onclick="return showAddAnotherPopup(this);">%s</a>'
        if hasattr(obj, 'deliverydebt'):
            url = reverse_lazy('admin:%s_%s_change' % (obj.deliverydebt.debt._meta.app_label,
                                                       obj.deliverydebt.debt._meta.model_name),
                               args=(obj.deliverydebt.debt.id,))
            return template % (url, _("details"))
        elif hasattr(obj, 'incomedebt'):
            url = reverse_lazy('admin:%s_%s_change' % (obj.incomedebt.debt._meta.app_label,
                                                       obj.incomedebt.debt._meta.model_name),
                               args=(obj.incomedebt.debt.id,))
            return template % (url, _("details"))
        else:
            return ''

    details_url.allow_tags = True
    details_url.short_description = _("details")


@register(SellDebt)
class SellAmountAdmin(IncomeAmountAdmin):
    readonly_fields = ('total', 'debt_amount', 'v_date', 'amount', 'details_url',)

    def has_add_permission(self, request):
        return False

    def details_url(self, obj=False):
        template = '<a href="%s?_to_field=id&_popup=1" onclick="return showAddAnotherPopup(this);">%s</a>'
        if hasattr(obj, 'debt'):
            url = reverse_lazy('admin:%s_%s_change' % (obj.debt._meta.app_label,
                                                       obj.debt._meta.model_name),
                               args=(obj.debt.id,))
            return template % (url, _("details"))
        else:
            return ''

    details_url.allow_tags = True
    details_url.short_description = _("details")

#todo пагинация в инлайнах
#todo ссылка в инлайнах клиентов
#todo Сворачивание инлайнов