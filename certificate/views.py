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
from certificate.models import Python_Workshop,\
Python_Workshop_BPPy, OpenModelica_WS, Drupal_WS,\
Osdag_WS, Scipy_TA_2016, Scipy_participant_2016,\
Scipy_speaker_2016, Scipy_workshop_2016, eSim_WS,\
Internship_participant, Internship16_participant,\
Scilab_participant, Certificate, Event, Scilab_speaker,\
Scilab_workshop, Question, Answer, FeedBack,\
Scipy_participant, Scipy_speaker, Drupal_camp,\
Tbc_freeeda, Dwsim_participant, Scilab_arduino,\
Esim_faculty, Scipy_participant_2015,\
Scipy_speaker_2015, OpenFOAM_Symposium_participant_2016,\
OpenFOAM_Symposium_speaker_2016, Scipy_2017, NCCPS_2018,\
Scipy_2018,Python_Workshop_adv, Scilab_Workshop_2019, Fellow2019, Osdag2019,\
Pymain, Esimcoord, Linuxcoord, ScilabSupport, PythonSupport, EqFellow2019,\
Scipy_2019, LinuxSupport, AnimationParticipant, AnimationWorkshop, EsimSupport,\
RSupport, FOSSWorkshopTest, Wintership, FDP, AnimationInternship, \
AnimationContribution, Fellow2020, PythonCertification, months, years, \
CertificateUser, ScilabHackathon, CPPSupport, RAppre, SciPyAll, SupportAll, \
ComplexFluids, SynfigHackathon, Mapathon, EsimMarathon, EsimMarathon2022, \
Intern2021, Fellow2021, MixedSignal

