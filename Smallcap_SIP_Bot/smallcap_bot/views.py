import traceback
import re
import random
import string
import os
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from .models import *
from .serializers import *

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --------------------- USER DEFINED FUNCTIONS ------------------------- #

def user_preference_error_handler(option,email,user_name,current_sip_amount,step_up_percentage,step_up_month,subscription_option):

    response_dict = {}

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    userpreference_object = UserPreferences.objects.filter(email=email).first()
    user_data = UserPreferences_Serializer(userpreference_object)

    if option != 'update':
        if user_data.data['email']:
            response_dict['error'] = "Duplicate record"
            response_dict['message'] = "A record with same email already exists"
            return response_dict
    else:
        if not user_data.data['email']:
            response_dict['error'] = "User does not exist"
            response_dict['message'] = "No record with this email exists"
            return response_dict
    
    if(not re.fullmatch(email_regex, email)):
        response_dict['error'] = "Invalid email"
        response_dict['message'] = "Not a valid email address"
        return response_dict

    if not type(current_sip_amount) == float and not type(current_sip_amount) == int:
        response_dict['error'] = "Invalid SIP amount"
        response_dict['message'] = "Invalid data type for SIP amount"
        return response_dict
    else:
        if current_sip_amount < 500:
            response_dict['error'] = "Invalid SIP amount"
            response_dict['message'] = "SIP amount cannot be less than 500"
            return response_dict
    
    if not type(step_up_percentage) == float and not type(step_up_percentage) == int:
        response_dict['error'] = "Invalid step-up percentage"
        response_dict['message'] = "Invalid data type for step-up percentage"
        return response_dict
    
    if not type(step_up_month) == int or step_up_month <= 0 or step_up_month > 12:
        response_dict['error'] = "Invalid step-up month"
        response_dict['message'] = "Invalid data type / value for step-up month"
        return response_dict
    
    if not type(subscription_option) == int or subscription_option <= 0 or subscription_option > 4:
        response_dict['error'] = "Invalid subscription option"
        response_dict['message'] = "Invalid data type / value for subscription option"
        return response_dict
    
    return response_dict

def strong_password_generator(length):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits

    all = lower + upper + num

    temp = random.sample(all,length)
    strong_password = "".join(temp)

    return strong_password

def send_mail(mail_id,app_password,email,user_name,new_password):
    try:
        with smtplib.SMTP('smtp.gmail.com',587) as smtp:
            msg = MIMEMultipart('alternative')
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(mail_id,app_password)

            recipients = [email]

            msg['Subject'] = f"[SIP Assistant] - New password generated for your account"
            msg['From'] = "SIP Assistant"
            msg['To'] = "SIP Assistant"

            body_html = "Hi {0}, <br> \
            <p> You are receiving this message because you have requested for a new password. </p> \
            <p> Your new password is <b>{1}</b></p> \
            <p> It is strongly advisable to change your password after your next successful login</p> \
            <br> \
            Thanks \
            <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,new_password)

            msg_body = MIMEText(body_html, 'html')
            msg.attach(msg_body)

            smtp.sendmail(mail_id,recipients,msg.as_string())

        return "Success"
    
    except Exception as err:
        return err

# --------------------- API FUNCTIONS ------------------------- #

