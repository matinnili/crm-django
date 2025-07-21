from django.db import models



class CallStatus(models.TextChoices):
    Answered = 'a', 'Answered'
    Missed = 'm', 'Missed'
    Voicemail = 'v', 'Voicemail'
    Busy = 'b', 'Busy'
    Failed = 'f', 'Failed'

class CallPurpose(models.TextChoices):
    PriceInquiry =  'Price Inquiry'
    WarrantyClaim =  'Warranty Claim'

class Role(models.TextChoices):
    Agent ='Agent'
    Supervisor = 'Supervisor'
    admin =  'Manager'

class Sentiment(models.TextChoices):
    Positive =  'Positive'
    Neutral =  'Neutral'
    Negative =  'Negative'


class Agent(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50,null=True)
    role= models.CharField(max_length=20, choices=Role.choices)
    email = models.EmailField(unique=True,null=False)
    phone_number = models.CharField(max_length=15, unique=True,null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50,null=True)
   
    email = models.EmailField(unique=True,null=False)
    phone_number = models.CharField(max_length=15, unique=True,null=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Call(models.Model):
    call_id = models.AutoField(primary_key=True)
    customer_id= models.ForeignKey(Customer, on_delete=models.CASCADE)
    agent_id = models.ForeignKey(Agent, on_delete=models.CASCADE)
    call_start_time=models.DateTimeField(null=False)
    call_end_time=models.DateTimeField(null=False)
    call_duration=models.DurationField(null=True,blank=True)
    call_status= models.CharField(CallStatus.choices, max_length=10)
    call_purpose = models.CharField(CallPurpose.choices, max_length=10)
    notes = models.TextField(blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)

    @property
    def call_duration(self):
        if self.call_start_time and self.call_end_time:
            return self.call_end_time - self.call_start_time
        return None

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