import csv

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
            if purpose == 'SciPy India 2017':
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', '29 - 30 November'),
                              ('Year', year)
                              ]

            elif purpose == 'SciPy India 2018':
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', '21 - 22 December'),
                              ('Year', year)
                              ]
                if not type == 'P':
                    detail_list.append(('Paper', paper))

                detail = OrderedDict(detail_list)
                context['serial_key'] = True
                context['detail'] = detail
                return context
            elif purpose == 'SciPy India 2019':
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', '29 - 30 November'),
                              ('Year', year)
                              ]
                if not type == 'P':
                    detail_list.append(('Paper', paper))

                detail = OrderedDict(detail_list)
                context['serial_key'] = True
                context['detail'] = detail
                return context
            elif purpose == 'SciPy India':
                if year == '2021':
                    date = '21 and 22 January'
                elif year == '2020':
                    date = '19 and 20 December'
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', date),
                              ('Year', year),
                              ('Organiser', 'FOSSEE')
                              ]
                if not type == 'P':
                    if type == 'W':
                        detail_list.append(('Role', 'Conducted Workshop'))
                        detail_list.append(('Workshop', paper))
                    if type == 'A':
                        detail_list.append(('Role', 'Speaker'))
                        detail_list.append(('Paper', paper))

                detail = OrderedDict(detail_list)
                context['serial_key'] = True
                context['detail'] = detail
                return context
            elif purpose == 'Complex Fluids Symposium':
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', '10 and 12 December'),
                              ('Year', year),
                              ('Organiser', 'IIT Bombay and the Indian Society of Rheology')
                              ]
                if not type == 'P':
                    if type == 'O':
                        detail_list.append(('Role', 'Presented a Poster'))
                        detail_list.append(('Title', paper))
                    if type == 'A':
                        detail_list.append(('Role', 'Presented a Talk'))
                        detail_list.append(('Title', paper))

                detail = OrderedDict(detail_list)
                context['serial_key'] = True
                context['detail'] = detail
                return context

            elif purpose == 'NCCPS 2018 Conference':
                detail_list = [
                              ('Name', name), ('Event', purpose),
                              ('Days', '26 November'),
                              ('Year', year)
                              ]
                if not type == 'P':
                    detail_list.append(('Paper', paper))

                detail = OrderedDict(detail_list)
                context['serial_key'] = True
                context['detail'] = detail
                return context
            if type == 'P':
                if purpose == 'DWSIM Workshop':
                    dwsim_user = Dwsim_participant.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                         ('Name', name),
                                         ('Event', purpose),
                                         ('Days', '29 - 30 May'),
                                         ('Year', year)
                                         ])
                elif purpose == 'Osdag Workshop 2019, IIT Bombay':
                    user = Osdag2019.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                         ('Name', name),
                                         ('Event', purpose),
                                         ('Year', year)
                                         ])
                elif purpose == 'Python Course Certificate':
                    certifications = PythonCertification.objects.filter(email=certificate.email)
                    certification = certifications.reverse()[0]
                    name = certification.name
                    institute = certification.institute
                    course = 'Basic Programming using Python'
                    offered_by = 'FOSSEE project, IIT Bombay'
                    detail = OrderedDict([('Name', name),
                                          ('Institute', institute),
                                          ('Course', course),
                                          ('Month(s)', str(', '.join(certifications.values_list('month', flat=True)))),
                                          ('Year(s)', ', '.join(map(str,certifications.values_list('year', flat=True)))),
                                          ('Grade(s)', str(', '.join(certifications.values_list('grade', flat=True)))),
                                          ('Offered by', offered_by)])
                elif purpose == 'FDP 2020, FOSSEE':
                    fdp_detail = FDP.objects.get(email=certificate.email)
                    event = "One Day Online Faculty Development Programme on \
                    Free and Open Source Tools for Education and Research"
                    organiser = 'BIT Sindri, Dhanbad and FOSSEE, IIT Bombay'
                    detail = OrderedDict([('Name', name),
                                          ('institute', fdp_detail.institute),
                                          ('Event', event),
                                          ('Date', '07 July 2020'),
                                          ('organiser', organiser)])
                elif purpose == 'OpenFOAM 2020, FOSSEE':
                    user = CertificateUser.objects.get(
                            email=certificate.email, purpose='OFM')
                    event = "Spoken Tutorial Based Pilot Workshop \
                    on Basic Level in OpenFOAM Version 7"
                    detail = OrderedDict([('Name', name),
                                          ('Event', event),
                                          ('Date', '26 July 2020')])
                elif purpose == 'R Workshop 2020':
                    user = RAppre.objects.get(
                            email=certificate.email, purpose='RAP')
                    event = "R Workshop 2020"
                    detail = OrderedDict([('Name', name),
                                          ('institute', user.institute),
                                          ('Event', event),
                                          ('Date', user.date)])
                elif purpose == 'Scilab Toolbox Hackathon 2020':
                    user = ScilabHackathon.objects.get(
                            email=certificate.email, purpose='SCH')
                    if user.ctype == 'champ':
                        ctype = 'Champion'
                    if user.ctype == 'conso':
                        ctype = 'Consolation'
                    if user.ctype == 'parti':
                        ctype = 'Participation'
                    event = purpose
                    detail = OrderedDict([('Name', name),
                                          ('Event', event),
                                          ('Interfaced', user.interfaced),
                                          ('Team Id', user.team),
                                          ('Type', '{0} Certificate'.format(ctype)),
                                          ('Time', 'June-July 2020')])
                elif purpose == 'Synfig Animation Hackathon 2020':
                    user = SynfigHackathon.objects.filter(
                            email=certificate.email, purpose='SYH')
                    user = user[0]
                    if user.ctype == 'champ':
                        ctype = 'Champion'
                    if user.ctype == 'conso':
                        ctype = 'Consolation'
                    if user.ctype == 'parti':
                        ctype = 'Participation'
                    if user.ctype == 'recog':
                        ctype = 'Recognition'
                    event = purpose
                    detail = OrderedDict([('Name', name),
                                          ('Event', event),
                                          ('Team Id', user.team),
                                          ('Type', '{0} Certificate'.format(ctype)),
                                          ('Time', '25 Nov and 15 Dec 2020')])
                    if user.ctype == 'champ':
                        detail.update([('Winner', '{0} prize'.format(user.position))])
                elif purpose == 'eSim Marathon 2022':
                    user = EsimMarathon2022.objects.filter(
                            email=certificate.email, purpose='EM2')
                    user = user[0]
                    if user.ctype == 'O':
                        ctype = 'Outstanding'
                    if user.ctype == 'V':
                        ctype = 'Very Good'
                    if user.ctype == 'G':
                        ctype = 'Good'
                    if user.ctype == 'E':
                        ctype = 'Excellent'
                    if user.ctype == 'M':
                        ctype = 'Mentoring'
                    event = 'Ciruit Design and Simulation using eSim'
                    detail = OrderedDict([('Name', name),
                                          ('College', user.college),
                                          ('Event', event),
                                          ('Ciruit', user.circuit),
                                          ('Performance', '{0}'.format(ctype)),
                                          ('Duration', 'For 3 weeks in the month of February-March 2022')])
                elif purpose == 'Mixed Signal Marathon 2022':
                    event = "Mixed Signal SoC design Marathon using eSim & SKY130"
                    user = MixedSignal.objects.filter(
                            email=certificate.email, purpose='MSM', year='2022')
                    user = user[0]
                    ctype = user.ctype
                    detail = OrderedDict([('Name', user.name),
                                          ('College', user.college),
                                          ('Event', event),
                                          ('Ciruit', user.circuit),
                                          ('Performance', '{0}'.format(ctype)),
                                          ('Duration', 'For 3 weeks in the month of September-October 2022')])
                elif purpose == 'eSim Marathon 2021':
                    user = EsimMarathon.objects.filter(
                            email=certificate.email, purpose='EMC')
                    user = user[0]
                    if user.ctype == 'O':
                        ctype = 'Outstanding'
                    if user.ctype == 'V':
                        ctype = 'Very Good'
                    if user.ctype == 'G':
                        ctype = 'Good'
                    if user.ctype == 'E':
                        ctype = 'Excellent'
                    if user.ctype == 'M':
                        ctype = 'Mentoring'
                    event = 'Ciruit Design and Simulation using eSim'
                    detail = OrderedDict([('Name', name),
                                          ('College', user.college),
                                          ('Event', event),
                                          ('Ciruit', user.circuit),
                                          ('Performance', '{0}'.format(ctype)),
                                          ('Duration', 'For 2 weeks in the month of June 2021')])
                elif purpose == 'Mapathon 2020':
                    user = Mapathon.objects.filter(
                            email=certificate.email, purpose='MAP')
                    user = user[0]
                    if user.ctype == 'champ':
                        ctype = 'Champion'
                    if user.ctype == 'parti':
                        ctype = 'Participation'
                    if user.ctype == 'recog':
                        ctype = 'Recognition'
                    if user.ctype == 'ment':
                        ctype = 'Mentor'
                    event = 'IITB-ISRO-AICTE Mapathon 2020'
                    detail = OrderedDict([('Name', name),
                                          ('Event', event),
                                          ('Team Id', user.team),
                                          ('Type', '{0} Certificate'.format(ctype)),
                                          ('Duration', '7 Dec. to 22 Dec. 2020')])
                elif purpose == 'Mapathon 2022':
                    user = Mapathon.objects.filter(
                            email=certificate.email, purpose='MP2')
                    user = user[0]
                    if user.ctype == 'champ':
                        ctype = 'Champion'
                    if user.ctype == 'parti':
                        ctype = 'Participation'
                    if user.ctype == 'recog':
                        ctype = 'Recognition'
                    if user.ctype == 'ment':
                        ctype = 'Mentor'
                    event = 'IITB-AICTE Mapathon 2022'
                    detail = OrderedDict([('Name', name),
                                          ('Event', event),
                                          ('Team Id', user.team),
                                          ('Type', '{0} Certificate'.format(ctype)),
                                          ('Duration', '22 February to 29 March 2022')])
                elif purpose == "FOSSEE WINTER INTERNSHIP 2019":
                    intership_detail = Wintership.objects.get(email=certificate.email)
                    user_project_title = intership_detail.topic
                    duration = '{0} to {1}'.format(intership_detail.start_date, intership_detail.end_date)
                    context['intern_ship'] = True
                    event = 'FOSSEE INTERNSHIP'
                    detail = OrderedDict([('Name', name), ('Event', event), ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), ('Internship Duration',duration)])
                elif purpose == "FOSSEE SUMMER FELLOWSHIP 2019":
                    intership_detail = Fellow2019.objects.get(email=certificate.email)
                    user_project_title = intership_detail.title
                    duration = '{0} to {1}'.format(intership_detail.start_date, intership_detail.end_date)
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('Event', purpose), ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), ('Internship Duration',duration)])
                elif purpose == "FOSSEE SUMMER FELLOWSHIP 2020":
                    internship_detail = Fellow2020.objects.get(email=certificate.email, _type='fellow')
                    user_project_title = internship_detail.title
                    institute = internship_detail.institute
                    duration = '{0} to {1}'.format(internship_detail.start_date, internship_detail.end_date)
                    mode = internship_detail.mode
                    mode_def = internship_detail.mode_def
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('From', institute),
                                          ('Event', purpose),
                                          ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), ('Internship Duration',duration),
                                          ('Mode', '{0}: {1}'.format(mode, mode_def))])
                elif purpose == "FOSSEE SUMMER FELLOWSHIP 2021":
                    internship_detail = Fellow2021.objects.get(email=certificate.email)
                    user_project_title = internship_detail.title
                    institute = internship_detail.institute
                    duration = '{0} to {1}'.format(internship_detail.start_date, internship_detail.end_date)
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('From', institute),
                                          ('Event', purpose),
                                          ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), ('Internship Duration',duration)])
                elif purpose == "FOSSEE SUMMER INTERNSHIP 2021":
                    internship_detail = Intern2021.objects.get(email=certificate.email)
                    user_project_title = internship_detail.title
                    institute = internship_detail.institute
                    mode = internship_detail.mode
                    mode_def = internship_detail.mode_def
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('From', institute),
                                          ('Event', purpose),
                                          ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), 
                                          ('Mode', '{0}: {1}'.format(mode, mode_def))])
                elif purpose == "FOSSEE INTERNSHIP 2020":
                    internship_detail = Fellow2020.objects.get(email=certificate.email, _type='intern')
                    user_project_title = internship_detail.title
                    institute = internship_detail.institute
                    duration = '{0} to {1}'.format(internship_detail.start_date, internship_detail.end_date)
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('From', institute),
                                          ('Event', purpose),
                                          ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title), ('Internship Duration',duration)])
                elif purpose == "FOSSEE SUMMER FELLOWSHIP 2019 Screening Task":
                    intership_detail = EqFellow2019.objects.get(email=certificate.email)
                    user_project_title = intership_detail.floss
                    context['intern_ship'] = True
                    detail = OrderedDict([('Name', name), ('Event', purpose), ('Internship Completed', 'Yes'),
                                          ('Project', user_project_title)])
                elif purpose == 'Scilab Arduino Workshop':
                    arduino_user = Scilab_arduino.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '3 - 4 July'),
                                          ('Year', year)
                                         ])
                elif purpose == 'eSim Faculty Meet':
                    faculty = Esim_faculty.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '22 August'),
                                          ('Year', year)
                                        ])
                elif purpose == 'Osdag Workshop':
                    osdag_workshop = Osdag_WS.objects.get(email=certificate.email)
                    days = '%s to %s' % (datetime.strftime(osdag_workshop.start_date, '%d %b'),
                                         datetime.strftime(osdag_workshop.end_date, '%d %b'))
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', days),
                                          ('Year', year)
                                          ])
                elif purpose == 'Drupal Workshop':
                    drupal_ws = Drupal_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                         ('Name', name),
                                         ('Event', purpose),
                                         ('Date', drupal_ws.date),
                                         ])
                elif purpose == 'OpenModelica Workshop':
                    faculty = OpenModelica_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '4-5 January'),
                                          ('Year', year)
                                          ])
                elif purpose == 'Python Workshop':
                    faculty = Python_Workshop.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', faculty.ws_date),
                                          ('Year', year)
                                          ])
                elif purpose == 'NCCPS 2018 Conference':
                    faculty = NCCPS_2018.objects.get(email=certificate.email)
                    detail = OrderedDict([
					  ('Name', name), ('Event', purpose),
                                          ('Days', '26 November'),
                                          ('Year', year)
                                          ])
                elif purpose == 'SciPy India 2018':
                    faculty = Scipy_2018.objects.get(email=certificate.email)
                    detail = OrderedDict([
					  ('Name', name), ('Event', purpose),
                                          ('Days', '21 - 22 December'),
                                          ('Year', year)
                                          ])
                elif purpose == 'Python 2day Workshop':
                    faculty = Python_Workshop_adv.objects.get(email=certificate.email, purpose='P2W')
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', faculty.ws_date),
                                          ('Year', year)
                                          ])
                elif purpose == 'Python 3day Workshop':
                    faculty = Python_Workshop_BPPy.objects.filter(email=certificate.email, purpose='P3W')
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', [f.ws_date for f in faculty]),
                                          ('Year', year)
                                          ])
                elif purpose == 'Self Learning':
                    self_workshop = Python_Workshop_BPPy.objects.filter(email=certificate.email, purpose='sel')
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', [str(ws.ws_date) for ws in self_workshop]),
                                          ('Year', year)
                                          ])
                elif purpose == "Python Coordinators' Workshop 2019":
                    self_workshop = Python_Workshop_BPPy.objects.filter(email=certificate.email, purpose='PYC')
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', [str(ws.ws_date) for ws in self_workshop]),
                                          ('Year', year)
                                          ])
                elif purpose == 'Scilab Workshop 2019':
                    self_workshop = Scilab_Workshop_2019.objects.get(email=certificate.email, purpose='SCI')
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', self_workshop.ws_date),
                                          ('Year', year)
                                          ])
                elif purpose == 'Scilab Workshop 2019, IIT Bombay(Support)':
                    self_workshop = ScilabSupport.objects.filter(email=certificate.email, purpose='SSS')
                    if self_workshop:
                        purpose = "{0} for the Scilab Workshop 2019, IIT Bombay".format([str(ws.role) for ws in self_workshop])
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '04 May'),
                                          ('Year', year)
                                          ])
                elif purpose == 'Python Workshop 2019, IIT Bombay(Support)':
                    self_workshop = PythonSupport.objects.filter(email=certificate.email, purpose='PSS')
                    if self_workshop:
                        purpose = "{0} for the Python Workshop 2019, IIT Bombay".format([str(ws.role) for ws in self_workshop])
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '22 June'),
                                          ('Year', year)
                                          ])
                elif purpose == 'Linux Workshop 2019, IIT Bombay(Support)':
                    self_workshop = LinuxSupport.objects.filter(email=certificate.email, purpose='LSS')
                    if self_workshop:
                        purpose = "{0} for the Linux Workshop 2019, IIT Bombay".format([str(ws.role) for ws in self_workshop])
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '23 August'),
                                          ('Year', year)
                                          ])
                elif purpose == "C-C++ Workshop 2020, IIT Bombay(Support)":
                    self_workshop = CPPSupport.objects.filter(email=certificate.email, purpose='CPS')
                    if self_workshop:
                        purpose = "{0} for the C-C++ Workshop 2020, IIT Bombay".format(', '.join([str(ws.role) for ws in self_workshop]))
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '29 February'),
                                          ('Year', year)
                                          ])
                elif purpose == "FOSS Workshop, IIT Bombay(Support)":
                    self_workshop = SupportAll.objects.filter(email=certificate.email, purpose='FSA')
                    if self_workshop:
                        roles = ', '.join([str(ws.role) for ws in self_workshop])
                        foss = ', '.join([str(ws.foss) for ws in self_workshop])
                        date = ', '.join([str(ws.year) for ws in self_workshop])
                        date = '08 February 2020'
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Roles', roles),
                                          ('FOSS', foss),
                                          ('Date', date)
                                          ])
                elif purpose == 'eSim Workshop 2019, IIT Bombay(Support)':
                    self_workshop = EsimSupport.objects.filter(email=certificate.email, purpose='ESS')
                    if self_workshop:
                        purpose = "{0} for the eSim Workshop 2019, IIT Bombay".format([str(ws.role) for ws in self_workshop])
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '21 September'),
                                          ('Year', year)
                                          ])
                elif purpose == 'R Workshop 2019, IIT Bombay(Support)':
                    date = None
                    self_workshop = RSupport.objects.filter(email=certificate.email, purpose='RSS')
                    if self_workshop:
                        purpose = "{0} for the eSim Workshop 2019, IIT Bombay".format([str(ws.role) for ws in self_workshop])
                        date = [str(ws.date) for ws in self_workshop]
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', date),
                                          ('Year', year)
                                          ])
                elif purpose == "FOSSEE Workshop Test Certificate":
                    tests = FOSSWorkshopTest.objects.filter(email=certificate.email, purpose='FWT')
                    foss = None
                    grades = None
                    if tests:
                        foss = [str(f) for f in tests.values_list('foss', flat=True)]
                        grades = [str(g) for g in tests.values_list('grade', flat=True)]
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('FOSS', foss),
                                          ('Grades respectively', grades),
                                          ])
                elif purpose == "FOSSEE Animation Workshop Certificate":
                    users = AnimationParticipant.objects.filter(email=certificate.email)
                    workshops = None
                    days = 0
                    date = None
                    if users:
                        user = users[0]
                        workshops = user.animationworkshop_set.all()
                    if workshops:
                        ws = workshops[0]
                        purpose = "{0}".format(ws.name)
                        days = ws.no_of_days
                        date = ws.date
                    else:
                        name = "Not Verified"
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', days),
                                          ('Date', date)
                                          ])
                elif purpose == "FOSSEE Animation Internship Certificate":
                    users = AnimationInternship.objects.filter(email=certificate.email)
                    if users:
                        user = users[0]
                    detail = OrderedDict([
                                          ('Name', user.student),
                                          ('Institute/University', user.institute),
                                          ('Internship', user.name),
                                          ('Duration', user.duration)
                                          ])
                elif purpose == "FOSSEE Animation Contribution Certificate":
                    users = AnimationContribution.objects.filter(email=certificate.email)
                    if users:
                        user = users[0]
                        topics = users.values_list('name', flat=True)
                        dates = users.values_list('date', flat=True)
                    detail = OrderedDict([
                                          ('Name', user.student),
                                          ('Institute/University', user.institute),
                                          ('Contribution(s)', ', '.join(topics)),
                                          ('Date(s)', ', '.join(dates)),
                                          ])
                elif purpose == 'Python Workshop 2019, IIT Bombay':
                    self_workshop = Pymain.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('college', self_workshop.college),
                                          ('organiser', self_workshop.organiser),
                                          ('Event', purpose),
                                          ('Days', self_workshop.date),
                                          ])
                elif purpose == "Linux Coordinators'  Workshop 2019, IIT Bombay":
                    self_workshop = Linuxcoord.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('college', self_workshop.college),
                                          ('Event', purpose),
                                          ('Days', self_workshop.date),
                                          ])
                elif purpose == "Esim Coordinators' Workshop 2019, IIT Bombay":
                    self_workshop = Esimcoord.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('college', self_workshop.college),
                                          ('Event', purpose),
                                          ('Days', self_workshop.date),
                                          ])
                elif purpose == 'eSim Workshop':
                    faculty = eSim_WS.objects.get(email=certificate.email)
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '11 June'),
                                          ('Year', year)
                                          ])
                elif purpose == 'SciPy India':
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '14 - 16 December'),
                                          ('Year', year)
                                          ])
                elif purpose == 'SciPy India 2016':
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '10 - 11 December'),
                                          ('Year', year)
                                          ])
                elif purpose == 'OpenFOAM Symposium':
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Event', purpose),
                                          ('Days', '27 February'),
                                          ('Year', year)
                                          ])
                elif purpose == 'DrupalCamp Mumbai':
                    drupal_user = Drupal_camp.objects.get(email=certificate.email)
                    DAY = drupal_user.attendance
                    if DAY == 1:
                        day = 'Day 1'
                    elif DAY == 2:
                        day = 'Day 2'
                    elif DAY == 3:
                        day = 'Day 1 and Day 2'
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Attended', day),
                                          ('Event', purpose),
                                          ('Year', year)
                                          ])
                elif purpose == 'FreeEDA Textbook Companion':
                    user_books = Tbc_freeeda.objects.filter(email=certificate.email).values_list('book')
                    books = [book[0] for book in user_books]
                    detail = OrderedDict([
                                          ('Name', name),
                                          ('Participant', 'Yes'),
                                          ('Project', 'FreeEDA Textbook Companion'),
                                          ('Books completed', ','.join(books))])
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
    elif serial_no[0:3] == 'P2W':
        purpose = 'Python 2day Workshop'
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
    elif serial_no[0:3] == 'S17':
        purpose = 'SciPy India 2017'
    elif serial_no[0:3] == 'S18':
        purpose = 'SciPy India 2018'
    elif serial_no[0:3] == 'S19':
        purpose = 'SciPy India 2019'
    elif serial_no[0:3] == 'S20':
        purpose = 'SciPy India'
    elif serial_no[0:3] == 'CFC':
        purpose = 'Complex Fluids Symposium'
    elif serial_no[0:3] == 'sel':
        purpose = 'Self Learning'
    elif serial_no[0:3] == 'SCI':
        purpose = 'Scilab Workshop 2019'
    elif serial_no[0:3] == 'NC8':
        purpose = 'NCCPS 2018 Conference'
    elif serial_no[0:3] == 'PYC':
        purpose = "Python Coordinators' Workshop 2019"
    elif serial_no[0:3] == 'FEL':
        purpose = "FOSSEE SUMMER FELLOWSHIP 2019"
    elif serial_no[0:3] == 'FL2':
        purpose = "FOSSEE SUMMER FELLOWSHIP 2020"
    elif serial_no[0:3] == 'F21':
        purpose = "FOSSEE SUMMER FELLOWSHIP 2021"
    elif serial_no[0:3] == 'IT2':
        purpose = "FOSSEE SUMMER INTERNSHIP 2021"
    elif serial_no[0:3] == 'IN2':
        purpose = "FOSSEE INTERNSHIP 2020"
    elif serial_no[0:3] == 'FEQ':
        purpose = "FOSSEE SUMMER FELLOWSHIP 2019 Screening Task"
    elif serial_no[0:3] == 'OSD':
        purpose = 'Osdag Workshop 2019, IIT Bombay'
    elif serial_no[0:3] == 'PYM':
        purpose = 'Python Workshop 2019, IIT Bombay'
    elif serial_no[0:3] == 'LXC':
        purpose = "Linux Coordinators'  Workshop 2019, IIT Bombay"
    elif serial_no[0:3] == 'ESC':
        purpose = "Esim Coordinators' Workshop 2019, IIT Bombay"
    elif serial_no[0:3] == 'SSS':
        purpose = "Scilab Workshop 2019, IIT Bombay(Support)"
    elif serial_no[0:3] == 'PSS':
        purpose = "Python Workshop 2019, IIT Bombay(Support)"
    elif serial_no[0:3] == 'LSS':
        purpose = "Linux Workshop 2019, IIT Bombay(Support)"
    elif serial_no[0:3] == 'ESS':
        purpose = "eSim Workshop 2019, IIT Bombay(Support)"
    elif serial_no[0:3] == 'CPS':
        purpose = "C-C++ Workshop 2020, IIT Bombay(Support)"
    elif serial_no[0:3] == 'FSA':
        purpose = "FOSS Workshop, IIT Bombay(Support)"
    elif serial_no[0:3] == 'RSS':
        purpose = "R Workshop 2019, IIT Bombay(Support)"
    elif serial_no[0:3] == 'FAC':
        purpose = "FOSSEE Animation Workshop Certificate"
    elif serial_no[0:3] == 'FAI':
        purpose = "FOSSEE Animation Internship Certificate"
    elif serial_no[0:3] == 'FAO':
        purpose = "FOSSEE Animation Contribution Certificate"
    elif serial_no[0:3] == 'FWT':
        purpose = "FOSSEE Workshop Test Certificate"
    elif serial_no[0:3] == 'WIC':
        purpose = "FOSSEE WINTER INTERNSHIP 2019"
    elif serial_no[0:3] == 'FD0':
        purpose = 'FDP 2020, FOSSEE'
    elif serial_no[0:3] == 'OFM':
        purpose = 'OpenFOAM 2020, FOSSEE'
    elif serial_no[0:3] == 'PCC':
        purpose = 'Python Course Certificate'
    elif serial_no[0:3] == 'SCH':
        purpose = 'Scilab Toolbox Hackathon 2020'
    elif serial_no[0:3] == 'RAP':
        purpose = 'R Workshop 2020'
    elif serial_no[0:3] == 'SYH':
        purpose = 'Synfig Animation Hackathon 2020'
    elif serial_no[0:3] == 'MAP':
        purpose = 'Mapathon 2020'
    elif serial_no[0:3] == 'MP2':
        purpose = 'Mapathon 2022'
    elif serial_no[0:3] == 'EMC':
        purpose = 'eSim Marathon 2021'
    elif serial_no[0:3] == 'EM2':
        purpose = 'eSim Marathon 2022'
    elif serial_no[0:3] == 'MSM':
        purpose = 'Mixed Signal Marathon 2022'

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
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'https://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
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
            qrcode = 'https://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name, 'day': day, 'serial_key': short_key}
            certificate = create_drupal_certificate(certificate_path, details,
                                                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                                            serial_no=serial_no,
                                            counter=1, workshop=workshop,
                                            paper=paper,
                                            serial_key=serial_key,
                                            short_key=short_key)
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

        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                                              day=name['day'],
                                              serial_key=name['serial_key'],
                                              qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
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
        author = user.author
        purpose = user.purpose
        year = '15'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
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
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              book=name['book'], author=name['author'], college=name['college'],
                                              serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
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
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
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

        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
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
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
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

        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
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


