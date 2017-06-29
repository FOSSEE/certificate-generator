from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from certificate.models import Python_Workshop, Python_Workshop_BPPy, OpenModelica_WS, Drupal_WS, Osdag_WS, Scipy_TA_2016, Scipy_participant_2016, Scipy_speaker_2016, Scipy_workshop_2016, eSim_WS, Internship_participant,Internship16_participant, Scilab_participant, Certificate, Event, Scilab_speaker, Scilab_workshop, Question, Answer, FeedBack, Scipy_participant, Scipy_speaker, Drupal_camp, Tbc_freeeda, Dwsim_participant, Scilab_arduino, Esim_faculty, Scipy_participant_2015, Scipy_speaker_2015, OpenFOAM_Symposium_participant_2016, OpenFOAM_Symposium_speaker_2016
import subprocess
import os
from string import Template
import hashlib
from certificate.forms import FeedBackForm
from collections import OrderedDict
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def index(request):
    return render_to_response('index.html')

def download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/certificate_template/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = request.POST.get('workshop', None)
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Scilab_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('download.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = Scilab_speaker.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scilab_speaker.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('download.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('download.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        elif type == 'W':
            if workshop:
                user = Scilab_workshop.objects.filter(email=email, workshops=workshop)
                if user:
                    user = [user[0]]
            else:
                user = Scilab_workshop.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('download.html', context, context_instance=ci)
            if len(user) > 1:
                context['workshops'] = user
                context['v'] = 'workshop'
                return render_to_response('download.html', context, context_instance=ci)
            else:
                user = user[0]
                workshop = user.workshops
        name = user.name
        purpose = user.purpose
        year = '14'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        qrcode = 'NAME: {0}; SERIAL-NO: {1}; '.format(name, serial_no)
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            certificate = create_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            certificate = create_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no, counter=1, workshop=workshop, paper=paper)
                    certi_obj.save()
                    return certificate[0]
        
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('download.html', context, ci)
    context['message'] = ''
    return render_to_response('download.html', context, ci)

def verification(serial, _type):
    context = {}
    if _type == 'key':
        try:
            certificate = Certificate.objects.get(short_key=serial)
            name = certificate.name.title()
            paper = certificate.paper
            workshop = certificate.workshop
            serial_no = certificate.serial_no
            certificate.verified += 1
            certificate.save()
            purpose, year, type = _get_detail(serial_no)
            if type == 'P':
                if purpose == 'DWSIM Workshop':
                    dwsim_user = Dwsim_participant.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name),
                        ('Event', purpose), ('Days', '29 - 30 May'), ('Year', year)])
                elif purpose == 'Scilab Arduino Workshop':
                    arduino_user = Scilab_arduino.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '3 - 4 July'), ('Year', year)])
                elif purpose == 'eSim Faculty Meet':
                    faculty = Esim_faculty.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '22 August'), ('Year', year)])
                elif purpose == 'Osdag Workshop':
                    faculty = Osdag_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '4 June'), ('Year', year)])
                elif purpose == 'Drupal Workshop':
                    faculty = Drupal_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '30 July'), ('Year', year)])
                elif purpose == 'OpenModelica Workshop':
                    faculty = OpenModelica_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '4-5 January'), ('Year', year)])
                elif purpose == 'Python Workshop':
                    faculty = Python_Workshop.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', faculty.ws_date), ('Year', year)])
                elif purpose == 'Python 3day Workshop':
                    faculty = Python_Workshop_BPPy.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', faculty.ws_date), ('Year', year)])
                elif purpose == 'eSim Workshop':
                    faculty = eSim_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '11 June'), ('Year', year)])
                elif purpose == 'SciPy India':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '14 - 16 December'), ('Year', year)])
                elif purpose == 'SciPy India 2016':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '10 - 11 December'), ('Year', year)])
                elif purpose == 'OpenFOAM Symposium':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                        ('Days', '27 February'), ('Year', year)])
                elif purpose == 'DrupalCamp Mumbai':
                    drupal_user = Drupal_camp.objects.get(email=certificate.email)
                    DAY = drupal_user.attendance
                    if DAY == 1:
                        day = 'Day 1'
                    elif DAY == 2:
                        day = 'Day 2'
                    elif DAY == 3:
                        day = 'Day 1 and Day 2'
                    detail = OrderedDict([('Name', name), ('Attended', day),
                        ('Event', purpose), ('Year', year)])
                elif purpose == 'FreeEDA Textbook Companion':
                    user_books = Tbc_freeeda.objects.filter(email=certificate.email).values_list('book')
                    books = [ book[0] for book in user_books ]
                    detail = OrderedDict([('Name', name), ('Participant', 'Yes'),
                        ('Project', 'FreeEDA Textbook Companion'), ('Books completed', ','.join(books))])
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A' or type == 'T':
                detail = '{0} had presented paper on {3} in the {1} {2}'.format\
                        (name, purpose, year, paper)
                if purpose == 'SciPy India':
                    detail = OrderedDict([('Name', name), ('Event', purpose), ('paper', paper), ('Days', '14 - 16 December'), ('Year', year)])
                elif purpose == 'SciPy India 2016':
                    detail = OrderedDict([('Name', name), ('Event', purpose), ('paper', paper), ('Days', '10 - 11 December'), ('Year', year)])
                elif purpose == 'OpenFOAM Symposium':
                    detail = OrderedDict([('Name', name), ('Event', purpose), ('paper', paper), ('Days', '27 February'), ('Year', year)])
                elif purpose == 'FOSSEE Internship':
                    intership_detail = Internship_participant.objects.get(email=certificate.email)
                    user_project_title = Internship_participant.objects.filter(email=certificate.email)
                    context['intern_ship'] = True                    
                    detail = OrderedDict([('Name', name), ('Internship Completed', 'Yes'),
                        ('Project', intership_detail.project_title), ('Internship Duration', intership_detail.internship_project_duration), ('Superviser Name', intership_detail.superviser_name_detail)])
                elif purpose == 'FOSSEE Internship 2016':
                    intership_detail = Internship16_participant.objects.get(email=certificate.email)
                    user_project_title = Internship16_participant.objects.filter(email=certificate.email)
                    context['intern_ship'] = True                    
                    detail = OrderedDict([('Name', name), ('Internship Completed', 'Yes'),
                        ('Project', intership_detail.project_title), ('Internship Duration', intership_detail.internship_project_duration)])
                
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'W':
                detail = '{0} had attended workshop on {3} in the {1} {2}'.format\
                        (name, purpose, year, workshop)
            context['serial_key'] = True
            
        except Certificate.DoesNotExist:
            detail = 'User does not exist'
            context["invalidserial"] = 1
        context['detail'] = detail
        return context
    if _type == 'number':
        try:
            certificate = Certificate.objects.get(serial_no=serial)
            name = certificate.name.title()
            paper = certificate.paper
            workshop = certificate.workshop
            certificate.verified += 1
            certificate.save()
            purpose, year, type = _get_detail(serial)
            if type == 'P':
                if purpose == 'DrupalCamp Mumbai':
                    drupal_user = Drupal_camp.objects.get(email=certificate.email)
                    DAY = drupal_user.attendance
                    if DAY == 1:
                        day = 'Day 1'
                    elif DAY == 2:
                        day = 'Day 2'
                    elif DAY == 3:
                        day = 'Day 1 and Day 2'
                    detail = {}
                    detail['Name'] = name
                    detail['Attended'] = day
                    detail['Event'] = purpose
                    detail['Year'] = year
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A' or type == 'T':
                detail = '{0} had presented paper on {3} in the {1} {2}'.format(name, purpose, year, paper)
            elif type == 'W' :
                detail = '{0} had attended workshop on {3} in the {1} {2}'.format(name, purpose, year, workshop)
            context['detail'] = detail
        except Certificate.DoesNotExist:
            context["invalidserial"] = 1
        return context


