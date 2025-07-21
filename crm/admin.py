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
import datetime



class TimeIntervalFilter(SimpleListFilter):
    title = 'month_filter'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        today = datetime.datetime.today()
        months = []
        for i in range(12):
            dt = today.replace(day=1) - datetime.timedelta(days=i*30)
            key = dt.strftime('%Y-%m')
            label = dt.strftime('%B %Y')
            months.append((key, label))
        return months

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

        # Get selected month from GET
        selected_month = request.GET.get('month')
        # selected_month = request.GET.get('month')
        print(selected_month)

        # Calculate the last 12 months
        today = datetime.datetime.today()
        months = []
        for i in range(12):
            dt = today.replace(day=1) - datetime.timedelta(days=i*30)
            key = dt.strftime('%Y-%m')
            label = dt.strftime('%B %Y')
            months.append((key, label))

        # Apply month filter
        qs = self.get_queryset(request)
        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                start = datetime(year, month, 1)
                if month == 12:
                    end = datetime(year + 1, 1, 1)
                else:
                    end = datetime(year, month + 1, 1)
                qs = qs.filter(call_start_time__gte=start, call_end_time__lt=end)
            except:
                pass

        # Group by call_purpose
        grouped = (
            qs.values('call_purpose')
              .annotate(total=Count('call_id'))
              .order_by('-total')
        )

        chart_labels = [entry['call_purpose'] for entry in grouped]
        chart_data = [entry['total'] for entry in grouped]

        extra_context.update({
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'selected_month': selected_month,
            'month_choices': months,
        })

        # extra_context = extra_context or {}

        # Read filter values from request.GET
        # interval = request.GET.get('interval', 'month')
        # chart_type = request.GET.get('chart', 'bar')

        # # Choose grouping function
        # from django.db.models.functions import TruncDay, TruncMonth, TruncYear
        # from django.db.models import Count

        # if interval == 'day':
        #     trunc = TruncDay
        # elif interval == 'year':
        #     trunc = TruncYear
        # else:
        #     trunc = TruncMonth

        # qs = self.get_queryset(request)
        # grouped = (
        #     qs.annotate(period=trunc('call_start_time'))
        #       .values('period')
        #       .annotate(total=Count('call_id'))
        #       .order_by('period')
        # )

        # Format chart data
        # if interval == 'day':
        #     labels = [entry['period'].strftime('%Y-%m-%d') for entry in grouped]
        # elif interval == 'year':
        #     labels = [entry['period'].strftime('%Y') for entry in grouped]
        # else:
        #     labels = [entry['period'].strftime('%B %Y') for entry in grouped]
 
        # extra_context.update({
        #    'chart_labels': labels,
        #     'chart_data': [entry['total'] for entry in grouped],
        #     'selected_chart': chart_type,
        #     'selected_interval': interval,
        # })

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Agent,Customer)
class CustomAdminClass(ModelAdmin):
    list_display=('email','phone_number')
    
# Register your models here.