def osdag_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/osdag_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        ws_date = request.POST.get('ws_date')
        ws_date = datetime.strptime(ws_date, '%Y-%m-%d')
        paper = None
        workshop = None
        if type == 'P':
            users = Osdag_WS.objects.filter(email=email, start_date=ws_date)
            if not users:
                context["notregistered"] = 1
                return render_to_response('osdag_workshop_download.html',
                                          context, context_instance=ci)
            else:
                user = users[0]
        name = user.name
        purpose = user.purpose
        year = user.start_date.year
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, str(year)[2:], hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        details = {
            'name': name, 'year': year,
            'college': user.college,
            'start_date': datetime.strftime(user.start_date, '%d %B'),
            'end_date': datetime.strftime(user.end_date, '%d %b')
        }
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details.update({'serial_key': old_user.short_key})
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
                    details.update({'serial_key': short_key})
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(short_key)
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


def create_osdag_workshop_certificate(certificate_path, details, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        template = 'template_OWS2016Pcertificate'
        download_file_name = 'OWS%sPcertificate.pdf' % (details['year'])
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key = details['serial_key'], qr_code=qrcode, college=details['college'],
                date='%s %s' % (details['start_date'], details['year']))
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
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
        status = 'successfully completed' if user.status else 'participated in'
        ws_date = user.date
        ws_date = datetime.strftime(ws_date, '%d %B %Y')
        year = ws_date[-2:]
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'https://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {
            'name': name, 'serial_key': old_user.short_key,
            'status': status, 'ws_date': ws_date
            }
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
            qrcode = 'https://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {
            'name': name,  'serial_key': short_key,
            'status': status, 'ws_date': ws_date
            }
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


