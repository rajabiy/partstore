from crudbuilder.abstract import BaseCrudBuilder

from store.models import Store


class StoreCrud(BaseCrudBuilder):
    model = Store
    #search_feilds = ['name']
    #tables2_fields = ('name', 'email')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20
