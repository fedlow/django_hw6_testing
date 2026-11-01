import django_filters
from django.utils import timezone
from datetime import timedelta
from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    skills = django_filters.CharFilter(lookup_expr="icontains")
    min_tenure = django_filters.NumberFilter(method="filter_by_tenure")

    class Meta:
        model = Employee
        fields = ["skills"]

    def filter_by_tenure(self, queryset, name, value):
        cutoff_date = timezone.now().date() - timedelta(days=int(value))
        return queryset.filter(hire_date__lte=cutoff_date)