def create_drupal_workshop_certificate(certificate_path, detail, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        year = detail["ws_date"][-4:]
        download_file_name = None
        template = 'template_DWS2018Pcertificate'
        download_file_name = 'DWS%sPcertificate.pdf'% year

        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=detail['name'].title(),
                                              serial_key=detail['serial_key'], qr_code=qrcode,
                                              status=detail['status'], ws_date=detail['ws_date']
                                              )
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
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


def create_fossee_internship_cerificate(
      certificate_path, name, qrcode,
      wtype, paper, internship_project_duration, student_edu_detail,
      student_institute_detail, superviser_name_detail,
      workshop, file_name):
    error = False
    try:
        download_file_name = None
        year = internship_project_duration.split()[2]
        if wtype == 'P':
            template = 'template_FIC2016Pcertificate'
            download_file_name = 'FIC2016Pcertificate.pdf'
        elif wtype == 'A':
            template = 'template_FIC2016Acertificate'
            if year == '2018':
              template = 'template_FIC2018Acertificate'
            download_file_name = 'FIC{0}Acertificate.pdf'.format(year)

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if wtype == 'P':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        elif wtype == 'A':
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
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          wtype, file_name)
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
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
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
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(short_key)
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
def python_workshop_feedback(request):
   return render_to_response('python_workshop_feedback.html')

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
        ws_date = request.POST.get('ws_date').split('-')
        ws_date[1] = calendar.month_name[int(ws_date[1])]
        ws_date.reverse()
        ws_date = ' '.join(ws_date)
        paper = None
        workshop = None
        if type == 'P':
            if format=='iscp':
                user = Python_Workshop.objects.filter(email=email, ws_date=ws_date)
            elif format=='sel':
                user = Python_Workshop_BPPy.objects.filter(email=email, purpose=format, ws_date=ws_date)
            elif format=='P2W':
                user = Python_Workshop_adv.objects.filter(email=email, purpose=format, ws_date=ws_date)
            else:
                user = Python_Workshop_BPPy.objects.filter(email=email, ws_date=ws_date)
            if not user:
                context["notregistered"] = 1
                return render_to_response('python_workshop_download.html',
                        context, context_instance=ci)
            else:
                user = user[0]
        if user.paper == 'F':
            context["failed"] = 1
            return render_to_response('python_workshop_download.html',
                        context, context_instance=ci)
        name = user.name
        college = user.college
        purpose = user.purpose
        ws_date = user.ws_date
        paper = user.paper
        is_coordinator = user.is_coordinator
        year = ws_date.split()[-1][2:]
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
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
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(short_key)
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
        if format=='iscp': # use templates based on 3day, 2day or 1day workshop
            if is_coordinator:
                template = 'coordinator_template_PWS2017Pcertificate'
            else:
                template = 'template_PWS2017Pcertificate'
        elif format=='sel':
            template = '3day_template_self_certificate'
        elif format=='P2W':
            if is_coordinator:
                template = '2day_coordinator_template_PWS2017Pcertificate'
            else:
                template = '2day_template_PWS2017Pcertificate'
        else:
            if is_coordinator:
                template = '3day_coordinator_template_PWS2017Pcertificate'
            else:
                template = '3day_template_PWS2017Pcertificate'

        download_file_name = 'PWS%sPcertificate.pdf' % ws_date.split()[-1]
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'], qr_code=qrcode, college=college, paper=paper, ws_date=ws_date)
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


@csrf_exempt
def scipy_feedback_2017(request):
   return render_to_response('scipy_feedback_2017.html')

