from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.

events = (
            ('SLC', 'Scilab Conference'),
            ('SPC', 'Scipy Conference'),
            ('S16', 'Scipy 2016 Conference'),
            ('PTC', 'Python Textbook Companion'),
            ('STC', 'Scilab Textbook Companion'),
            ('DCM', 'DrupalCamp Mumbai'),
            ('FET', 'FreeEda Textbook Companion'),
	    ('OFC', 'OpenFOAM Symposium'),
	    ('FIC', 'Fossee Internship'),
            ('F16', 'Fossee Internship 2016'),
            ('OWS', 'Osdag Workshop'),
            ('EWS', 'eSim Workshop'),
            ('DRP', 'Drupal Workshop'),
            ('OMW', 'OpenModelica Workshop'),
            ('PWS', 'Python Workshop'),
            ('S17', 'Scipy 2017 Conference'),
            ('S18', 'SciPy India 2018'),
            ('S19', 'SciPy India 2019'),
            ('NC8', 'NCCPS 2018 Conference'),
            ('IN2', 'Internship 2020'),
            ('SCI', 'Scilab Workshop 2019')
        )

roles = (
            ('Student', 'Student'),
            ('Contributor', 'Contributor'),
        )
internship_type = (
            ('remote', 'Remote Internship'),
        )

MONTHS = (
            ('January', 'January'),
            ('February', 'February'),
            ('March', 'March'),
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December'),
        )

years = ['2020', '2021']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

class Profile(models.Model):
    user = models.OneToOneField(User)
    # other details
    uin = models.CharField(max_length=50)  #2 intialletters + 6 hexadigits
    attendance = models.NullBooleanField()

class Event(models.Model):
    purpose = models.CharField(max_length=25, choices=events)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # other details

class Certificate(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50, null=True, blank=True)
    serial_no = models.CharField(max_length=50) #purpose+uin+1stletter
    counter = models.IntegerField()
    workshop = models.CharField(max_length=100, null=True, blank=True)
    paper = models.CharField(max_length=100, null=True, blank=True)
    verified = models.IntegerField(default=0)
    serial_key = models.CharField(max_length=200, null=True)
    short_key = models.CharField(max_length=50, null=True)

class Scilab_participant(models.Model):
    ''' Autogenerated model file csvimport Mon Dec  1 07:46:00 2014 '''
    id = models.IntegerField(primary_key=True, null=False)
    ticket_number = models.IntegerField(default=0, null=False, blank=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    ticket = models.CharField(max_length=50, null=True, blank=True)
    date = models.CharField(max_length=50, null=True, blank=True)
    order_id = models.IntegerField(default=0, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='SLC')
    attendance = models.BooleanField(default=False)

    class Meta:
        managed = True

class Scilab_speaker(models.Model):
    ''' Autogenerated model file csvimport Wed Dec  3 05:36:56 2014 '''

    id = models.IntegerField(default=0, null=False, primary_key=True, blank=False)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    ticket = models.CharField(max_length=100)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='SLC')
    attendance = models.BooleanField(default=False)

class Scilab_workshop(models.Model):
    ''' Autogenerated model file csvimport Wed Dec  3 06:31:59 2014 '''

    id = models.IntegerField(null=False, primary_key=True, blank=False)
    name = models.CharField(max_length=300)
    ticket_number = models.IntegerField(null=True)
    email = models.CharField(max_length=300)
    workshops = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='SLC')
    attendance = models.BooleanField(default=False)

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
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=1000)


class Scipy_participant(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='SPC')
    attendance = models.BooleanField(default=False)


class Scipy_speaker(models.Model):
    id = models.IntegerField(default=0, null=False, primary_key=True, blank=False)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='SPC')
    attendance = models.BooleanField(default=False)

class Drupal_camp(models.Model):
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    # Day 1 - 1, Day 2 - 2, Both days - 3, else 0
    attendance = models.PositiveSmallIntegerField(default=0)
    role = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='DCM')
    is_student = models.IntegerField(default=0)

class Tbc_freeeda(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    college = models.CharField(max_length=200)
    book = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='FET')


