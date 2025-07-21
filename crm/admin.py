from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter
from .models import Agent, Customer, Call,AiCallAnalysis
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Count, ExpressionWrapper, DurationField, F, FloatField
from django.db.models.functions import ExtractSecond, ExtractMinute, ExtractHour, Extract

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
admin.site.unregister(User)
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter

from django.db.models.functions import TruncMonth,TruncDay, TruncYear
from django.db.models import Count
import json
from django.contrib.admin import SimpleListFilter
import datetime



# class TimeIntervalFilter(SimpleListFilter):
#     title = 'month_filter'
#     parameter_name = 'month'

#     def lookups(self, request, model_admin):
#         today = datetime.datetime.today()
#         months = []
#         for i in range(12):
#             dt = today.replace(day=1) - datetime.timedelta(days=i*30)
#             key = dt.strftime('%Y-%m')
#             label = dt.strftime('%B %Y')
#             months.append((key, label))
#         return months

#     def queryset(self, request, queryset):

#         return queryset

class IntervalGroup(SimpleListFilter):
    title = 'group_by'
    parameter_name = 'interval'

    def lookups(self, request, model_admin):
        return [
            ('day', 'Day'),
            ('month', 'Month'),
            ('year', 'Year'),
        ]

    def queryset(self, request, queryset):
        return queryset

class Purposefilter(SimpleListFilter):
    title = 'call_purpose'
    parameter_name = 'call_purpose'

    def lookups(self, request, model_admin):
        return [
            ('Price Inquiry', 'Price Inquiry'),
            ('Warranty Claim', 'Warranty Claim'),
        ]

    def queryset(self, request, queryset):  
        if self.value() == 'Price Inquiry':
            return queryset.filter(call_purpose='Price Inquiry')
        elif self.value() == 'Warranty Claim':
            return queryset.filter(call_purpose='Warranty Claim')

        return queryset

class Statusfilter(SimpleListFilter):
    title = 'call_status'
    parameter_name = 'call_status'

    def lookups(self, request, model_admin):
        return [("a", "Answered"),
                ("m", "Missed"),
                ("v", "Voicemail"),
                ("b", "Busy"),
                ("f", "Failed")

        ]

    def queryset(self, request, queryset):
        if self.value() == 'a':
            return queryset.filter(call_status='a')
        elif self.value() == 'm':
            return queryset.filter(call_status='m')
        elif self.value() == 'v':
            return queryset.filter(call_status='v')
        elif self.value() == 'b':
            return queryset.filter(call_status='b')
        elif self.value() == 'f':
            return queryset.filter(call_status='f')

        return queryset

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Call)
class CallAdmin(ModelAdmin):
    list_display=("call_start_time","call_end_time","call_duration")
    list_filter_submit = True  # Submit button at the bottom of the filter
    change_list_template = "admin/change_call_list.html"
    list_filter = [IntervalGroup,Purposefilter,Statusfilter,  ("call_start_time",RangeDateFilter)]

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        objects=Call.objects.all()
        print(f"----------this is type{type((objects[0].call_duration))}")        # Get selected month from GET
        selected_month = request.GET.get('month')
        purpose= request.GET.get('call_purpose')
        status= request.GET.get('call_status')
        interval= request.GET.get('interval')
        date_start=request.GET.get('call_start_time_from')
        if date_start:
            qs=qs.filter(call_start_time__gte=date_start)
        
        print(f"-----------------this is date_start{date_start}")
        date_end=request.GET.get('call_start_time_to')
        if date_end:
            qs=qs.filter(call_start_time__lte=date_end)
        print(f"-----------------this is date_end{date_end}")
        if interval == 'month':
            trunc = TruncMonth
        elif interval == 'year':
            trunc = TruncYear
        else:
            trunc = TruncDay

        print(selected_month)

        # Calculate the last 12 months
        today = datetime.datetime.today()
        # months = []
        # for i in range(12):
        #     dt = today.replace(day=1) - datetime.timedelta(days=i*30)
        #     key = dt.strftime('%Y-%m')
        #     label = dt.strftime('%B %Y')
        #     months.append((key, label))
        # qs_with_duration = qs.annotate(
        #     duration_minutes=F("call_end_time") - F("call_start_time")
        # ).values("duration_minutes").annotate(seconds=Extract('duration_minutes', 'epoch')).values("seconds")
        # print(f"-----------------this is duration{qs_with_duration}")

# Round down to nearest minute for grouping
        # from django.db.models.functions import Floor
        # qs_with_duration = qs_with_duration.annotate(
        #     minutes=Extract('duration_minutes','epoch')).values("minutes")
        
        # print(f"-----------------this is duration{qs_with_duration}")
        


# Group by rounded duration in minutes
        

# )
        # Apply month filter
        
        # if selected_month:
        #     print("--------------------hi")
        #     try:
        #         year, month = map(int, selected_month.split('-'))
        #         start = datetime.datetime(year, month, 1)
        #         if month == 12:
        #             end = datetime.datetime(year + 1, 1, 1)
        #         else:
        #             end = datetime.datetime(year, month + 1, 1)
        #         print("--------------------hi")
        #         qs = qs.filter(call_start_time__gte=start, call_end_time__lt=end)
        #         print([i for i in qs])
        #     except Exception as e:
        #         print(f"Error parsing month: {e}")
        if purpose:
            qs = qs.filter(call_purpose=purpose)
            print(f"Filtered by purpose: {qs}")
        if status:
            qs = qs.filter(call_status=status)
            print(f"Filtered by status: {len(qs)}")

        # Group by call_purpose
        grouped_purpose = (
            qs.values('call_purpose')
              .annotate(total=Count('call_id'))
              .order_by('total')
        )
        grouped_status = (
            qs.values('call_status')
              .annotate(total=Count('call_id'))
              .order_by('total')
        )
        grouped_date = (
        qs.annotate(period=trunc('call_start_time'))
          .values('period')
          .annotate(total=Count('call_id'))
          .order_by('period')
    )

        chart_labels = [entry['call_purpose'] for entry in grouped_purpose]
        chart_data = [entry['total'] for entry in grouped_purpose]
        chart_labels_status = [entry['call_status'] for entry in grouped_status]
        chart_data_status = [entry['total'] for entry in grouped_status]
        chart_labels_date = [entry['period'].strftime('%Y-%m') for entry in grouped_date]
        chart_data_date = [entry['total'] for entry in grouped_date]
        # line_labels = [int(entry['rounded_minutes']) for entry in distribution]
        # line_data = [entry['count'] for entry in distribution]


        extra_context.update({
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'chart_labels_status': chart_labels_status,
            'chart_data_status': chart_data_status,
            'chart_labels_date': chart_labels_date,
            'chart_data_date': chart_data_date,
            'selected_month': selected_month,
            # 'month_choices': months,
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
@admin.register(AiCallAnalysis)
class AiCallAnalysisAdmin(ModelAdmin):
    list_display = ('call', 'sentiment')
    list_filter = [("call__call_start_time",RangeDateFilter)]
    search_fields = ('call__customer_id__first_name', 'call__customer_id__last_name', 'call__agent_id__first_name', 'call__agent_id__last_name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('call', 'call__customer_id', 'call__agent_id')
    
# Register your models here.

