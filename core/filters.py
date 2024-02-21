from django_filters.rest_framework import FilterSet
from .models import Foods


class FoodFilter(FilterSet):
    class Meta:
        model = Foods
        fields = {
            'collection_id': ['exact'],
            'price': ['gt', 'lt'],

        }