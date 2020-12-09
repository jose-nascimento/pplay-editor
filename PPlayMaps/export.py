import os
from PIL import Image
from PPlayMaps import config as conf
config = conf.config["active"]

def export(project = None):
    if project == None:
        project = config["active_project"]