@csrf_exempt
def scipy_download_2017(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2017/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        attendee_type = request.POST.get('type')
        user = Scipy_2017.objects.filter(email=email, attendee_type=attendee_type)
        if not user:
            context["notregistered"] = 1
            return render_to_response('scipy_download_2017.html', context, context_instance=ci)
        elif len(user) > 1:
            context["duplicate"] = True
            return render_to_response('scipy_download_2017.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        purpose = user.purpose
        paper = user.paper
        year = '17'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')


        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_certificate_2017(certificate_path, details, qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                #context['error'] = False
                return certificate[0]
                #render_to_response( 'scipy_download_2017.html', context)
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_certificate_2017(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0] #render(request, 'scipy_download_2017.html')

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download_2017.html', context, ci)
    context['message'] = ''
    return render_to_response('scipy_download_2017.html', context, ci)


@csrf_exempt
def create_scipy_certificate_2017(certificate_path, name, qrcode, attendee_type, paper, workshop, file_name):
    error = False
    try:
        template = 'template_SPC2017%scertificate' % attendee_type
        download_file_name = 'SPC2017%scertificate.pdf' % attendee_type
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if attendee_type == 'P' or attendee_type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                        serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, attendee_type, file_name)

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


#NCCPS_2018 Starts here

@csrf_exempt
def nccps_feedback_2018(request):
   return render_to_response('nccps_feedback_2018.html')


@csrf_exempt
def nccps_download_2018(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/nccps_template_2018/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        attendee_type = request.POST.get('type')
        user = NCCPS_2018.objects.filter(email=email, attendee_type=attendee_type)
        if not user:
            context["notregistered"] = 1
            return render_to_response('nccps_download_2018.html', context, context_instance=ci)
        elif len(user) > 1:
            context["duplicate"] = True
            return render_to_response('nccps_download_2018.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        purpose = user.purpose
        paper = user.paper
        year = '18'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')


        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_nccps_certificate_2018(certificate_path, details, qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                #context['error'] = False
                return certificate[0]
                #render_to_response( 'scipy_download_2017.html', context)
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_nccps_certificate_2018(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0] #render(request, 'scipy_download_2017.html')

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('nccps_download_2018.html', context, ci)
    context['message'] = ''
    return render_to_response('nccps_download_2018.html', context, ci)


@csrf_exempt
def create_nccps_certificate_2018(certificate_path, name, qrcode, attendee_type, paper, workshop, file_name):
    error = False
    try:
        template = 'template_NCCPS2018%scertificate' % attendee_type
        download_file_name = 'NCCPS2018%scertificate.pdf' % attendee_type
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if attendee_type == 'P' or attendee_type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                        serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, attendee_type, file_name)

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

#NCCPS 2018 Ends Here



#Scipy India 2018 Starts here

@csrf_exempt
def scipy_feedback_2018(request):
   return render_to_response('scipy_feedback_2018.html')


@csrf_exempt
def scipy_download_2018(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2018/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        attendee_type = request.POST.get('type')
        user = Scipy_2018.objects.filter(email=email, attendee_type=attendee_type)
        if not user:
            context["notregistered"] = 1
            return render_to_response('scipy_download_2018.html', context, context_instance=ci)
        elif len(user) > 1:
            context["duplicate"] = True
            return render_to_response('scipy_download_2018.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        purpose = user.purpose
        paper = user.paper
        year = '18'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')


        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_certificate_2018(certificate_path, details, qrcode, attendee_type, paper, workshop, file_name)
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_certificate_2018(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download_2018.html', context, ci)
    context['message'] = ''
    return render_to_response('scipy_download_2018.html', context, ci)


@csrf_exempt
def create_scipy_certificate_2018(certificate_path, name, qrcode, attendee_type, paper, workshop, file_name):
    error = False
    try:
        template = 'template_SPC2018%scertificate' % attendee_type
        download_file_name = 'SPC2018%scertificate.pdf' % attendee_type
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if attendee_type == 'P' or attendee_type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                        serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, attendee_type, file_name)

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

#Scipy India 2018 Ends Here

@csrf_exempt
def contact(request):
    """
This view function is used to submit contact form, It used Google's reCAPTCHA validation
"""

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            ws_date = form.cleaned_data['date']
            category = form.cleaned_data['category']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            msg = "Name : {0} \n Workshop Date:{1} \n Category:{2} \n Message:{3}".format(name,ws_date,category,message)
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                      'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                      'response': recaptcha_response
                      }
            data = urllib.urlencode(values)
            req =  urllib2.Request(url, data=data)
            response = urllib2.urlopen(req)
            result = json.load(response)
            if result['success']:
                done = sending_emails.send_email(subject,from_email,msg)
                if done:
                    return HttpResponse('We have received your message and would like to thank you for writing to us. We will reply by email as soon as possible.')
                else:
                    return HttpResponse('Email your query/issue to  certificates[at]fossee[dot]in')
            else:
                return render(request,'contact_us.html',{'form':form})
        else:
            return render(request,'contact_us.html',{'form':form})
    else:
        form = ContactForm()
    return render(request,'contact_us.html',{'form':form})

@csrf_exempt
def st_feedback_2019(request):
   return render_to_response('scilab_st_feedback_2019.html')

@csrf_exempt
def st_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        format = request.POST.get('format', 'scilab')
        ws_date = request.POST.get('ws_date').split('-')
        ws_date[1] = calendar.month_name[int(ws_date[1])]
        ws_date.reverse()
        ws_date = ' '.join(ws_date)
        paper = None
        workshop = None
        organiser = 'IIT Bombay'
        if format=='scilab':
       	    user = Scilab_Workshop_2019.objects.filter(email=email, ws_date=ws_date)
            if user:
                organiser = user[0].organiser
                organiser = organiser.replace('&', 'and')
        else:
            user = Python_Workshop_BPPy.objects.filter(email=email, ws_date=ws_date)
        if not user:
            context["notregistered"] = 1
            return render_to_response('st_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        if user.paper == 'F':
            context["failed"] = 1
            return render_to_response('st_workshop_download.html',
                        context, context_instance=ci)
        name = user.name
        college = user.college
        college = college.replace('&', 'and')
        purpose = user.purpose
        ws_date = user.ws_date
        paper = user.paper
        is_coordinator = user.is_coordinator
        year = ws_date.split()[-1][2:]
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_st_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name, college, ws_date,
                    organiser, is_coordinator,format)
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
            certificate = create_st_workshop_certificate(certificate_path, details,
                    qrcode, type, paper, workshop, file_name, college, ws_date,
                    organiser, is_coordinator,format)
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
            return render_to_response('st_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('st_workshop_download.html', context, ci)


def create_st_workshop_certificate(certificate_path, name, qrcode, type, paper,
                                   workshop, file_name, college, ws_date,
                                   organiser='IIT Bombay',
                                   is_coordinator=False,format='scilab'):
    error = False
    err = None
    try:
        download_file_name = None
        if format=='scilab': # use templates based on workshop
            if is_coordinator:
                template = 'template_STT'
            else:
                template = 'template_STT'
            if ws_date == '04 May 2019':
                template = 'template_STT4thmay'
        else:
            if is_coordinator:
                template = '3day_coordinator_template_PWS2017Pcertificate'
                if ws_date == '25 May 2019':
                    template = 'template_STTPyCoord'
                    bg = 'bg25'
                if ws_date == '08 June 2019':
                    template = 'template_STTPyCoord'
                    bg = 'bg8'
            else:
                template = '3day_template_PWS2017Pcertificate'

        download_file_name = 'PWS%sPcertificate.pdf' % ws_date.split()[-1]
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if ws_date == '04 May 2019' and format == 'scilab':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    organiser=organiser,
                    serial_key=name['serial_key'], qr_code=qrcode,
                    college=college, paper=paper, ws_date=ws_date)
        elif (ws_date == '08 June 2019' or ws_date == '25 May 2019') and format == 'py19':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode, bg=bg,
                    college=college)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode,
                    college=college, paper=paper, ws_date=ws_date)
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


def fellowship2019_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fellowship2019/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Fellow2019.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('fellowship2019_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        start_date = user.start_date
        end_date = user.end_date
        internship_project_duration = '\hspace{3} {0} \hspace{2} to \hspace{2} {1}'.format(start_date, end_date, '{0.02cm}', '{0.15cm}')
        student_institute_detail=(user.institute).title()
        student_institute_detail = student_institute_detail.replace('&', 'and')
        worked_on = user.title
        worked_on = worked_on.replace('&', 'and')
        year = '19'
        id =  int(user.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fellowship2019_certificate(certificate_path,
                    details, qrcode, internship_project_duration,
                    student_institute_detail, file_name, worked_on)
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
            certificate = create_fellowship2019_certificate(certificate_path,
                    details, qrcode, internship_project_duration,
                    student_institute_detail, file_name, worked_on)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fellowship2019_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fellowship2019_certificate_download.html', context, ci)


def create_fellowship2019_certificate(certificate_path, details, qrcode,
        internship_project_duration, student_institute_detail, file_name, worked_on):
    error = False
    try:
        template = 'template_fellow2019Pcertificate'
        download_file_name = 'FEL2019Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                internship_project_duration=internship_project_duration,
                student_institute_detail=student_institute_detail,
                worked_on = worked_on)
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

        error = True
    return [None, error]


def osdag2019_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/osdag2019/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Osdag2019.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('osdag2019_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        year = '19'
        id =  int(user.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_osdag2019_certificate(certificate_path,
                          details, qrcode, file_name)
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
            qrcode = 'https://fossee.in/certificates/verify/{0} '.format(short_key)
            details = {'name': name,  'serial_key': short_key}
            certificate = create_osdag2019_certificate(certificate_path,
                    details, qrcode, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('osdag2019_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('osdag2019_certificate_download.html', context, ci)


def create_osdag2019_certificate(certificate_path, details, qrcode, file_name):
    error = False
    try:
        template = 'template_osdag2019Pcertificate'
        download_file_name = 'OSD2019Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        _type = 'P'
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def pymain_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = Pymain.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('st_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        organiser = user.organiser
        college = user.college
        college = college.replace('&', 'and')
        organiser = organiser.replace('&', 'and')
        purpose = user.purpose
        ws_date = user.date
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_pythonmain_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, organiser, college, ws_date)
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
            certificate = create_pythonmain_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, organiser, college, ws_date)
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
            return render_to_response('pythonmain_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('pythonmain_workshop_download.html', context, ci)


def create_pythonmain_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, organiser, college, ws_date):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_STTPyMain'

        download_file_name = 'PWS%sPcertificate.pdf' % ws_date.split()[-1]
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                organiser=organiser, serial_key=name['serial_key'],
                qr_code=qrcode, college=college)
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


def linuxcoord_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = Linuxcoord.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('linuxcoord_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        college = user.college
        college = college.replace('&', 'and')
        purpose = user.purpose
        ws_date = user.date
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_linuxcoord_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, ws_date)
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
            certificate = create_linuxcoord_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, ws_date)
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
            return render_to_response('linuxcoord_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('linuxcoord_workshop_download.html', context, ci)


def create_linuxcoord_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, ws_date):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_linuxcoord'

        download_file_name = 'PWS%sPcertificate.pdf' % ws_date.split()[-1]
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, college=college)
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


def esimcoord_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = Esimcoord.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('esimcoord_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        college = user.college
        college = college.replace('&', 'and')
        purpose = user.purpose
        ws_date = user.date
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esimcoord_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, ws_date)
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
            certificate = create_esimcoord_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, ws_date)
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
            return render_to_response('esimcoord_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esimcoord_workshop_download.html', context, ci)


def create_esimcoord_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, ws_date):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_esimcoord'

        download_file_name = 'PWS%sPcertificate.pdf' % ws_date.split()[-1]
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, college=college)
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


def scilabsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = ScilabSupport.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('scilabsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_scilabsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            certificate = create_scilabsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            return render_to_response('scilabsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('scilabsupport_workshop_download.html', context, ci)


def create_scilabsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_scilabstaff'

        download_file_name = 'PWS2019Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def pythonsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = PythonSupport.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('pythonsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_pythonsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            certificate = create_pythonsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            return render_to_response('pythonsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('pythonsupport_workshop_download.html', context, ci)


def create_pythonsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_pythonstaff'

        download_file_name = 'PWS2019Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def linuxsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = LinuxSupport.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('linuxsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_linuxsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            certificate = create_linuxsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            return render_to_response('linuxsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('linuxsupport_workshop_download.html', context, ci)


def create_linuxsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_linuxstaff'

        download_file_name = 'PWS2019Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def rsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        rerun = request.POST.get('rerun', 0)
        user = RSupport.objects.filter(email=email, rerun=rerun)
        if not user:
            context["notregistered"] = 1
            return render_to_response('rsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '19'
        date = user.date
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_rsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role, date)
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
            certificate = create_rsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role, date)
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
            return render_to_response('rsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('rsupport_workshop_download.html', context, ci)


def create_rsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role, date):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_rstaff'

        download_file_name = 'PWS2019Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'], date=date,
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def cppsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = CPPSupport.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('cppsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_cppsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            certificate = create_cppsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            return render_to_response('cppsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('cppsupport_workshop_download.html', context, ci)


def create_cppsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_cppstaff'

        download_file_name = 'CWS2020Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def esimsupport_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    paper = None
    workshop = None
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        user = EsimSupport.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('esimsupport_workshop_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esimsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            certificate = create_esimsupport_workshop_certificate(certificate_path, details,
                    qrcode, type, file_name, college, rcid, role)
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
            return render_to_response('esimsupport_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esimsupport_workshop_download.html', context, ci)


def create_esimsupport_workshop_certificate(certificate_path, name, qrcode, type,
        file_name, college, rcid, role):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_esimstaff'

        download_file_name = 'PWS2019Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
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


def eqfellowship2019_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fellowship2019/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = EqFellow2019.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('eqfellowship2019_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        student_institute_detail=user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        worked_on = user.floss
        worked_on = worked_on.replace('&', 'and')
        year = '19'
        id =  int(user.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_eqfellowship2019_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name, worked_on)
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
            certificate = create_eqfellowship2019_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name, worked_on)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('eqfellowship2019_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('eqfellowship2019_certificate_download.html', context, ci)


def create_eqfellowship2019_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name, worked_on):
    error = False
    try:
        template = 'template_eqfellow2019Pcertificate'
        download_file_name = 'FEL2019Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                student_institute_detail=student_institute_detail,
                worked_on = worked_on)
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

        error = True
    return [None, error]

#Scipy India 2019 Starts here

@csrf_exempt
def scipy_feedback_2019(request):
   return render_to_response('scipy_feedback_2019.html')


@csrf_exempt
def scipy_download_2019(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2019/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        attendee_type = request.POST.get('type')
        user = Scipy_2019.objects.filter(email=email, attendee_type=attendee_type)
        if not user:
            context["notregistered"] = 1
            return render_to_response('scipy_download_2019.html', context, context_instance=ci)
        elif len(user) > 1:
            context["duplicate"] = True
            return render_to_response('scipy_download_2019.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        purpose = user.purpose
        paper = user.paper
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')


        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_certificate_2019(certificate_path, details, qrcode, attendee_type, paper, workshop, file_name)
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_certificate_2019(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_download_2019.html', context, ci)
    context['message'] = ''
    return render_to_response('scipy_download_2019.html', context, ci)


@csrf_exempt
def create_scipy_certificate_2019(certificate_path, name, qrcode, attendee_type, paper, workshop, file_name):
    error = False
    try:
        template = 'template_SPC2019%scertificate' % attendee_type
        download_file_name = 'SPC2019%scertificate.pdf' % attendee_type
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if attendee_type == 'P' or attendee_type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                        serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, attendee_type, file_name)

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

#Scipy India 2019 Ends Here
def animation_contribution_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/animation/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        topic = request.POST.get('topic', None)
        user = AnimationContribution.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('animation_contribution_certificate_download.html', context, context_instance=ci)
        elif len(user) > 1 and topic is None:
            context["multicontribution"] = 2
            context["email"] = email
            context["contributions"] = user.values_list('name', flat=True)
            return render_to_response('animation_contribution_certificate_download.html', context, context_instance=ci)
        else:
            if topic is None:
                user = user[0]
            else:
                user = user.get(name=topic)
        name = (user.student).title()
        purpose = user.purpose
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        contribution = user.name
        contribution_name = (contribution).replace('&', 'and')
        date = user.date

        year = str(user.year)[:2]
        id =  int(user.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_animation_contribution_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    contribution_name, date)
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
            certificate = create_animation_contribution_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    contribution_name, date)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('animation_contribution_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('animation_contribution_certificate_download.html', context, ci)


def create_animation_contribution_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name, contribution_name, date):
    error = False
    try:
        template = 'template_animationCcertificate'
        download_file_name = 'FAC1920Ccertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                student_institute_detail=student_institute_detail,
                contribution_name=contribution_name, date=date)
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
        error = True
    return [None, error]


def animation_internship_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/animation/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = AnimationInternship.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('animation_internship_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.student).title()
        purpose = user.purpose
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        internship = user.name
        internship_name = (internship).replace('&', 'and')
        duration = user.duration

        year = str(user.year)[:2]
        id =  int(user.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_animation_internship_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    internship_name, duration)
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
            certificate = create_animation_internship_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    internship_name, duration)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('animation_internship_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('animation_internship_certificate_download.html', context, ci)


def create_animation_internship_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name, internship_name, duration):
    error = False
    try:
        template = 'template_animationIcertificate'
        download_file_name = 'FAC1920Icertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                student_institute_detail=student_institute_detail,
                internship_name=internship_name, duration=duration)
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

        error = True
    return [None, error]


def animation_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/animation/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = AnimationParticipant.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('animation_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = 'FAC'
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        workshop = user.animationworkshop_set.all()[0]
        workshop_name = (workshop.name).replace('&', 'and')
        workshop_venue = (workshop.venue).replace('&', 'and')
        duration = workshop.no_of_days
        date = workshop.date

        year = '19'
        id =  int(user.id) + int(workshop.id)
        _type = 'P'
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_animation_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    workshop_name, workshop_venue, duration, date)
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
            certificate = create_animation_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    workshop_name, workshop_venue, duration, date)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('animation_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('animation_certificate_download.html', context, ci)


def create_animation_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name, workshop_name, workshop_venue,
        duration, date):
    error = False
    try:
        template = 'template_animationPcertificate'
        download_file_name = 'FAC2019Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                student_institute_detail=student_institute_detail,
                workshop_name=workshop_name, workshop_venue=workshop_venue,
                duration=duration, date=date)
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

        error = True
    return [None, error]


