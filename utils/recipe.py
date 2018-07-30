import os, json
os.environ['DJANGO_SETTINGS_MODULE'] ='FFXIVBOT.settings'
import django
from django.db import connection, connections
django.setup()
from FFXIVBOT.models import *

recipes = json.load(open("out2.json", "r", encoding="utf-8"))
count = 0;
for key in recipes:
    item = FFrecipe(name=key, recipe=recipes[key])
    item.save()
    count += 1
    print("(%d / %d) %s = %s" % (count, len(recipes), key, "+".join(recipes[key])))    
    