def verify(request, serial_key=None):
    context = {}
    ci = RequestContext(request)
    detail = None
    if serial_key is not None:
        context = verification(serial_key, 'key')
        return render_to_response('verify.html', context, ci)
    if request.method == 'POST':
        serial_no = request.POST.get('serial_no').strip()
        context = verification(serial_no, 'number')
        if 'invalidserial' in  context:
            context = verification(serial_no, 'key')
        return render_to_response('verify.html', context, ci)
    return render_to_response('verify.html',{}, ci)

def _get_detail(serial_no):
    purpose = None
    if serial_no[0:3] == 'SLC':
        purpose = 'Scilab Conference'
    elif serial_no[0:3] == 'SPC':
        purpose = 'SciPy India'
    elif serial_no[0:3] == 'S16':
        purpose = 'SciPy India 2016'
    elif serial_no[0:3] == 'DCM':
        purpose = 'DrupalCamp Mumbai'
    elif serial_no[0:3] == 'FET':
        purpose = 'FreeEDA Textbook Companion'
    elif serial_no[0:3] == 'DWS':
        purpose = 'DWSIM Workshop'
    elif serial_no[0:3] == 'SCA':
        purpose = 'Scilab Arduino Workshop'
    elif serial_no[0:3] == 'ESM':
        purpose = 'eSim Faculty Meet'
    elif serial_no[0:3] == 'OWS':
        purpose = 'Osdag Workshop'
    elif serial_no[0:3] == 'DRP':
        purpose = 'Drupal Workshop'
    elif serial_no[0:3] == 'OMW':
        purpose = 'OpenModelica Workshop'
    elif serial_no[0:3] == 'PWS':
        purpose = 'Python Workshop'
    elif serial_no[0:3] == 'P3W':
        purpose = 'Python 3day Workshop'
    elif serial_no[0:3] == 'EWS':
        purpose = 'eSim Workshop'
    elif serial_no[0:3] == 'OFC':
        purpose = 'OpenFOAM Symposium'
    elif serial_no[0:3] == 'FIC':
        purpose = 'FOSSEE Internship'
    elif serial_no[0:3] == 'F16':
        purpose = 'FOSSEE Internship 2016'


    if serial_no[3:5] == '14':
        year = '2014'
    elif serial_no[3:5] == '15':
        year = '2015'
    elif serial_no[3:5] == '16':
        year = '2016'
    elif serial_no[3:5] == '17':
        year = '2017'
    return purpose, year, serial_no[-1]


