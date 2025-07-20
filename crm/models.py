from django.db import models


class customer(models.Model):


class Call(models):
    call_id = models.AutoField(primary_key=True)
    customer_id= models.IntegerField(primary_key=True)
    agent_id = models.IntegerField(primary_key=True)
    call_start_time=models.DateTimeField(auto_now_add=True)
    call_end_time=models.DateTimeField(auto_now=True)
    call_duration=models.DurationField()
    call_status= models.CharField(CallStatus.choices, max_length=10)
    call_purpose = models.CharField(CallPurpose.choices, max_length=10)
    call_purpose = models.varcharField(max_length=250)
    notes = models.TextField(blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Call {self.call_id} - Agent {self.agent_id} ({self.call_start_time} to {self.call_end_time})"

class AiCallAnalysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name='ai_analysis')
    sentiment_score = models.En
    keywords = models.TextField()
    action_items = models.TextField()
    analysis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.analysis_id} for Call {self.call.call_id}"


class CallStatus(models.TextChoices):
    Answered = 'a', 'Answered'
    Missed = 'm', 'Missed'
    Voicemail = 'v', 'Voicemail'
    Busy = 'b', 'Busy'
    Failed = 'f', 'Failed'

class CallPurpose(models.TextChoices):
    PriceInquiry = 'pi', 'Price Inquiry'
    WarrantyClaim = 'wc', 'Warranty Claim'