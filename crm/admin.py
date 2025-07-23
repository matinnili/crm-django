from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter
from .models import Agent, Customer, Call,AiCallAnalysis,Ticket, TicketReply, Order,OrderItem,product,Warranty,WarrantyClaim
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
import math
import pandas as pd
from django.db import models


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
        return [("Answered", "Answered"),
                ("Missed", "Missed"),
                ("Voicemail", "Voicemail"),
                ("Busy", "Busy"),
                ("Failed", "Failed")

        ]

    def queryset(self, request, queryset):
        if self.value() == 'Answered':
            return queryset.filter(call_status='Answered')
        elif self.value() == 'Missed':
            return queryset.filter(call_status='Missed')
        elif self.value() == 'Voicemail':
            return queryset.filter(call_status='Voicemail')
        elif self.value() == 'Busy':
            return queryset.filter(call_status='Busy')
        elif self.value() == 'Failed':
            return queryset.filter(call_status='Failed')

        return queryset
class Sentimentfilter(SimpleListFilter):
    title = 'sentiment'
    parameter_name = 'sentiment'

    def lookups(self, request, model_admin):
        return [
            ('Positive', 'Positive'),
            ('Neutral', 'Neutral'),
            ('Negative', 'Negative'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Positive':
            return queryset.filter(sentiment='Positive')
        elif self.value() == 'Neutral':
            return queryset.filter(sentiment='Neutral')
        elif self.value() == 'Negative':
            return queryset.filter(sentiment='Negative')

        return 
class TicketReplyInline(admin.TabularInline):
    model = TicketReply
class OrderItemInline(admin.TabularInline):
    model = OrderItem
class AnalysisInline(admin.TabularInline):
    model= AiCallAnalysis

class CallInline(admin.TabularInline):
    model = Call
class OrderInline(admin.TabularInline):
    model = Order
    

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
    search_fields=["notes"]
    list_filter = [IntervalGroup,Purposefilter,Statusfilter,  ("call_start_time",RangeDateFilter)]
    inlines=[AnalysisInline]


    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        # call_durations = [[math.floor(i.call_duration.total_seconds()/60),i.call_start_time.day\
        # ,i.call_start_time.month,i.call_start_time.year] for i in Call.objects.all()]
        # print(f"-----------------this is call_durations{call_durations}")
        
        qs = self.get_queryset(request)
        objects=Call.objects.filter(call_status="Answered")
        # print(f"----------this is list{[object.call_duration for object in objects]}")
        # calls_number=len(objects)
        # print(f"----------this is type{type((objects[0].call_duration))}")        # Get selected month from GET
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
        # today = datetime.datetime.today()
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
        grouped_qs = (
        qs.annotate(day=TruncDay('call_start_time'))
          .values('day', 'call_purpose')
          .annotate(total=Count('call_id'))
          .order_by('day')
    )
        grouped_bar_status= (
            qs.annotate(day=TruncDay('call_start_time'))
            .values('day', 'call_status')
            .annotate(total=Count('call_id'))
            .order_by('day')
        )
        # print(f"-----------------this is grouped_qs{grouped_qs}")
        # print(f"-----------------this is grouped_bar_status{grouped_bar_status}")

    # Process data into structure suitable for Chart.js
        from collections import defaultdict
        import datetime

        day_labels = sorted({entry['day'].date() for entry in grouped_qs})
        purposes = list({entry['call_purpose'] for entry in grouped_qs})
        statuses = list({entry['call_status'] for entry in grouped_bar_status})

    # Map: purpose -> day -> count
        data_map = {purpose: {day: 0 for day in day_labels} for purpose in purposes}
        for entry in grouped_qs:
            day = entry['day'].date()
            purpose = entry['call_purpose']
            data_map[purpose][day] = entry['total']
        data_map_status = {status: {day: 0 for day in day_labels} for status in statuses}
        for entry in grouped_bar_status:
            day = entry['day'].date()
            status = entry['call_status']
            data_map_status[status][day] = entry['total']

        datasets = []
        colors = ["#4dc9f6", "#f67019", "#f53794", "#537bc4", "#acc236"]
        colors_status = ["#4dc9f6", "#f67019", "#f53794", "#537bc4", "#acc236"]
        for i, purpose in enumerate(purposes):
            datasets.append({
                "label": purpose,
                "data": [data_map[purpose][day] for day in day_labels],
                "backgroundColor": colors[i % len(colors)]
            })
        datasets_status = []
        for i, status in enumerate(statuses):
            datasets_status.append({
                "label": status,
                "data": [data_map_status[status][day] for day in day_labels],
                "backgroundColor": colors_status[i % len(colors_status)]
            })


        extra_context.update({
            "bar_chart_labels": [day.strftime("%Y-%m-%d") for day in day_labels],
            "bar_chart_datasets": datasets,
        })
        extra_context.update({
            "bar_chart_labels_status": [day.strftime("%Y-%m-%d") for day in day_labels],
            "bar_chart_datasets_status": datasets_status,
        })

        grouped_purpose = (
            qs.values('call_purpose')
              .annotate(percentage=Count('call_id'))
              .order_by('percentage')
        )
        
        grouped_status = (
            qs.values('call_status')
              .annotate(percentage=Count('call_id'))
              .order_by('percentage')
        )
        # print(f"-----------this is grouped purpose {grouped_status[0]}")
        # print(f"---------this is len_qs{len(qs)}")
        grouped_date = (
        qs.annotate(period=trunc('call_start_time'))
          .values('period')
          .annotate(total=Count('call_id'))
          .order_by('period')
    )

        chart_labels = [entry['call_purpose'] for entry in grouped_purpose]
        chart_data = [entry['percentage'] for entry in grouped_purpose]
        print(f"---------------this is chart data{chart_data}")
        chart_labels_status = [entry['call_status'] for entry in grouped_status]
        chart_data_status = [entry['percentage'] for entry in grouped_status]
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


@admin.register(Agent, Customer)
class CustomAdminClass(ModelAdmin):
    # list_display=('email','phone_number')
    inlines = [CallInline,OrderInline]
    change_form_template = 'admin/agent_change_view.html'
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        agent = Agent.objects.get(agent_id=object_id)
        calls= Call.objects.filter(agent_id=object_id)
        qs=calls.values("call_purpose").annotate(total=Count('call_id')).order_by('call_purpose')
        labels= [entry['call_purpose'] for entry in qs]
        data= [entry['total'] for entry in qs]
        extra_context.update({
            'chart_labels': labels,
            'chart_data': data,
        })
        extra_context['agent'] = agent
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

@admin.register(AiCallAnalysis)
class AiCallAnalysisAdmin(ModelAdmin):
    list_display = ('call', 'sentiment')
    list_filter = [("call__call_start_time",RangeDateFilter)]
    search_fields = ('call__customer_id__first_name', 'call__customer_id__last_name', 'call__agent_id__first_name', \
    'call__agent_id__last_name',"keywords")
    change_list_template = "admin/change_ai_analysis_list.html"
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        self.queryset = qs
        # Get the selected month from GET parameters
        sentiment = request.GET.get('sentiment')
        if sentiment:
            self.queryset = self.queryset.filter(sentiment=sentiment)
        sentiment_grouped = (
            self.queryset.values('sentiment')
            .annotate(total=Count('analysis_id'))
            .order_by('sentiment')
        )
        sentiment_grouped_bar= (
        qs.annotate(day=TruncDay('call__call_start_time'))
          .values('day', 'sentiment')
          .annotate(total=Count('call__call_id'))
          .order_by('day')
    )
        from collections import defaultdict
        import datetime

        day_labels = sorted({entry['day'].date() for entry in sentiment_grouped_bar})
        sentiments = list({entry['sentiment'] for entry in sentiment_grouped_bar})
        # Map: sentiment -> day -> count
        data_map = {sentiment: {day: 0 for day in day_labels} for sentiment in sentiments}
        for entry in sentiment_grouped_bar:
            day = entry['day'].date()
            sentiment = entry['sentiment']
            data_map[sentiment][day] = entry['total']   
        datasets = []
        colors = ["#4dc9f6", "#f67019", "#f53794", "#537bc4", "#acc236"]
        for i, sentiment in enumerate(sentiments):
            datasets.append({
                "label": sentiment,
                
                "data": [data_map[sentiment][day] for day in day_labels],
                "backgroundColor": colors[i % len(colors)]
            })      
        print(f"datasets: {datasets}")
        extra_context.update({
            "bar_chart_labels": [day.strftime("%Y-%m-%d") for day in day_labels],
            "bar_chart_datasets": datasets,
        })
        # Prepare data for the chart

        chart_labels = [entry['sentiment'] for entry in sentiment_grouped]
        chart_data = [entry['total'] for entry in sentiment_grouped]
        extra_context.update({
            'chart_labels': chart_labels,
            'chart_data': chart_data,
        })


        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('call', 'call__customer_id', 'call__agent_id')
    
# Register your models here.


    
    
@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('ticket_id', 'customer', 'aasigned_agent', 'subject', 'status', 'priority', 'source', 'created_at')
    list_filter = ('status', 'priority', 'source', ('created_at', RangeDateTimeFilter))
    search_fields = ('subject', 'customer__first_name', 'customer__last_name')
    inlines = [TicketReplyInline]
@admin.register(TicketReply)
class TicketReplyAdmin(ModelAdmin):
    list_display = ('reply_id', 'ticket', 'agent', 'customer', 'body', 'is_internal', 'created_at')
    list_filter = ('is_internal', ('created_at', RangeDateTimeFilter))
    search_fields = ('body', 'ticket__subject', 'agent__first_name', 'agent__last_name')
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id', 'customer', 'agent', 'order_date', 'total_amount', 'oredr_status', 'created_at')
    list_filter = ('oredr_status', ('order_date', RangeDateTimeFilter))
    search_fields = ('customer__first_name', 'customer__last_name', 'agent__first_name', 'agent__last_name')
    Inlines = [OrderItemInline]
@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ('order_item_id', 'order', 'product_name', 'quantity', 'unit_price')
    list_filter = ('order__customer__first_name', 'order__customer__last_name')
    search_fields = ('product_name', 'order__customer__first_name', 'order__customer__last_name')
@admin.register(product)
class ProductAdmin(ModelAdmin):
    list_display = ('product_id', 'name', 'description', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    Inlines = [OrderItemInline]
@admin.register(Warranty)
class WarrantyAdmin(ModelAdmin):
    list_display = ('warranty_id', 'product_id', 'start_date', 'end_date', 'status')
    list_filter = ('status', ('start_date', RangeDateTimeFilter), ('end_date', RangeDateTimeFilter))
    search_fields = ('product__name', 'status')
@admin.register(WarrantyClaim)
class WarrantyClaimAdmin(ModelAdmin):
    list_display = ('claim_id', 'warranty_id', 'customer_id', 'product_id', 'claim_date', 'reported_issue', 'resolution_type', 'resolved_by_agent_id', 'closed_at')
    list_filter = ('resolution_type', ('claim_date', RangeDateTimeFilter), ('closed_at', RangeDateTimeFilter))
    search_fields = ('customer_id__first_name', 'customer_id__last_name', 'product_id__name', 'reported_issue')




