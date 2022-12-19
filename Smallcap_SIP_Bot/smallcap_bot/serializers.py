from rest_framework import serializers
from .models import *

class TotalReturnsIndex_Data_Serializer(serializers.ModelSerializer):
    class Meta:
        model=TotalReturnsIndex_Data
        fields="__all__"

class UserPreferences_Serializer(serializers.ModelSerializer):
    class Meta:
        model=UserPreferences
        fields="__all__"

class UserDetails_Serializer(serializers.ModelSerializer):
    class Meta:
        model=UserDetails
        fields="__all__"

class Alerts_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Alerts
        fields="__all__"