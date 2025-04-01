import django_filters
from django.db.models import Min, Max
from ..models import Offer


class OfferFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(method='filter_min_price', label="Mindestpreis")
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time', label="Maximale Lieferzeit")
    creator_id = django_filters.NumberFilter(method='filter_creator_id', label="Ersteller-ID")

    class Meta:
        model = Offer
        fields = ['user']

    def filter_min_price(self, queryset, name, value):
        return queryset.annotate(min_price=Min('details__price')).filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        return queryset.annotate(max_delivery_time=Max('details__delivery_time_in_days')).filter(max_delivery_time__lte=value)

    def filter_creator_id(self, queryset, name, value):
        return queryset.filter(user__id=value)