def foss_workshop_test_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/foss_workshop_test_template/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        foss = request.POST.get('foss')
        user = FOSSWorkshopTest.objects.filter(email=email, foss=foss)
        if not user:
            context["notregistered"] = 1
            return render_to_response('foss_workshop_test_download.html',
                        context, context_instance=ci)
        else:
            user = user[0]
        name = user.name.strip()
        grade = user.grade.strip()
        purpose = user.purpose.strip()
        year = '19'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_foss_workshop__test_certificate(
                    certificate_path, details, qrcode, type, file_name, foss, grade)
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
            certificate = create_foss_workshop_test_certificate(certificate_path,
                    details, qrcode, type, file_name, foss, grade)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, workshop=None,
                            paper=None, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('foss_workshop_test_download.html',
                                      context, ci)
    context['message'] = ''
    return render_to_response('foss_workshop_test_download.html', context, ci)


def create_foss_workshop_test_certificate(certificate_path, name, qrcode, type,
        file_name, foss, grade):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_test'

        download_file_name = 'FWT2020Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'],
                qr_code=qrcode, foss=foss, grade=grade)
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


def winter_internship_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/winter-internship/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Wintership.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('winter_internship_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = 'WIC'
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        topic = user.topic
        topic = topic.replace('&', 'and')
        start_date = user.start_date
        end_date = user.end_date

        year = '19'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_wintership_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    topic, start_date, end_date)
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
            certificate = create_wintership_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name,
                    topic, start_date, end_date)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('winter_internship_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('winter_internship_certificate_download.html', context, ci)


def create_wintership_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name, topic, start_date, end_date):
    error = False
    try:
        template = 'templateWI'
        download_file_name = 'WIC2019Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=student_institute_detail,
                topic=topic, start_date=start_date, end_date=end_date)
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

        error = True
    return [None, error]


def fdp_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/FDP/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = FDP.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('fdp_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = 'FD0'
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')

        year = '20'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fdp_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name)
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
            certificate = create_fdp_certificate(certificate_path,
                    details, qrcode, student_institute_detail, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fdp_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fdp_certificate_download.html', context, ci)


def create_fdp_certificate(certificate_path, details, qrcode,
        student_institute_detail, file_name):
    error = False
    try:
        template = 'templateFDP'
        download_file_name = 'FDP2020Pcertificate.pdf'

        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=student_institute_detail)
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

        error = True
    return [None, error]

def intern20_certificate_download(request):
    return fellow20_certificate_download(request, kind='intern')

def fellow20_certificate_download(request, kind='fellow'):
    context = {'kind': kind}
    if kind == 'intern':
        context['heading'] = 'INTERNSHIP'
    else:
        context['heading'] = 'FELLOWSHIP'

    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fellow20/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Fellow2020.objects.filter(email=email, _type=kind)
        if not user:
            context["notregistered"] = 1
            return render_to_response('fellow20_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        topic = (user.title).replace('&', 'and')
        start_date = user.start_date
        end_date = user.end_date
        mode = user.mode
        mode_def = user.mode_def

        year = '20'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fellow20_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    start_date, end_date, mode, mode_def, file_name, kind)
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
            certificate = create_fellow20_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    start_date, end_date, mode, mode_def, file_name, kind)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fellow20_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fellow20_certificate_download.html', context, ci)


