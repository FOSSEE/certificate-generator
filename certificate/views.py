from __future__ import unicode_literals
import subprocess
import os
from string import Template
import hashlib
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from certificate.forms import FeedBackForm, ContactForm
from collections import OrderedDict
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
import calendar
from datetime import datetime
from django.http import HttpResponseRedirect
import json
import urllib
import urllib2
from django.conf import settings
import sending_emails
from certificate.models import CEP, Certificate, Event, Question, Answer, FeedBack
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
                return render_to_response('download.html', context,
                                          context_instance=ci)
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
                return render_to_response('download.html', context,
                                          context_instance=ci)
            if len(user) > 1:
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('download.html', context,
                                          context_instance=ci)
            else:
                user = user[0]
                paper = user.paper
        elif type == 'W':
            if workshop:
                user = Scilab_workshop.objects.filter(email=email,
                                                      workshops=workshop)
                if user:
                    user = [user[0]]
            else:
                user = Scilab_workshop.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('download.html', context,
                                          context_instance=ci)
            if len(user) > 1:
                context['workshops'] = user
                context['v'] = 'workshop'
                return render_to_response('download.html', context,
                                          context_instance=ci)
            else:
                user = user[0]
                workshop = user.workshops
        name = user.name
        purpose = user.purpose
        year = '14'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        qrcode = 'NAME: {0}; SERIAL-NO: {1}; '.format(name, serial_no)
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email,
                                               serial_no=serial_no)
            certificate = create_certificate(certificate_path,
                                             name, qrcode, type, paper,
                                             workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            certificate = create_certificate(certificate_path,
                                             name, qrcode, type, paper,
                                             workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                                            serial_no=serial_no,
                                            counter=1, workshop=workshop,
                                            paper=paper)
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
                if purpose == 'CEP Course':
                    cep_detail = CEP.objects.get(email=certificate.email)
                    detail = OrderedDict([('Name', name),
                                          ('course', fdp_detail.course),
                                          ('incharge', fdp_detail.incharge),
                                          ('coordinator', fdp_detail.coordinator),
                                          ('Event', event),
                                          ('Date', 'April-October 2021'),
                                          ('organiser', CEP, IITB)])
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A' or type == 'T':
                detail = '{0} had presented paper on {3} in the {1} {2}'.format(name, purpose, year, paper)
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
                detail = '{0} had attended workshop on {3} in the {1} {2}'.format(name, purpose, year, workshop)
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
            elif type == 'W':
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
        if 'invalidserial' in context:
            context = verification(serial_no, 'key')
        return render_to_response('verify.html', context, ci)
    return render_to_response('verify.html', {}, ci)


def _get_detail(serial_no):
    purpose = None
    if serial_no[0:3] == 'SLC':
        purpose = 'Scilab Conference'
    elif serial_no[0:3] == 'SPC':
        purpose = 'SciPy India'
    elif serial_no[0:3] == 'CEP':
        purpose = 'CEP Course'

    year = '20%s' % serial_no[3:5]
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

        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
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
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
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
    command = 'participant_cert'
    if type == 'P':
        command = 'participant_cert'
    elif type == 'A':
        command = 'paper_cert'
    elif type == 'W':
        command = 'workshop_cert'
    elif type == 'T':
        command = 'workshop_cert'
    process = subprocess.Popen('timeout 15 make -C {0} {1} file_name={2}'.format(path, command, file_name),
                               stderr=subprocess.PIPE, shell=True)
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
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        qrcode = 'NAME: {0}; SERIAL-NO: {1}; '.format(name, serial_no)
        file_name = '{0}{1}'.format(email, id)
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
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if type == 'P':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode)
        elif type == 'A':
            content_tex = content.safe_substitute(name=name.title(), qr_code=qrcode,
                                                  paper=paper)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
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


def cep_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/CEP/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = CEP.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('cep_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.student_name).title()
        incharge = user.incharge
        coordinator = user.coordinator
        purpose = 'CEP'
        course = user.course_name
        course = course.replace('&', 'and')

        year = '21'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://www.cep.iitb.ac.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_cep_certificate(certificate_path,
                    details, qrcode, course, incharge, coordinator, file_name)
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
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_cep_certificate(certificate_path,
                    details, qrcode, course, incharge, coordinator, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('cep_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('cep_certificate_download.html', context, ci)


def create_cep_certificate(certificate_path, details, qrcode,
        course, incharge, coordinator, file_name):
    error = False
    try:
        template = 'templateCEP'
        download_file_name = 'CEP2021Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                course=course, incharge=incharge, coordinator=coordinator)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        _type = 'P'
        return_value, err = _make_certificate_certificate(certificate_path, _type, file_name)
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
        print(e)

        error = True
    return [None, error]