class Dwsim_participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='DWS')


class Scilab_arduino(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='SCA')


class Esim_faculty(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='ESM')

class Osdag_WS(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    college = models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField(default='2016-01-01')
    end_date = models.DateField(default='2016-01-01')
    purpose = models.CharField(max_length=10, default='OWS')

class Drupal_WS(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='DRP')
    status = models.BooleanField(default=False)
    date = models.DateField(default='2016-01-01')

class OpenModelica_WS(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='OMW')

class eSim_WS(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='EWS')

class Scipy_participant_2015(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='SPC')


class Scipy_speaker_2015(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='SPC')

class Scipy_participant_2016(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='S16')

class Scipy_speaker_2016(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S16')

class Scipy_workshop_2016(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S16')

class Scipy_TA_2016(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S16')

class OpenFOAM_Symposium_participant_2016(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='OFC')


class OpenFOAM_Symposium_speaker_2016(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='OFC')

class Python_Workshop(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300) #grades
    purpose = models.CharField(max_length=10, default='PWS')
    college = models.CharField(max_length = 200)
    ws_date = models.CharField(max_length = 100, null=True, blank=True)
    is_coordinator = models.BooleanField(default=False)


class Python_Workshop_BPPy(models.Model):
    """
    3day python workshop user details
    """
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300) #grades
    purpose = models.CharField(max_length=10, default='PWS')
    college = models.CharField(max_length = 200)
    ws_date = models.CharField(max_length = 100, null=True, blank=True)
    is_coordinator = models.BooleanField(default=False)


class Python_Workshop_adv(models.Model):
    """
    2day python workshop user details
    """
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300) #grades
    purpose = models.CharField(max_length=10, default='PWS')
    college = models.CharField(max_length = 200)
    ws_date = models.CharField(max_length = 100, null=True, blank=True)
    is_coordinator = models.BooleanField(default=False)


class Internship_participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    student_edu_detail = models.CharField(max_length=1000, null=True, blank=True)
    student_institute_detail = models.CharField(max_length=2000, null=True, blank=True)
    superviser_name_detail = models.CharField(max_length=2000, null=True, blank=True)
    project_title = models.CharField(max_length=1000)
    internship_project_duration = models.CharField(max_length=500, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='FIC')
    # year = models.CharField(max_length = 4)

class Internship16_participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    student_edu_detail = models.CharField(max_length=1000, null=True, blank=True)
    student_institute_detail = models.CharField(max_length=2000, null=True, blank=True)
    superviser_name_detail = models.CharField(max_length=2000, null=True, blank=True)
    project_title = models.CharField(max_length=1000)
    internship_project_duration = models.CharField(max_length=500, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='F16')


class Fellow2019(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    institute = models.CharField(max_length=2000, null=True, blank=True)
    title = models.CharField(max_length=1000)
    start_date = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='FEL')


class EqFellow2019(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    institute = models.CharField(max_length=2000, null=True, blank=True)
    floss = models.CharField(max_length=1000)
    purpose = models.CharField(max_length=10, default='FEQ')


class Osdag2019(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='OSD')

attendee_types = (
    ('P','Participants'),
    ('A','Speaker'),
    ('W','Workshop'),
    ('T','Organizers')
    )

class Scipy_2017(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S17')
    attendee_type = models.CharField(max_length=25, choices=attendee_types)


class Scipy_2018(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S18')
    attendee_type = models.CharField(max_length=25, choices=attendee_types)


class Scipy_2019(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='S19')
    attendee_type = models.CharField(max_length=25, choices=attendee_types)

class SciPyAll(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300, null=True)
    date = models.CharField(max_length=300)
    year = models.CharField(max_length=10)
    purpose = models.CharField(max_length=10, default='S20')
    attendee_type = models.CharField(max_length=25, default='P',
                                     choices=attendee_types)


class NCCPS_2018(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='NC8')
    attendee_type = models.CharField(max_length=25, choices=attendee_types)


class Scilab_Workshop_2019(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    paper = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='SCI')
    college = models.CharField(max_length = 200)
    organiser = models.CharField(max_length=300, default='IIT Bombay')
    ws_date = models.CharField(max_length = 100, null=True, blank=True)
    is_coordinator = models.BooleanField(default=False)


class Pymain(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='PYM')
    college = models.CharField(max_length = 200)
    organiser = models.CharField(max_length=300, default='IIT Bombay')
    date = models.CharField(max_length = 100, null=True, blank=True)


class Linuxcoord(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='LXC')
    college = models.CharField(max_length = 200)
    date = models.CharField(max_length = 100, null=True, blank=True)


class Esimcoord(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    purpose = models.CharField(max_length=10, default='ESC')
    college = models.CharField(max_length = 200)
    date = models.CharField(max_length = 100, null=True, blank=True)


class ScilabSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='SSS')


class PythonSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='PSS')


class LinuxSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='LSS')


class EsimSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='ESS')


class CPPSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='CPS')


class SupportAll(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    foss = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='FSA')


class RSupport(models.Model):
    rcid = models.IntegerField()
    rcname = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    role = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='RSS')
    rerun = models.BooleanField(default=False)


