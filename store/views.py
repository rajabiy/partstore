from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum


from store.models import Store


class StoreTotals(ChangeList):

    def get_results(self, request):
        #totals = self.result_list.aggregate(
        super(StoreTotals, self).get_results(request)
        totals = self.model.objects.aggregate(
            parts_count=Sum('p_count'),
            parts_sum=Sum('s_sum'))
        self.totals = totals