def create_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_SLC2014Pcertificate'
            download_file_name = 'SLC2014Pcertificate.pdf'
        elif type == 'A':
            template = 'template_SLC2014Acertificate'
            download_file_name = 'SLC2014Acertificate.pdf'
        elif type == 'W':
            template = 'template_SLC2014Wcertificate'
            download_file_name = 'SLC2014Wcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode,
                    paper=paper)
        elif type == 'W':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode,
                    workshop=workshop)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False] 
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

def _clean_certificate_certificate(path, file_name):
    clean_process = subprocess.Popen('make -C {0} clean file_name={1}'.format(path, file_name),
            shell=True)
    clean_process.wait()

def _make_certificate_certificate(path, type, file_name):
    if type == 'P':
        command = 'participant_cert'
    elif type == 'A':
        command = 'paper_cert'
    elif type == 'W':
        command = 'workshop_cert'
    elif type == 'T':
        command = 'workshop_cert'
    process = subprocess.Popen('timeout 15 make -C {0} {1} file_name={2}'.format(path, command, file_name),
            stderr = subprocess.PIPE, shell = True)
    err = process.communicate()[1]
    return process.returncode, err

def feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='SLC')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='SLC')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = 'Thank you for the feedback. You can download your certificate.'
                return render_to_response('download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('feedback.html', context, ci)


def scipy_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='SPC')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='SPC')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('scipy_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'SPC'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = 'Thank you for the feedback. You can download your certificate.'
                return render_to_response('scipy_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('scipy_feedback.html', context, ci)


def scipy_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Scipy_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = Scipy_speaker.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scipy_speaker.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_download.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        name = user.name
        purpose = user.purpose
        year = '14'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        qrcode = 'NAME: {0}; SERIAL-NO: {1}; '.format(name, serial_no)
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            certificate = create_scipy_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            certificate = create_scipy_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no, counter=1, workshop=workshop, paper=paper)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download.html', context, ci)
    context['message'] = 'You can download the certificate'
    return render_to_response('scipy_download.html', context, ci)


def create_scipy_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_SPC2014Pcertificate'
            download_file_name = 'SPC2014Pcertificate.pdf'
        elif type == 'A':
            template = 'template_SPC2014Acertificate'
            download_file_name = 'SPC2014Acertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode,
                    paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def drupal_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='DMC')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='DMC')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('drupal_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'DMC'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('drupal_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('drupal_feedback.html', context, ci)

def drupal_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/drupal_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Drupal_camp.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('drupal_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        fname = user.firstname
        lname = user.lastname
        name = '{0} {1}'.format(fname, lname)
        purpose = user.purpose
        DAY = user.attendance
        if DAY == 1:
            day = 'Day 1'
        elif DAY == 2:
            day = 'Day 2'
        elif DAY == 3:
            day = 'Day 1 and Day 2'
        else:
            context['notregistered'] = 2
            return render_to_response('drupal_download.html', context,
                    context_instance=ci)
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'day': day, 'serial_key': old_user.short_key}
            certificate = create_drupal_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name, 'day': day, 'serial_key': short_key}
            certificate = create_drupal_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('drupal_download.html', context, ci)
    context['message'] = ''
    return render_to_response('drupal_download.html', context, ci)