def create_fellow20_certificate(certificate_path, details, qrcode,
        student_institute_detail, topic, start_date, end_date, mode, mode_def,
        file_name, kind):
    error = False
    try:
        if kind == 'fellow':
            template = 'template20'
            download_file_name = 'FEL2020Pcertificate.pdf'
        elif kind == 'intern':
            template = 'templateI20'
            download_file_name = 'INT2020Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=student_institute_detail, topic=topic, mode=mode,
                start_date=start_date, end_date=end_date, mode_def=mode_def)
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
        error = True
    return [None, error]


def python_certification_download(request):
    context = {'years': years, 'months': months}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/python_workshop_template/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        month = request.POST.get('month')
        year = int(request.POST.get('year'))
        user = PythonCertification.objects.filter(email=email, month=month, year=year)
        if not user:
            context["notregistered"] = 1
            return render_to_response('python_certification_download.html',
                                       context, context_instance=ci)
        else:
            user = user[0]
            if user.grade == 'F':
                context["failed"] = 1
                return render_to_response('python_workshop_download.html',
                                           context, context_instance=ci)
        _type = 'P'
        name = user.name
        institute = user.institute
        institute = institute.replace('&', 'and')
        purpose = user.purpose
        grade = user.grade
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_python_certificate(certificate_path, details,
                    qrcode, _type, grade, file_name, institute, month, year)
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
            certificate = create_python_certificate(certificate_path, details,
                    qrcode, _type, grade, file_name, institute, month, year)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('python_certification_download.html', context, ci)
    context['message'] = ''
    return render_to_response('python_certification_download.html', context, ci)


