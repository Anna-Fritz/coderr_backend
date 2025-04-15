import django_filters
from django.db.models import Min
from ..models import Offer


class OfferFilter(django_filters.FilterSet):
    """
    Custom filter set for filtering `Offer` objects based on various criteria.
    """
    min_price = django_filters.NumberFilter(method='filter_min_price', label="Mindestpreis")
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time', label="Maximale Lieferzeit")
    creator_id = django_filters.NumberFilter(method='filter_creator_id', label="Ersteller-ID")

    class Meta:
        model = Offer
        fields = ['user']

    def filter_min_price(self, queryset, name, value):
        """
        Filters the offers to only include those with a price greater than or equal to the specified minimum price.
        """
        return queryset.annotate(min_price=Min('details__price')).filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filters the offers to only include those with a maximum delivery time less than or equal to the specified value.
        """
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

    def filter_creator_id(self, queryset, name, value):
        """
        Filters the offers to only include those created by a specific user, identified by the `creator_id` (user ID).
        """
        return queryset.filter(user__id=value)
