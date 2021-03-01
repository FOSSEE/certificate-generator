from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
events = ()
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # other details
    uin = models.CharField(max_length=50)  #2 intialletters + 6 hexadigits
    attendance = models.NullBooleanField()

class Event(models.Model):
    purpose = models.CharField(max_length=25, choices=events)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # other details

class Certificate(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300, null=True, blank=True)
    serial_no = models.CharField(max_length=50) #purpose+uin+1stletter
    counter = models.IntegerField()
    workshop = models.CharField(max_length=1000, null=True, blank=True)
    paper = models.CharField(max_length=1000, null=True, blank=True)
    verified = models.IntegerField(default=0)
    serial_key = models.CharField(max_length=200, null=True)
    short_key = models.CharField(max_length=50, null=True)


class FeedBack(models.Model):
    ''' Feed back form for the event '''
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    institution = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin_number = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='SLC')
    submitted = models.BooleanField(default=False)
    answer = models.ManyToManyField('Answer')


class Question(models.Model):
    question = models.CharField(max_length=500)
    purpose = models.CharField(max_length=10, default='SLC')

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000)


class CEP(models.Model):
    course_name = models.CharField(max_length=500)
    student_name = models.CharField(max_length=200)
    incharge = models.CharField(max_length=200)
    coordinator = models.CharField(max_length=200)
    email = models.EmailField()
    institute = models.CharField(max_length=2000, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='CEP')