def create_drupal_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_DCM2015Pcertificate'
        download_file_name = 'DCM2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                day=name['day'], serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]



def tbc_freeeda_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/tbc_freeeda_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Tbc_freeeda.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('tbc_freeeda_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        book = user.book
        author =user.author
        purpose = user.purpose
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'book': book, 'college': college, 'author': author, 'serial_key': old_user.short_key}
            certificate = create_freeeda_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name, 'book': book, 'college': college, 'author': author, 'serial_key': short_key}
            certificate = create_freeeda_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('tbc_freeeda_download.html', context, ci)
    context['message'] = ''
    return render_to_response('tbc_freeeda_download.html', context, ci)


def create_freeeda_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_FET2015Pcertificate'
        download_file_name = 'FET2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                book=name['book'], author=name['author'], college=name['college'],
                serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def dwsim_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='DWS')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='DWS')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('dwsim_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'DWS'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('dwsim_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('dwsim_feedback.html', context, ci)

def dwsim_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/dwsim_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Dwsim_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('dwsim_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_dwsim_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_dwsim_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('dwsim_download.html', context, ci)
    context['message'] = ''
    return render_to_response('dwsim_download.html', context, ci)


def create_dwsim_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_DWS2015Pcertificate'
        download_file_name = 'DWS2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def arduino_google_feedback(request):
    return render_to_response('arduino_google_feedback.html')


def arduino_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='SCA')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='SCA')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('arduino_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'SCA'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('arduino_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('arduino_feedback.html', context, ci)

def arduino_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scilab_arduino_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Scilab_arduino.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('arduino_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_arduino_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_arduino_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('arduino_download.html', context, ci)
    context['message'] = ''
    return render_to_response('arduino_download.html', context, ci)


def create_arduino_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_SCA2015Pcertificate'
        download_file_name = 'SCA2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def osdag_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/osdag_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Osdag_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('osdag_workshop_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_osdag_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_osdag_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('osdag_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('osdag_workshop_download.html', context, ci)

def osdag_workshop_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='OWS')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='OWS')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('osdag_workshop_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'OWS'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('osdag_workshop_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('osdag_workshop_feedback.html', context, ci)


def create_osdag_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_OWS2016Pcertificate'
        download_file_name = 'OWS2016Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

def drupal_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/drupal_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Drupal_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('drupal_workshop_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_drupal_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_drupal_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('drupal_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('drupal_workshop_download.html', context, ci)

def create_drupal_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_DWS2016Pcertificate'
        download_file_name = 'DWS2016Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

def esim_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/esim_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = eSim_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('esim_workshop_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esim_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_esim_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('esim_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esim_workshop_download.html', context, ci)

def esim_workshop_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='EWS')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='EWS')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('esim_workshop_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'EWS'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('esim_workshop_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('esim_workshop_feedback.html', context, ci)


def create_esim_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_EWS2016Pcertificate'
        download_file_name = 'EWS2016Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def esim_google_feedback(request):
    return render_to_response('esim_google_feedback.html')

def esim_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/esim_faculty_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Esim_faculty.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('esim_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esim_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_esim_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('esim_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esim_download.html', context, ci)


def create_esim_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_ESM2015Pcertificate'
        download_file_name = 'ESM2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

###############################################################################
# SciPy 2015
###############################################################################

def scipy_feedback_2015(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='SPC2015')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='SPC2015')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('scipy_download_2015.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'SPC2015'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('scipy_download_2015.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('scipy_feedback_2015.html', context, ci)


def scipy_download_2015(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2015/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Scipy_participant_2015.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2015.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = Scipy_speaker_2015.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scipy_speaker_2015.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2015.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_download_2015.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        name = user.name
        purpose = user.purpose
        year = '15'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_scipy_certificate_2015(certificate_path, details, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_scipy_certificate_2015(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download_2015.html', context, ci)
    context['message'] = ''
    return render_to_response('scipy_download_2015.html', context, ci)


def create_scipy_certificate_2015(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_SPC2015Pcertificate'
            download_file_name = 'SPC2015Pcertificate.pdf'
        elif type == 'A':
            template = 'template_SPC2015Acertificate'
            download_file_name = 'SPC2015Acertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

@csrf_exempt
def scipy_feedback_2016(request):
   return render_to_response('scipy_feedback_2016.html')


@csrf_exempt
def scipy_download_2016(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2016/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Scipy_participant_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
            paper = "paper name temporary"
        elif type == 'A':
            if paper:
                user = Scipy_speaker_2016.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scipy_speaker_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        elif type == 'W':
            if paper:
                user = Scipy_workshop_2016.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scipy_workshop_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        elif type == 'T':
            if paper:
                user = Scipy_TA_2016.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = Scipy_TA_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        name = user.name
        email = user.email
        purpose = user.purpose
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')


        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_certificate_2016(certificate_path, details, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                context['error'] = False
                return render_to_response( 'scipy_download_2016.html', context)
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_certificate_2016(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return render(request, 'scipy_download_2016.html')

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download_2016.html', context, ci)
    context['message'] = ''
    return render_to_response('scipy_download_2016.html', context, ci)


@csrf_exempt
def create_scipy_certificate_2016(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_SPC2016Pcertificate'
            download_file_name = 'SPC2016Pcertificate.pdf'
        elif type == 'W':
            template = 'template_SPC2016Wcertificate'
            download_file_name = 'SPC2016Wcertificate.pdf'
        elif type == 'A':
            template = 'template_SPC2016Acertificate'
            download_file_name = 'SPC2016Acertificate.pdf'
        elif type == 'T':
            template = 'template_SPC2016Tcertificate'
            download_file_name = 'SPC2016Tcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        elif type == 'W':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        elif type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
    

        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            path = os.path.join(certificate_path, str(file_name)+ ".pdf")
            
            try : 
                sender_name = "scipy"
                sender_email = "scipy@fossee.in"
                subject = "SciPy India 2016 - Certificate"
                to = ['scipy@fossee.in', name['email'],]

                message_text = """Dear Participant,\n\nPlease find attached the participation certificate for SciPy India 2016.\nIf you wish to print this certificate, for optimal printing, please follow these instructions:\n\nRecommended Paper: Ivory (Matt or Glossy) White \nRecommended GSM: Minimum of 170\nSize:  Letter size (8.5 x 11 in)\nPrint Settings: Fit to page\n\nRegards,\nSciPy India Team."""
                message_html = """Dear Participant,<br><br>Please find attached the participation certificate for SciPy India 2016.<br>If you wish to print this certificate, for optimal printing, please follow these instructions:<br><br>Recommended Paper: Ivory (Matt or Glossy) White <br>Recommended GSM: Minimum of 170<br>Size:  Letter size (8.5 x 11 in)<br>Print Settings: Fit to page<br><br>Regards,<br>SciPy India Team."""
                email = EmailMultiAlternatives(
                    subject,message_text,
                    sender_email, to,
                    headers={"Content-type":"text/html;charset=iso-8859-1"}
                )
                email.attach_alternative(message_html, "text/html")
                email.attach_file(path) 
                email.send(fail_silently=True)

            except Exception as e:
                pass
            _clean_certificate_certificate(certificate_path, file_name)
            return [None, False]
        else:
            error = True

    except Exception, e:  
        error = True
    return [None, error]




@csrf_exempt
def openmodelica_feedback_2017(request):
   return render_to_response('openmodelica_feedback_2017.html')

@csrf_exempt
def openmodelica_download_2017(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/openmodelica_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = OpenModelica_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('openmodelica_download_2017.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '17'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_openmodelica_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_openmodelica_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('openmodelica_download_2017.html', context, ci)
    context['message'] = ''
    return render_to_response('openmodelica_download_2017.html', context, ci)

def create_openmodelica_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_OMW2017Pcertificate'
        download_file_name = 'OMW2017Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]








###############################################################################
# OpenFOAM Symposium 2016
###############################################################################

def openfoam_symposium_feedback_2016(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='OFSC2016')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='OFSC2016')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('openfoam_symposium_download_2016.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'OFSC2016'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('openfoam_symposium_download_2016.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('openfoam_symposium_feedback_2016.html', context, ci)


def openfoam_symposium_download_2016(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/openfoam_symposium_template_2016/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = OpenFOAM_Symposium_participant_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('openfoam_symposium_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = OpenFOAM_Symposium_speaker_2016.objects.filter(email=email, paper=paper)
                if user:
                    user = [user[0]]
            else:
                user = OpenFOAM_Symposium_speaker_2016.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('openfoam_symposium_download_2016.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('openfoam_symposium_download_2016.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        name = user.name
        purpose = user.purpose
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_openfoam_symposium_certificate_2016(certificate_path, details, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_openfoam_symposium_certificate_2016(certificate_path, details,
                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('openfoam_symposium_download_2016.html', context, ci)
    context['message'] = ''
    return render_to_response('openfoam_symposium_download_2016.html', context, ci)


def create_openfoam_symposium_certificate_2016(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_OFSC2016Pcertificate'
            download_file_name = 'OFSC2016Pcertificate.pdf'
        elif type == 'A':
            template = 'template_OFSC2016Acertificate'
            download_file_name = 'OFSC2016Acertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


###############################################################################
# Scilab Internship Certificate
###############################################################################


def fossee_internship_cerificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fossee_internship_cerificate_template/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('project_title', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Internship_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('fossee_internship_cerificate_download.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = Internship_participant.objects.filter(email=email, paper=project_title, internship_project_duration=internship_project_duration, student_edu_detail=student_edu_detail, student_institute_detail=student_institute_detail, superviser_name_detail=superviser_name_detail)
                if user:
                    user = [user[0]]
            else:
                user = Internship_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('fossee_internship_cerificate_download.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('fossee_internship_cerificate_download.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.project_title
        name = user.name
        purpose = user.purpose
        internship_project_duration = user.internship_project_duration
        student_edu_detail = user.student_edu_detail
        student_institute_detail=user.student_institute_detail
        superviser_name_detail=user.superviser_name_detail
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fossee_internship_cerificate(certificate_path, details, qrcode, type, paper, internship_project_duration, 
                student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_fossee_internship_cerificate(certificate_path, details, qrcode, type, paper,
                          internship_project_duration, student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no, counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fossee_internship_cerificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fossee_internship_cerificate_download.html', context, ci)


def create_fossee_internship_cerificate(certificate_path, name, qrcode, type, paper, internship_project_duration, student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name):
    error = False
    try:
        download_file_name = None
        year = internship_project_duration[internship_project_duration.find('to')-5:internship_project_duration.find('to')].strip()
        if type == 'P':
            template = 'template_FIC2016Pcertificate'
            download_file_name = 'FIC2016Pcertificate.pdf'
        elif type == 'A':
            template = 'template_FIC2016Acertificate'
            download_file_name = 'FIC{0}Acertificate.pdf'.format(year)

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper, 
                    internship_project_duration=internship_project_duration, 
                    student_edu_detail=student_edu_detail, 
                    student_institute_detail=student_institute_detail, 
                    superviser_name_detail=superviser_name_detail)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]


def fossee_internship16_cerificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fossee_internship16_cerificate_template/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('project_title', None)
        workshop = None
        email = request.POST.get('email').strip()
        type = request.POST.get('type')
        if type == 'P':
            user = Internship16_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('fossee_internship16_cerificate_download.html', context, context_instance=ci)
            else:
                user = user[0]
        elif type == 'A':
            if paper:
                user = Internship16_participant.objects.filter(email=email, paper=project_title, internship_project_duration=internship_project_duration, student_edu_detail=student_edu_detail, student_institute_detail=student_institute_detail, superviser_name_detail=superviser_name_detail)
                if user:
                    user = [user[0]]
            else:
                user = Internship16_participant.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('fossee_internship16_cerificate_download.html', context, context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('fossee_internship16_cerificate_download.html', context, context_instance=ci)
            else:
                user = user[0]
                paper = user.project_title
        name = user.name
        purpose = user.purpose
        internship_project_duration = user.internship_project_duration
        student_edu_detail = user.student_edu_detail
        student_institute_detail=user.student_institute_detail
        superviser_name_detail=user.superviser_name_detail
        year = '16'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fossee_internship_cerificate(certificate_path, details, qrcode, type, paper, internship_project_duration, 
                student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_fossee_internship_cerificate(certificate_path, details, qrcode, type, paper,
                          internship_project_duration, student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no, counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fossee_internship16_cerificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fossee_internship16_cerificate_download.html', context, ci)


def create_fossee_internship16_cerificate(certificate_path, name, qrcode, type, paper, internship_project_duration, student_edu_detail, student_institute_detail, superviser_name_detail, workshop, file_name):
    error = False
    try:
        download_file_name = None
        if type == 'P':
            template = 'template_FIC2016Pcertificate'
            download_file_name = 'FIC2016Pcertificate.pdf'
        elif type == 'A':
            template = 'template_FIC2016Acertificate'
            download_file_name = 'FIC2016Acertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, paper=paper, 
                    internship_project_duration=internship_project_duration, 
                    student_edu_detail=student_edu_detail, 
                    student_institute_detail=student_institute_detail, 
                    superviser_name_detail=superviser_name_detail)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

# def python_workshop_download(request):
#     return render_to_response("python_workshop_download.html")


@csrf_exempt
def python_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/python_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        format = request.POST.get('format','iscp')
        paper = None
        workshop = None
        if type == 'P':
            if format=='iscp':
                user = Python_Workshop.objects.filter(email=email)
            else:
                user = Python_Workshop_BPPy.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('python_workshop_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        purpose = user.purpose
        ws_date = user.ws_date
        paper = user.paper
        is_coordinator = user.is_coordinator
        year = '17'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_python_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name, college, ws_date, is_coordinator,format)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_python_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name, college, ws_date, is_coordinator,format)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=workshop,
                            paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('python_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('python_workshop_download.html', context, ci)

def create_python_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name, college, ws_date, is_coordinator=False,format='iscp'):
    error = False
    err = None
    try:
        download_file_name = None
        if format=='iscp': # use templates based on 3day or 1day workshop
            if is_coordinator:
                template = 'coordinator_template_PWS2017Pcertificate'
            else:
                template = 'template_PWS2017Pcertificate'
        else:
            if is_coordinator:
                template = '3day_coordinator_template_PWS2017Pcertificate'
            else:
                template = '3day_template_PWS2017Pcertificate'

        download_file_name = 'PWS2017Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key = name['serial_key'], qr_code=qrcode, college = college, paper = paper, ws_date= ws_date)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]
