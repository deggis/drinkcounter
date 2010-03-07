import urllib2
import appuifw, e32
from key_codes import *


class Drinker(object):
    def __init__(self):
        self.id = 0
        self.name = ""
        self.prom = 0.0
        self.idle = ""
        self.drinks = 0


def get_drinker_list():
    data = urllib2.urlopen("http://192.168.11.5:8080/drinkcounter/get_datas/").read().split("\n")
    drinkers = []

    for data_row in data:
        if data_row == '': continue

        fields = data_row.split('|')

        drinker = Drinker()
        drinker.id = int(fields[0])
        drinker.name = fields[1]
        drinker.drinks = int(fields[2])
        drinker.prom = float(fields[3])
        drinker.idle = fields[4]

        drinkers.append(drinker)

    return drinkers


def get_listbox_items(drinkers):
    items = []

    for drinker in drinkers:
        items.append(unicode('%s, %d drinks, %s' % (drinker.name, drinker.drinks, drinker.idle)))

    return items


appuifw.app.title = u"Alkoholilaskuri"

app_lock = e32.Ao_lock()

#Define the exit function 
def quit():
        app_lock.signal()

appuifw.app.exit_key_handler = quit

drinkers = get_drinker_list()
items = get_listbox_items(drinkers)


#Define a function that is called when an item is selected
def handle_selection():
    selected_drinker = drinkers[lb.current()]
    urllib2.urlopen("http://192.168.11.5:8080/drinkcounter/add_drink/%d/" % (selected_drinker.id))
    appuifw.note(u"A drink has been added to " + drinkers[lb.current()].name, 'info')

    new_drinkers = get_drinker_list()
    items = get_listbox_items(new_drinkers)

    lb.set_list(items, lb.current())


#Create an instance of Listbox and set it as the application's body
lb = appuifw.Listbox(items, handle_selection)
appuifw.app.body = lb
 
app_lock.wait()
