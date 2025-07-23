from django.db import models

from django.db.models import F


class CallStatus(models.TextChoices):
    Answered = 'Answered'
    Missed = 'Missed'
    Voicemail = 'Voicemail'
    Busy = 'Busy'
    Failed = 'Failed'
    def __str__(self):
        return "call_status"

class CallPurpose(models.TextChoices):
    PriceInquiry = 'Price Inquiry'
    WarrantyClaim = 'Warranty Claim'

class Role(models.TextChoices):
    Agent ='Agent'
    Supervisor = 'Supervisor'
    admin =  'Manager'

class Sentiment(models.TextChoices):
    Positive =  'Positive'
    Neutral =  'Neutral'
    Negative =  'Negative'



class Agent(models.Model):
    agent_id= models.AutoField(primary_key=True)
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
    secondary_phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_type = models.CharField(max_length=20, choices=[('Individual', 'Individual'), ('Business', 'Business')], default='Individual')
    company_name = models.CharField(max_length=100, null=True, blank=True)
    created_by_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Call(models.Model):
    call_id = models.AutoField(primary_key=True)
    customer_id= models.ForeignKey(Customer, on_delete=models.CASCADE)
    agent_id = models.ForeignKey(Agent, on_delete=models.CASCADE)
    call_start_time=models.DateTimeField(null=False)
    call_end_time=models.DateTimeField(null=False)
    call_duration=models.DurationField()
    call_status= models.CharField(choices=CallStatus.choices,max_length=40,verbose_name="Status")
    call_purpose = models.CharField(choices=CallPurpose.choices,max_length=40,verbose_name='Purpose')
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
    sentiment=models.CharField(choices=Sentiment.choices, max_length=10, verbose_name="Sentiment")
    summary = models.TextField(default='', blank=True)
    transcription = models.TextField(null=True, blank=True)
    keywords = models.TextField()
    action_items = models.TextField(null=True, blank=True)
    analysis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.analysis_id} for Call {self.call.call_id}"
class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    related_call= models.ForeignKey(Call, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    aasigned_agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING ,null=True, blank=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Closed', 'Closed')], default='Open')
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'),('Urgent','Urgent')], default='Medium',verbose_name="Priority")
    source= models.CharField(max_length=20, choices=[('Email', 'Email'), ('Phone', 'Phone'), ('Web', 'Web'),("Chatbot","Chatbot")], default='Email')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_replied_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

class TicketReply(models.Model):
    reply_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField()
    is_internal = models.BooleanField(default=False, verbose_name="Internal Reply")
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    oredr_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('Cancelled', 'Cancelled'),
    ('Delivered','Delivered'),('Shipped',"Shipped")], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class product   (models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255) 
    description = models.TextField(null=True, blank=True)
    price= models.DecimalField(max_digits=10, decimal_places=2)
    sku=models.UUIDField(unique=True, default=None, editable=False)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.subject}"


class WarrantyClaim(models.Model):
    claim_id = models.AutoField(primary_key=True)
    warranty_id = models.ForeignKey('Warranty', on_delete=models.CASCADE, related_name='claims')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_id = models.ForeignKey(product, on_delete=models.CASCADE)
    claim_date = models.DateTimeField(auto_now_add=True)
    reported_issue = models.TextField(null=True, blank=True)
    resolution_type = models.CharField(max_length=20, choices=[('Repair', 'Repair'), ('Replacement', 'Replacement'), ('Rejected', 'Rejected')], null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    resolved_by_agent_id = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_claims')
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Warranty Claim {self.claim_id} for {self.product.name} by {self.customer.first_name} {self.customer.last_name}"

class Warranty(models.Model):
    warranty_id = models.AutoField(primary_key=True)
    oredr_item_id = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='warranties')
    product_id = models.ForeignKey(product, on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Voided', 'Voided')], default='Active')

    def __str__(self):
        return f"Warranty {self.warranty_id} for {self.product.name} - {self.customer.first_name} {self.customer.last_name}"