class AnimationParticipant(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    institute = models.CharField(max_length=400)
    role = models.CharField(max_length=100, choices=roles)


class AnimationWorkshop(models.Model):
    name = models.CharField(max_length=400)
    venue = models.CharField(max_length=400)
    no_of_days = models.CharField(max_length=20, default="one")
    date = models.CharField(max_length=100)
    participants = models.ManyToManyField(AnimationParticipant)
    purpose = models.CharField(max_length=10, default='FAC')


class AnimationInternship(models.Model):
    name = models.CharField(max_length=400)
    student = models.CharField(max_length=250)
    email = models.EmailField()
    institute = models.CharField(max_length=400)
    duration = models.CharField(max_length=100)
    method = models.CharField(max_length=100, choices=internship_type)
    purpose = models.CharField(max_length=10, default='FAI')
    year = models.IntegerField()


class AnimationContribution(models.Model):
    name = models.CharField(max_length=400)
    student = models.CharField(max_length=250)
    email = models.EmailField()
    institute = models.CharField(max_length=400)
    date = models.CharField(max_length=100)
    purpose = models.CharField(max_length=10, default='FAO')
    year = models.IntegerField()


class FOSSWorkshopTest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    foss = models.CharField(max_length=50)
    grade = models.CharField(max_length=5)
    purpose = models.CharField(max_length=5, default='FWT')


    class Meta:
        unique_together = ['email', 'foss']


class Wintership(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    institute = models.CharField(max_length=2000, null=True, blank=True)
    topic = models.CharField(max_length=1000)
    start_date = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='WIC')


class FDP(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    institute = models.CharField(max_length=2000, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='FD0')


class Fellow2020(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    institute = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200)
    start_date = models.CharField(max_length=25, null=True, blank=True)
    end_date = models.CharField(max_length=25, null=True, blank=True)
    mode = models.CharField(max_length=15, null=True, blank=True)
    mode_def = models.CharField(max_length=30, null=True, blank=True)
    _type = models.CharField(max_length=20, default='fellow')
    purpose = models.CharField(max_length=5, default='FL2')

class PythonCertification(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    grade = models.CharField(max_length=10)
    month = models.CharField(max_length=10)
    year = models.IntegerField()
    percentage = models.FloatField()
    institute = models.CharField(max_length=150)
    purpose = models.CharField(max_length=10, default='PCC')


class RAppre(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    foss = models.CharField(max_length=150)
    institute = models.CharField(max_length=150)
    date = models.CharField(max_length=150)
    purpose = models.CharField(max_length=10, default='RAP')


class ScilabHackathon(models.Model):
    team = models.CharField(max_length=20)
    interfaced = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    ctype = models.CharField(max_length=10)
    purpose = models.CharField(max_length=10, default='SCH')

new_pruposes = (
        ('openfoam2020', 'OFM'),
        )

class CertificateUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    institute = models.CharField(max_length=150, null=True, blank=True)
    purpose = models.CharField(max_length=10)