def create_python_certificate(certificate_path, name, qrcode, _type, grade,
        file_name, institute, month, year):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_certification'
        download_file_name = 'PCC{0}Pcertificate.pdf'.format(year)
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'], qr_code=qrcode,
                institute=institute, grade=grade, month=month, year=year)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def openfoam_certificate_download(request):
    context = {'years': years, 'months': months}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/openfoam_symposium_template_2016/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = CertificateUser.objects.filter(email=email, purpose='OFM')
        if not user:
            context["notregistered"] = 1
            return render_to_response('openfoam_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_openfoam_certificate(certificate_path, details,
                    qrcode, _type, file_name)
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
            certificate = create_openfoam_certificate(certificate_path, details,
                    qrcode, _type, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('openfoam_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('openfoam_certificate_download.html', context, ci)


def create_openfoam_certificate(certificate_path, name, qrcode, _type, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_OFM'
        download_file_name = 'OFM2020Pcertificate.pdf'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def synfig_hackathon_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/syn-hackathon/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = SynfigHackathon.objects.filter(email=email, purpose='SYH')
        if not user:
            context["notregistered"] = 1
            return render_to_response('synfig_hackathon_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        first_name = user.first_name
        last_name = user.last_name
        name = '{0} {1}'.format(first_name, last_name)
        ctype = user.ctype
        position = user.position
        team = user.team
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_synfig_hackathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, position, file_name)
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
            certificate = create_synfig_hackathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, position, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('synfig_hackathon_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('synfig_hackathon_certificate_download.html', context, ci)


def create_synfig_hackathon_certificate(certificate_path, details, qrcode, _type,
                                        ctype, team, position, file_name):
    error = False
    err = None
    try:
        download_file_name = 'SYH2020certificate.pdf'
        if ctype == 'champ':
            template = 'template_ch'
        elif ctype == 'conso':
            template = 'template_co'
        elif ctype == 'recog':
            template = 'template_reco'
        else:
            template = 'template_pa'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if ctype == 'champ':
            content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode, team=team,
                position=position)
        else:
            content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode, team=team)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def mapathon_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/mapathon/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Mapathon.objects.filter(email=email, purpose='MAP')
        if not user:
            context["notregistered"] = 1
            return render_to_response('mapathon_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        ctype = user.ctype
        team = user.team
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_mapathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, file_name)
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
            certificate = create_mapathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('mapathon_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('mapathon_certificate_download.html', context, ci)


def mapathon2_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/mapathon2/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Mapathon.objects.filter(email=email, purpose='MP2')
        if not user:
            context["notregistered"] = 1
            return render_to_response('mapathon2_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        ctype = user.ctype
        team = user.team
        purpose = user.purpose
        year = '22'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_mapathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, file_name)
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
            certificate = create_mapathon_certificate(certificate_path, details,
                    qrcode, _type, ctype, team, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('mapathon2_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('mapathon2_certificate_download.html', context, ci)

def create_mapathon_certificate(certificate_path, details, qrcode, _type,
                                ctype, team, file_name):
    error = False
    err = None
    try:
        download_file_name = 'MAP20222certificate.pdf'
        if ctype == 'champ':
            template = 'template_ch'
        elif ctype == 'recog':
            template = 'template_reco'
        elif ctype == 'ment':
            template = 'template_ment'
        else:
            template = 'template_pa'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
            serial_key=details['serial_key'], qr_code=qrcode, team=team)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def hackathon_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/hackathon/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = ScilabHackathon.objects.filter(email=email, purpose='SCH')
        if not user:
            context["notregistered"] = 1
            return render_to_response('hackathon_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        interfaced = user.interfaced
        ctype = user.ctype
        team = user.team
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_hackathon_certificate(certificate_path, details,
                    qrcode, _type, interfaced, ctype, team, file_name)
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
            certificate = create_hackathon_certificate(certificate_path, details,
                    qrcode, _type, interfaced, ctype, team, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('hackathon_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('hackathon_certificate_download.html', context, ci)


def create_hackathon_certificate(certificate_path, details, qrcode, _type,
                                 interfaced, ctype, team, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        if ctype == 'champ':
            template = 'template_ch'
        elif ctype == 'conso':
            template = 'template_co'
        else:
            template = 'template_pa'
        download_file_name = 'SCIH2020certificate.pdf'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode, team=team,
                interfaced=interfaced)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def vlabappre_certificate_download(request):
    if request.method == 'POST':
        return rappre_certificate_download(request)
    context= {}
    ci = RequestContext(request)
    return render_to_response('vlab_certificate_download.html', context, ci)


def rappre_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/st_workshop_template/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        foss = request.POST.get('foss').strip()
        user = RAppre.objects.filter(email=email, foss=foss, purpose='RAP')
        if foss == 'R':
            template = 'rappre_certificate_download.html'
        else:
            template = 'vlab_certificate_download.html'
        if not user:
            context["notregistered"] = 1
            return render_to_response(template,
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        institute = user.institute.replace('&', 'and')
        foss = user.foss
        date = user.date
        purpose = user.purpose
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_rappre_certificate(certificate_path, details,
                    qrcode, _type, institute, foss, date, file_name)
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
            certificate = create_rappre_certificate(certificate_path, details,
                    qrcode, _type, institute, foss, date, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response(template, context, ci)
    context['message'] = ''
    return render_to_response('rappre_certificate_download.html', context, ci)


def create_rappre_certificate(certificate_path, details, qrcode, _type,
                              institute, foss, date, file_name):
    error = False
    err = None
    try:
        if foss == 'R':
            template = 'template_r_appre'
        else:
            template = 'template_vlab'
        download_file_name = 'RAPP2021certificate.pdf'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=institute, foss=foss, date=date)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def scipy_all_download(request, year="2020"):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2019/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        year = request.POST.get('year', None)
        context['year'] = year
        workshop = None
        email = request.POST.get('email').strip()
        attendee_type = request.POST.get('type')
        if paper:
            user = SciPyAll.objects.filter(email=email,
                    attendee_type=attendee_type, year=year, paper=paper)
        else:
            user = SciPyAll.objects.filter(email=email,
                    attendee_type=attendee_type, year=year)
        if not user:
            context["notregistered"] = 1
            return render_to_response('scipy_all_download.html', context, context_instance=ci)
        elif len(user) > 1:
            if attendee_type == 'W' or attendee_type == 'A':
                context['user_papers'] = user
                context['v'] = 'paper'
                return render_to_response('scipy_all_download.html', context, context_instance=ci)
            context["duplicate"] = True
            return render_to_response('scipy_all_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        purpose = user.purpose
        paper = user.paper
        yr = year[2:]
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, yr, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        template = 'template_SPC%s%scertificate' % (year, attendee_type)
        download_file_name = 'SPC%s%scertificate.pdf' % (year, attendee_type)
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_all_certificate(
                certificate_path, details, qrcode, attendee_type, paper,
                workshop, file_name, template, download_file_name
            )
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_all_certificate(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name,
                    template, download_file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('scipy_all_download.html', context, ci)
    context['message'] = ''
    context['year'] = year
    return render_to_response('scipy_all_download.html', context, ci)


@csrf_exempt
def create_scipy_all_certificate(certificate_path, name, qrcode, attendee_type, paper, workshop, file_name,
                                 template, download_file_name):
    error = False
    try:
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        if attendee_type == 'P' or attendee_type == 'T':
            content_tex = content.safe_substitute(name=name['name'].title(),
                    serial_key=name['serial_key'], qr_code=qrcode)
        else:
            content_tex = content.safe_substitute(name=name['name'].title(),
                        serial_key=name['serial_key'], qr_code=qrcode, paper=paper)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path, attendee_type, file_name)

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


def ardsupport_workshop_download(request):
    foss = 'Arduino'
    template = 'template_ardstaff'
    html_template = 'ardsupport_workshop_download.html'
    year = '2021'
    return support_workshop_all_download(request, foss, template,
                                         html_template, year)

def support_workshop_all_download(request, foss, template, html_template, year):
    context = {}
    err = ""
    ci = RequestContext(request)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        _type = request.POST.get('type', 'P')
        user = SupportAll.objects.filter(email=email, foss=foss, year=year)
        if not user:
            context["notregistered"] = 1
            return render_to_response(html_template, context, context_instance=ci)
        else:
            user = user[0]
        cur_path = os.path.dirname(os.path.realpath(__file__))
        certificate_path = '{0}/st_workshop_template/'.format(cur_path)
        paper = None
        workshop = None
        name = user.name
        rcname = user.rcname
        rcid = user.rcid
        role = user.role
        foss = user.foss
        college = rcname.replace('&', 'and')
        purpose = user.purpose
        year = '21'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_support_all_workshop_certificate(certificate_path,
                    details, qrcode, _type, file_name, college, rcid, role, foss,
                    template)
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
            certificate = create_support_all_workshop_certificate(certificate_path,
                    details, qrcode, _type, file_name, college, rcid, role, foss,
                    template)
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
            return render_to_response(html_template, context, ci)
    context['message'] = ''
    return render_to_response(html_template, context, ci)

def create_support_all_workshop_certificate(certificate_path, name, qrcode,
        _type, file_name, college, rcid, role, foss, template):
    error = False
    err = None
    try:
        download_file_name = None
        template = template

        download_file_name = 'WSS2020Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name['name'].title(),
                serial_key=name['serial_key'], foss=foss,
                qr_code=qrcode, rcname=college, rcid=rcid, role=role)
        create_tex = open('{0}{1}.tex'.format\
                (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def complex_fluids_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/scipy_template_2019/'.format(cur_path)

    if request.method == 'POST':
        paper = request.POST.get('paper', None)
        workshop = None
        email = request.POST.get('email').strip()
        email = email.lower()
        attendee_type = request.POST.get('type')
        if paper:
            user = ComplexFluids.objects.filter(email__iexact=email,
                    attendee_type=attendee_type, year='2020', paper=paper)
        else:
            user = ComplexFluids.objects.filter(email__iexact=email,
                    attendee_type=attendee_type, year='2020')
        if not user:
            context["notregistered"] = 1
            return render_to_response('complex_fluids_download.html', context, context_instance=ci)
        elif len(user) > 1:
            if attendee_type == 'O' or attendee_type == 'A':
                context['user_papers'] = user
                context['v'] = 'paper'+attendee_type
                return render_to_response('complex_fluids_download.html', context, context_instance=ci)
            context["duplicate"] = True
            return render_to_response('complex_fluids_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        email = user.email
        email = email.lower()
        purpose = user.purpose
        paper = user.paper
        paper = paper.replace('&', 'and')
        year = '20'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, attendee_type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        template = 'template_CFC2020%scertificate' % attendee_type
        download_file_name = 'CFC2020%scertificate.pdf' % attendee_type
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'email' : email}
            certificate = create_scipy_all_certificate(
                certificate_path, details, qrcode, attendee_type, paper,
                workshop, file_name, template, download_file_name)
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
            details = {'name': name,  'serial_key': short_key, 'email': email}
            certificate = create_scipy_all_certificate(certificate_path, details,
                    qrcode, attendee_type, paper, workshop, file_name,
                    template, download_file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no,
                            counter=1, workshop=workshop, paper=paper, serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('complex_fluids_download.html', context, ci)
    context['message'] = ''
    return render_to_response('complex_fluids_download.html', context, ci)


def python_certified_students(request):
    students = PythonCertification.objects.all().order_by('-id')
    return render(request,'certified.html', {'students': students})

def certified_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="certified.csv"'

    writer = csv.writer(response)
    students = PythonCertification.objects.all().order_by('-id')
    writer.writerow(['name', 'email', 'grade', 'month', 'year'])
    for student in students:
        writer.writerow([student.name, student.email, student.grade,
            student.month, student.year])
    return response


def esim_marathon_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/esim/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = EsimMarathon.objects.filter(email=email, purpose='EMC')
        if not user:
            context["notregistered"] = 1
            return render_to_response('esim_marathon_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        circuit = user.circuit
        circuit = circuit.replace('&', 'and')
        college = user.college
        college = college.replace('&', 'and')
        ctype = user.ctype
        purpose = user.purpose
        year = '21'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esim_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
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
            certificate = create_esim_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('esim_marathon_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esim_marathon_certificate_download.html', context, ci)


def esim_marathon_2022_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/esim22/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = EsimMarathon2022.objects.filter(email=email, purpose='EM2')
        if not user:
            context["notregistered"] = 1
            return render_to_response('esim_marathon_2022_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        circuit = user.circuit
        circuit = circuit.replace('&', 'and')
        college = user.college
        college = college.replace('&', 'and')
        ctype = user.ctype
        purpose = user.purpose
        year = '22'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_esim_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
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
            certificate = create_esim_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('esim_marathon_2022_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('esim_marathon_2022_certificate_download.html', context, ci)


def create_esim_marathon_certificate(certificate_path, details, qrcode, _type,
                                     circuit, ctype, college, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        if ctype == 'O':
            template = 'template_o'
        elif ctype == 'E':
            template = 'template_e'
        elif ctype == 'V':
            template = 'template_v'
        elif ctype == 'M':
            template = 'template_m'
        else:
            template = 'template_g'
        download_file_name = 'ESMPcertificate.pdf'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode, college=college,
                circuit=circuit)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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


def intern21_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/intern21/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Intern2021.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('intern21_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        topic = (user.title).replace('&', 'and')
        mode = user.mode
        mode_def = user.mode_def
        foss = user.foss

        year = '21'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_intern21_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    mode, mode_def, foss, file_name)
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
            certificate = create_intern21_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    mode, mode_def, foss, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('intern21_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('intern21_certificate_download.html', context, ci)


def create_intern21_certificate(certificate_path, details, qrcode,
        student_institute_detail, topic, mode, mode_def, foss, file_name):
    error = False
    try:
        bg = 'bg{}.png'.format(foss.strip())
        template = 'template'
        download_file_name = 'INT2021Pcertificate.pdf'
        template_file = open('{0}{1}'.format\
                (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=student_institute_detail, title=topic, mode=mode,
                bg=bg, mode_def=mode_def)
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
        error = True
    return [None, error]

def fellow21_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fellow21/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = Fellow2021.objects.filter(email=email)
        if not user:
            context["notregistered"] = 1
            return render_to_response('fellow21_certificate_download.html', context, context_instance=ci)
        else:
            user = user[0]
        name = (user.name).title()
        purpose = user.purpose
        student_institute_detail = user.institute
        student_institute_detail = student_institute_detail.replace('&', 'and')
        topic = (user.title).replace('&', 'and')
        start_date = user.start_date
        end_date = user.end_date

        year = '21'
        _type = 'P'
        hexa = hex(user.id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, user.id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fellow21_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    start_date, end_date, file_name)
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
            certificate = create_fellow21_certificate(certificate_path,
                    details, qrcode, student_institute_detail, topic,
                    start_date, end_date, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1, serial_key=serial_key,
                            short_key=short_key)
                    certi_obj.save()
                    return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('fellow21_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fellow21_certificate_download.html', context, ci)


def create_fellow21_certificate(certificate_path, details, qrcode,
        student_institute_detail, topic, start_date, end_date, file_name):
    error = False
    try:
        template = 'template20'
        download_file_name = 'FEL2021Pcertificate.pdf'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode,
                institute=student_institute_detail, topic=topic,
                start_date=start_date, end_date=end_date)
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
        error = True
    return [None, error]

def mixed_signal_marathon_2022_certificate_download(request):
    context= {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/marathon/mixed-signals/'.format(cur_path)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        user = MixedSignal.objects.filter(email=email, year='2022', purpose='MSM')
        if not user:
            context["notregistered"] = 1
            return render_to_response('mixed_signal_marathon_2022_certificate_download.html',
                                       context, context_instance=ci)
        user = user[0]
        _type = 'P'
        name = user.name
        circuit = user.circuit
        circuit = circuit.replace('&', 'and')
        college = user.college
        college = college.replace('&', 'and')
        ctype = user.ctype
        purpose = user.purpose
        year = '22'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, _type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email,id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'http://fossee.in/certificates/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_mixed_signal_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
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
            certificate = create_mixed_signal_marathon_certificate(certificate_path, details,
                    qrcode, _type, circuit, ctype, college, file_name)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email,
                            serial_no=serial_no, counter=1,
                            serial_key=serial_key, short_key=short_key)
                    certi_obj.save()
                    return certificate[0]
        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = certificate[0]
            return render_to_response('mixed_signal_marathon_2022_certificate_download.html', context, ci)
    context['message'] = ''
    return render_to_response('mixed_signal_marathon_2022_certificate_download.html', context, ci)


def create_mixed_signal_marathon_certificate(certificate_path, details, qrcode, _type,
                                     circuit, ctype, college, file_name):
    error = False
    err = None
    try:
        download_file_name = 'MSMPcertificate.pdf'
        template = 'template'
        if ctype == 'Outstanding':
            bg = 'bgO.jpg'
        elif ctype == 'Excellent':
            bg = 'bgE.jpg'
        elif ctype == 'Very Good':
            bg = 'bgV.jpg'
        elif ctype == 'Mentoring':
            bg = 'bgA.jpg'
        else:
            bg = 'bgG.jpg'
        template_file = open('{0}{1}'.format(certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=details['name'].title(),
                serial_key=details['serial_key'], qr_code=qrcode, institute=college,
                circuit=circuit, category=ctype, bg=bg)
        create_tex = open('{0}{1}.tex'.format(certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                _type, file_name)
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
