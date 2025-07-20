from django.db import models



class CallStatus(models.TextChoices):
    Answered = 'a', 'Answered'
    Missed = 'm', 'Missed'
    Voicemail = 'v', 'Voicemail'
    Busy = 'b', 'Busy'
    Failed = 'f', 'Failed'

class CallPurpose(models.TextChoices):
    PriceInquiry = 'pi', 'Price Inquiry'
    WarrantyClaim = 'wc', 'Warranty Claim'

class Role(models.TextChoices):
    Agent = 'a', 'Agent'
    Supervisor = 's', 'Supervisor'
    admin = 'm', 'Manager'

class Sentiment(models.TextChoices):
    Positive = 'positive', 'Positive'
    Neutral = 'neutral', 'Neutral'
    Negative = 'negative', 'Negative'


class Agent(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role= models.CharField(max_length=20, choices=Role.choices)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True,null=False)
    role= models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
   
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True,null=False)
    role= models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Call(models.Model):
    call_id = models.AutoField(primary_key=True)
    customer_id= models.ForeignKey(Customer, on_delete=models.CASCADE)
    agent_id = models.ForeignKey(Agent, on_delete=models.CASCADE)
    call_start_time=models.DateTimeField(auto_now_add=True)
    call_end_time=models.DateTimeField(auto_now=True)
    call_duration=models.DurationField()
    call_status= models.CharField(CallStatus.choices, max_length=10)
    call_purpose = models.CharField(CallPurpose.choices, max_length=10)
    call_purpose = models.CharField(max_length=250)
    notes = models.TextField(blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Call {self.call_id} - Agent {self.agent_id} ({self.call_start_time} to {self.call_end_time})"

class AiCallAnalysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name='ai_analysis')
    sentiment=models.CharField(Sentiment.choices, max_length=10)
    keywords = models.TextField()
    action_items = models.TextField()
    analysis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.analysis_id} for Call {self.call.call_id}"


