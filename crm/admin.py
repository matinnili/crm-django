from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from .models import Agent, Customer, Call
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
admin.site.unregister(User)
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter

from django.db.models.functions import TruncMonth
from django.db.models import Count
import json
from django.contrib.admin import SimpleListFilter



class TimeIntervalFilter(SimpleListFilter):
    title = 'Time Interval'
    parameter_name = 'interval'

    def lookups(self, request, model_admin):
        return [
            ('day', 'Day'),
            ('month', 'Month'),
            ('year', 'Year'),
        ]

    def queryset(self, request, queryset):
        return queryset

class ChartTypeFilter(SimpleListFilter):
    title = 'Chart Type'
    parameter_name = 'chart'

    def lookups(self, request, model_admin):
        return [
            ('bar', 'Bar'),
            ('pie', 'Pie'),
        ]

    def queryset(self, request, queryset):
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Call)
class CallAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    change_list_template = "admin/change_call_list.html"
    list_filter = [TimeIntervalFilter, ChartTypeFilter]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Read filter values from request.GET
        interval = request.GET.get('interval', 'month')
        chart_type = request.GET.get('chart', 'bar')

        # Choose grouping function
        from django.db.models.functions import TruncDay, TruncMonth, TruncYear
        from django.db.models import Count

        if interval == 'day':
            trunc = TruncDay
        elif interval == 'year':
            trunc = TruncYear
        else:
            trunc = TruncMonth

        qs = self.get_queryset(request)
        grouped = (
            qs.annotate(period=trunc('call_start_time'))
              .values('period')
              .annotate(total=Count('call_id'))
              .order_by('period')
        )

        # Format chart data
        if interval == 'day':
            labels = [entry['period'].strftime('%Y-%m-%d') for entry in grouped]
        elif interval == 'year':
            labels = [entry['period'].strftime('%Y') for entry in grouped]
        else:
            labels = [entry['period'].strftime('%B %Y') for entry in grouped]

        extra_context.update({
            'chart_labels': labels,
            'chart_data': [entry['total'] for entry in grouped],
            'selected_chart': chart_type,
            'selected_interval': interval,
        })

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Agent)
class CustomAdminClass(ModelAdmin):
    pass
# Register your models here.

