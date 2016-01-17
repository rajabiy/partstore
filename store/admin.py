# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.decorators import register
from django.utils.translation import ugettext_lazy as _

from store.models import Part, StoreIncome, Store, InvoiceOut, StoreSell, Sell, General, Invoice, Delivery, Client, \
    DeliveryPart, Income, ClientDebt, ClientDeliveryDebt, ClientInvoiceDebt, IncomeDebt, DeliveryDebt, SellDebt, \
    IncomeAmount, DeliveryAmount


class StoreSaleInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    model = StoreSell


class InvoiceOutInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    model = InvoiceOut


class StoreIncomeInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
    model = StoreIncome


class ClientDebtInline(admin.TabularInline):
    fields = ('total', 'amount', 'v_date',)
    readonly_fields = ('total',)
    exclude = ('type',)
    list_display = ('client', 'v_date', 'total', 'amount',)
    model = ClientDebt


class DeliveryPartInline(admin.TabularInline):
    readonly_fields = ('total', 'v_date',)
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


#@register(General)
class GeneralAdmin(admin.ModelAdmin):
    readonly_fields = ('total', 'amount', 'type', 'v_date')
    date_hierarchy = 'v_date'
    list_display = ('type', 'v_date', 'total', 'amount', 'v_date',)

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        elif hasattr(obj, 'deliverydebt') or hasattr(obj, 'incomedebt') or hasattr(obj, 'clientdebt'):
            return False
        else:
            return True


@register(ClientDebt)
class ClientDebtAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (('client', 'v_date',), 'amount', ), }),
    )
    readonly_fields = ('total',)
    date_hierarchy = 'v_date'
    exclude = ('type',)
    list_display = ('client', 'v_date', 'total', 'amount',)

#@register(ClientDeliveryDebt, ClientInvoiceDebt)
class ClientDebtAdmin(admin.ModelAdmin):
    readonly_fields = ('total', 'amount', 'type', 'v_date', 'debt', 'client', )
    date_hierarchy = 'v_date'
    list_display = ('client', 'v_date', 'debt', 'total', 'amount', 'v_date',)

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        elif obj.debt_id:
            return False
        else:
            return True

    def has_add_permission(self, request):
        return False


#@register(IncomeDebt, DeliveryDebt)
class MyDebtAdmin(admin.ModelAdmin):
    readonly_fields = ('v_date', 'debt', 'total', 'amount',)
    date_hierarchy = 'v_date'
    list_display = ('v_date', 'debt', 'total', 'amount',)

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        elif obj.debt_id:
            return False
        else:
            return True

    def has_add_permission(self, request):
        return False


@register(IncomeAmount, DeliveryAmount, SellDebt)
class IncomeAmountAdmin(admin.ModelAdmin):
    readonly_fields = ('total', 'type', 'debt_amount')
    list_display = ('v_date', 'total', 'amount',)
    date_hierarchy = 'v_date'
    readonly_fields = ('debt_amount', )

#todo пагинация в инлайнах
#todo ссылка в инлайнах клиентов
#todo Сворачивание инлайнов