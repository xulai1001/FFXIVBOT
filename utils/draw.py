import os, json, random
from random import choice
os.environ['DJANGO_SETTINGS_MODULE'] ='FFXIVBOT.settings'
import django
from django.db import connection, connections
django.setup()
from FFXIVBOT.models import *

filename = choice(os.listdir("../card"))
idx = int(filename.split(".")[0])
print(idx)

text_item = YGOText.objects.using("mycard").filter(id=idx)
if text_item:
    print(text_item[0].name, text_item[0].desc)


