# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from models import *
import django
from datetime import time
import datetime
import math

class PersonInfo(object): pass

def solve_base():
    url_root = ''
    try:
        url_root = django.root
    except: pass
    return url_root

def get_idlestring(last):
    now = datetime.datetime.now()
    idle = now - last
    return int(math.ceil(idle.seconds/60.0))

def get_personinfos():
    personinfos = []
    persons = Person.objects.all()
    for person_ in persons:
        info = PersonInfo()
        drinks = Drink.objects.filter(person=person_).order_by('-finished')
        info.name = person_.name
        info.id = person_.id
        info.drinks = len(drinks)
        if len(drinks) > 0:
            info.idle = "%s min" % (get_idlestring(drinks[0].finished))
        else:
            info.idle = "oo"
        personinfos.append(info)
    return personinfos

def index(request):
    t = loader.get_template('views/index.html')
    c = Context({
        'personinfos': get_personinfos(),
        'base': solve_base()
    })
    return HttpResponse(t.render(c))

def add_drink(request, personid):
    try:
        person = Person.objects.get(id=personid)
        drink = Drink()
        drink.person = person
        drink.finished = datetime.datetime.now()
        drink.save()
        if request.GET.has_key("robot"):
            return HttpResponse("OK", mimetype="text/plain")
        else:
            response = """
            <html><head><title>Saved!</title></head><body>
            <p>Thank you, drink saved! No refreshing please.</p>
            <p>Go back by clicking <a href="%s/drinkcounter/">this</a></p>
            </body></html>
            """ % solve_base()
            return HttpResponse(response)
    except:
        return HttpResponse("Screw you.")

def get_datas(request):
    personinfos = get_personinfos()
    response = ""
    for personinfo in personinfos:
        response += "%s|%s|%s|%s\n" % (personinfo.id, \
            personinfo.name, personinfo.drinks, "0.0")
    return HttpResponse(response, mimetype="text/plain")


def get_drink_count_for_past_6_hours(person_, moment):
    begins = moment - datetime.timedelta(hours=6)
    drinks = Drink.objects.filter(finished__gte=begins, \
        finished__lte=moment, person=person_)
    return len(drinks)

def get_cumulative_data():
    if len(Drink.objects.all()) == 0:
        raise ValueError("Not enough data")
    first = Drink.objects.all().order_by('finished')[0]
    last = Drink.objects.all().order_by('-finished')[0]
    persons = Person.objects.all()

    hour = 0
    checkpoint = hourize(first.finished)
    analyzing_ends = last.finished

    datas_by_hours = []
    while checkpoint < analyzing_ends:
        datas_by_users = dict()
        for person in persons:
            count = get_drink_count_for_past_6_hours(person, checkpoint)
            datas_by_users[person] = count
        datas_by_hours.append(datas_by_users)
        checkpoint = checkpoint + datetime.timedelta(hours=1)
    return datas_by_hours

def hourize(moment):
    year = moment.year
    mon = moment.month
    day = moment.day
    hour = moment.hour
    return datetime.datetime(year,mon,day,hour)

def get_cumulative_data_as_js():
    js = ""
    datas_by_hours = get_cumulative_data()
    hour = 0
    item_index = 0
    for datas_by_users in datas_by_hours:
        for user in datas_by_users.keys():
           count = datas_by_users[user]
           js += """data.setValue(%s, 0, '%s')\n""" % (item_index, user.name)
           js += """data.setValue(%s, 1, %s)\n""" % (item_index, hour)
           js += """data.setValue(%s, 2, %s)\n""" % (item_index, count)
           item_index += 1
        hour += 1
    row_count = item_index # last +1 completes count
    return (js, row_count)

def statistics(request):
    js, count = get_cumulative_data_as_js()
    t = loader.get_template('views/statistics.html')
    c = Context({
        u'data': js,
        u'rowcount': count,
        'base': solve_base()
    })
    return HttpResponse(t.render(c))

