from django.contrib import admin

from store.models import Part, StoreIncome, Store, InvoiceOut, StoreSell, Sell, Cash, Invoice, Delivery, Client


class StoreSaleInline(admin.TabularInline):
    model = StoreSell


class StoreOutComeInline(admin.TabularInline):
    model = InvoiceOut


class SellAdmin(admin.ModelAdmin):
    inlines = [StoreSaleInline]


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [StoreOutComeInline]


admin.site.register(Part)
admin.site.register(Store)
admin.site.register(StoreIncome)
admin.site.register(InvoiceOut)
admin.site.register(StoreSell)
admin.site.register(Sell, SellAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Client)
admin.site.register(Cash)
admin.site.register(Delivery)