# Create your views here.
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        try:
            email = request.data['email']
            user_name = request.data['user_name']
            password = make_password(request.data['password'])
            current_sip_amount = request.data['current_sip_amount']
            step_up_percentage = request.data['step_up_percentage']
            step_up_month = request.data['step_up_month']
            subscription_option = request.data['subscription_option']
            last_updated_date = datetime.today().date()
            
            current_year = int(last_updated_date.strftime("%Y"))
            current_month = int(last_updated_date.strftime("%m"))

            # --------------------- ERROR HANDLING ------------------------- #
            option = 'create'
            error_handler = user_preference_error_handler(option,email,user_name,current_sip_amount,step_up_percentage,step_up_month,subscription_option)
            if error_handler:
                return Response(error_handler,status=status.HTTP_400_BAD_REQUEST)

            # --------------------- FUNCTIONALITY ------------------------- #
            
            sip_amount = current_sip_amount

            if step_up_month <= current_month:
                next_step_up_date = datetime(current_year + 1, step_up_month, 1).date()
            else:
                next_step_up_date = datetime(current_year, step_up_month, 1).date()

            
            create_userpreferences_object = UserPreferences.objects.create(
                email=email,
                user_name=user_name,
                password=password,
                current_sip_amount=current_sip_amount,
                step_up_percentage=step_up_percentage,
                step_up_month=step_up_month,
                subscription_option=subscription_option,
                last_updated_date=last_updated_date,
                next_step_up_date=next_step_up_date
            )

            create_userdetails_object = UserDetails.objects.create(
                email=email,
                user_name=user_name,
                subscription_option=subscription_option,
                sip_amount=sip_amount
            )

            create_userpreferences_object.save()
            create_userdetails_object.save()

            return Response({
                "success": True,
            },status=status.HTTP_201_CREATED)

        except Exception as err:
            return Response({
                "error": "Unexpected Error",
                "message": "Unexpected Error with the backend code",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_user_preference(request):
    if request.method == 'PUT':
        try:
            email = request.data['email']
            user_name = request.data['user_name']
            password = request.data['password']
            current_sip_amount = request.data['current_sip_amount']
            step_up_percentage = request.data['step_up_percentage']
            step_up_month = request.data['step_up_month']
            subscription_option = request.data['subscription_option']
            last_updated_date = datetime.today().date()

            current_year = int(last_updated_date.strftime("%Y"))
            current_month = int(last_updated_date.strftime("%m"))

            sip_amount = current_sip_amount

            if step_up_month <= current_month:
                next_step_up_date = datetime(current_year + 1, step_up_month, 1).date()
            else:
                next_step_up_date = datetime(current_year, step_up_month, 1).date()

            # --------------------- ERROR HANDLING ------------------------- #
            option = 'update'
            error_handler = user_preference_error_handler(option,email,user_name,current_sip_amount,step_up_percentage,step_up_month,subscription_option)
            if error_handler:
                return Response(error_handler,status=status.HTTP_400_BAD_REQUEST)
            
            userpreference_object = UserPreferences.objects.filter(email=email).first()
            user_data = UserPreferences_Serializer(userpreference_object)

            db_password = user_data.data['password']

            if not check_password(password,db_password):
                response_dict = {}
                response_dict['error'] = "Incorrect password"
                response_dict['message'] = "Incorrect password"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)

            # --------------------- FUNCTIONALITY ------------------------- #
            
            userpreference_object = UserPreferences.objects.get(email=email)
            setattr(userpreference_object,'user_name',user_name)
            setattr(userpreference_object,'current_sip_amount',current_sip_amount)
            setattr(userpreference_object,'step_up_percentage',step_up_percentage)
            setattr(userpreference_object,'step_up_month',step_up_month)
            setattr(userpreference_object,'subscription_option',subscription_option)
            setattr(userpreference_object,'last_updated_date',last_updated_date)
            setattr(userpreference_object,'next_step_up_date',next_step_up_date)
            
            userdetails_object = UserDetails.objects.get(email=email)
            setattr(userdetails_object,'user_name',user_name)
            setattr(userdetails_object,'subscription_option',subscription_option)
            setattr(userdetails_object,'sip_amount',sip_amount)
            
            userpreference_object.save()
            userdetails_object.save()

            return Response({
                "success": True,
                "last_updated_date": last_updated_date,
                "next_step_up_date": next_step_up_date
            },status=status.HTTP_200_OK)
        
        except Exception as err:
            return Response({
                "error": "Unexpected Error",
                "message": "Unexpected Error with the backend code",
                "track": str(err),
                "trace": traceback.format_exc()
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        try:
            response_dict = {}

            email = request.data['email']
            password = request.data['password']

            userpreference_object = UserPreferences.objects.filter(email=email).first()
            user_data = UserPreferences_Serializer(userpreference_object)

            db_email = user_data.data['email']
            db_password = user_data.data['password']

            if not db_email:
                response_dict['error'] = "User does not exist"
                response_dict['message'] = "No user with this email exists"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)

            if not check_password(password,db_password):
                response_dict['error'] = "Incorrect password"
                response_dict['message'] = "Incorrect password"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)
            
            username = user_data.data['user_name']
            current_sip_amount = user_data.data['current_sip_amount']
            step_up_percentage = user_data.data['step_up_percentage']
            step_up_month = user_data.data['step_up_month']
            subscription_option = user_data.data['subscription_option']
            last_updated_date = user_data.data['last_updated_date']
            next_step_up_date = user_data.data['next_step_up_date']

            return Response({
                "success": True,
                "username": username,
                "current_sip_amount": current_sip_amount,
                "step_up_percentage": step_up_percentage,
                "step_up_month": step_up_month,
                "subscription_option": subscription_option,
                "last_updated_date": last_updated_date,
                "next_step_up_date": next_step_up_date

            },status=status.HTTP_200_OK)

        except Exception as err:
            return Response({
                "error": "Unexpected Error",
                "message": "Unexpected Error with Backend",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def password_reset(request):
    if request.method == 'POST':
        try:
            response_dict = {}

            email = request.data['email']

            userpreference_object = UserPreferences.objects.filter(email=email).first()
            user_data = UserPreferences_Serializer(userpreference_object)

            db_email = user_data.data['email']
            username = user_data.data['user_name']

            if not db_email:
                response_dict['error'] = "User does not exist"
                response_dict['message'] = "No user with this email exists"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)
            
            new_password = strong_password_generator(10)
            hashed_password = make_password(new_password)

            ###################### SEND EMAIL ######################

            mail_id = os.environ.get('MAIL_ID')
            app_password = os.environ.get('APP_PASSWORD_SCRIPT')

            userpreference_object = UserPreferences.objects.get(email=email)
            setattr(userpreference_object,'password',hashed_password)

            if send_mail(mail_id,app_password,email,username,new_password) != "Success":
                response_dict['error'] = err,
                response_dict['message'] = "Unable to send email at this time, please try later"
                return Response(response_dict,status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            userpreference_object.save()
            return Response({
                "success": True,
            },status=status.HTTP_200_OK)


        except Exception as err:
            return Response({
                "error": "Unexpected Error",
                "message": "Unexpected Error with Backend",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def change_password(request):
    if request.method == 'POST':
        try:
            response_dict = {}

            email = request.data['email']
            password = make_password(request.data['password'])
            password_confirmation = request.data['password_confirmation']

            userpreference_object = UserPreferences.objects.filter(email=email).first()
            user_data = UserPreferences_Serializer(userpreference_object)

            db_email = user_data.data['email']

            if not db_email:
                response_dict['error'] = "User does not exist"
                response_dict['message'] = "No user with this email exists"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)
            
            if not check_password(password_confirmation,password):
                response_dict['error'] = "Password mismatch"
                response_dict['message'] = "Password mismatch"
                return Response(response_dict,status=status.HTTP_400_BAD_REQUEST)

            userpreference_object = UserPreferences.objects.get(email=email)
            setattr(userpreference_object,'password',password)
            userpreference_object.save()

            return Response({
                "success": True,
            },status=status.HTTP_200_OK)


        except Exception as err:
            return Response({
                "error": "Unexpected Error",
                "message": "Unexpected Error with Backend",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def latest_relative_value(request):
    try:
        latest_date_object = TotalReturnsIndex_Data.objects.all().order_by('-date').first()
        latest_date_serializer = TotalReturnsIndex_Data_Serializer(latest_date_object)

        date_list = latest_date_serializer.data['date'].split(' ')[0].split('-')
        date = date_list[2] + '-' + date_list[1] + '-' + date_list[0]

        full_relative_value = latest_date_serializer.data['relative_value']
        relative_value = str(full_relative_value)[:4]

        return Response({
            "date": date,
            "relative_value": relative_value
        },status=status.HTTP_200_OK)
    
    except Exception as err:
        return Response({
            "error": "Unexpected Error",
            "message": "Unexpected Error with Backend",
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_relative_values(request):
    try:
        tri_data_object = TotalReturnsIndex_Data.objects.all().order_by('-date')
        tri_data_serializer = TotalReturnsIndex_Data_Serializer(tri_data_object,many=True)
        
        total_data = []

        for data in tri_data_serializer.data:
            data_set = {}
            date_format = datetime.strptime(data['date'].split(' ')[0],'%Y-%m-%d').date()

            data_set['date'] = date_format
            data_set['nifty_smallcap_tri'] = data['nifty_smallcap_tri']
            data_set['nifty_50_tri'] = data['nifty_50_tri']
            data_set['relative_value'] = data['relative_value']
            total_data.append(data_set)

        return Response({
            "data": total_data,
            "count": len(total_data)
        },status=status.HTTP_200_OK)

    except Exception as err:
        return Response({
            "error": "Unexpected Error",
            "message": "Unexpected Error with Backend",
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
