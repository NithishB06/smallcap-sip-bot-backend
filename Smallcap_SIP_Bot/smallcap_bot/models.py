from django.db import models

class TotalReturnsIndex_Data(models.Model):
    date = models.CharField(max_length=100,primary_key=True)
    nifty_smallcap_tri = models.FloatField()
    nifty_50_tri = models.FloatField()
    relative_value = models.FloatField()

class UserPreferences(models.Model):
    email = models.CharField(max_length=100,primary_key=True)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    current_sip_amount = models.FloatField()
    step_up_percentage = models.FloatField()
    step_up_month = models.IntegerField()
    subscription_option = models.IntegerField(default=1)
    last_updated_date = models.DateField()
    next_step_up_date = models.DateField()

class UserDetails(models.Model):
    email = models.CharField(max_length=100,primary_key=True)
    user_name = models.CharField(max_length=100)
    subscription_option = models.IntegerField(default=1)
    sip_amount = models.FloatField()

class Alerts(models.Model):
    date = models.CharField(max_length=100,primary_key=True)
    email = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    relative_value = models.FloatField()

