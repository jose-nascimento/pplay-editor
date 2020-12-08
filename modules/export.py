import os
from PIL import Image
from modules import config as conf
config = conf.config["current"]

def export(project = None):
    if project == None:
        project = config["active_project"]