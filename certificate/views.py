from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from certificate.models import Scilab_import, Certificate, Event
import subprocess
import os
from string import Template

# Create your views here.
def download(request):
    email = request.POST.get('email')

    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/certificate_template/'.format(cur_path)

    if request.method == 'POST':
        try:
            user = Scilab_import.objects.get(email=email)
        except Scilab_import.DoesNotExist:
            return HttpResponse('Entered email is not registered')
        name = user.name
        purpose = user.purpose
        year = '14'
        id =  int(user.id)
        hexa = hex(id).replace('0x','').zfill(6).upper()
        type = 'P'
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        qrcode = '{0}\n{1}'.format(name, serial_no)
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            certificate = create_certificate(certificate_path, name, qrcode)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            certificate = create_certificate(certificate_path, name, qrcode)
            if not certificate[1]:
                    certi_obj = Certificate(name=name, email=email, serial_no=serial_no, counter=1)
                    certi_obj.save()
                    return certificate[0]
        
        if certificate[1]:
            _clean_certificate_certificate(certificate_path)
            context['error'] = True
            return render_to_response('download.html', context, ci)
    return render_to_response('download.html', context, ci)

def verify(request):
    context = {}
    ci = RequestContext(request)
    detail = None
    if request.method == 'POST':
        serial_no = request.POST.get('serial_no')
        try:
            certificate = Certificate.objects.get(serial_no=serial_no)
        except Certificate.DoesNotExist:
            return HttpResponse('Invalid Serial Number')
        else:
            name = certificate.name
            purpose, year, type = _get_detail(serial_no)
            if type == 'P':
                detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A':
                detail = '{0} had presented paper in the {1} {2}'.format(name, purpose, year)
            elif type == 'E':
                detail = '{0} had attended workshop in the {1} {2}'.format(name, purpose, year)
            context['detail'] = detail
            print detail
            return render_to_response('verify.html', context, ci)
    return render_to_response('verify.html',{}, ci)

def _get_detail(serial_no):
    if serial_no[0:3] == 'SLC':
        purpose = 'Scilab Conference'
    elif serial_no[0:3] == 'SPC':
        purpose = 'SciPy India'

    if serial_no[3:5] == '14':
        year = '2014'
    elif serial_no[3:5] == '15':
        year = '2015'

    #if serial_no[-1] == 'P':
    #    type = 'Participant'
    #elif serial_no[-1] == 'A':
    
    #type = 'Paper'
    #elif serial_no[-1] == 'W':
    #    type = 'Workshop'
    return purpose, year, serial_no[-1]


def create_certificate(certificate_path, name, qrcode):
    error = False 
    try:
        template_file = open('{0}template_certificate'.format\
                (certificate_path), 'r')
        content = Template(template_file.read())
        template_file.close()
        content_tex = content.safe_substitute(name=name, code=qrcode)
        create_tex = open('{0}certificate.tex'.format\
                (certificate_path), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path)
        if return_value == 0:
            file_name = 'certificate.pdf'
            pdf = open('{0}{1}'.format(certificate_path, file_name) , 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path)
            return [response, False] 
        else:
            error = True
    except Exception, e:
        error = True
    return [None, error]

def _clean_certificate_certificate(path):
    clean_process = subprocess.Popen('make -C {0} clean'.format(path),
            shell=True)
    clean_process.wait()

def _make_certificate_certificate(path):
    process = subprocess.Popen('timeout 15 make -C {0} certificate'.format(path),
            stderr = subprocess.PIPE, shell = True)
    err = process.communicate()[1]
    return process.returncode, err

    return HttpResponse("DOWNLAOD")
