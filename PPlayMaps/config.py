import os
import configparser
config = configparser.ConfigParser()

if "config.ini" in os.listdir():
    config.read("config.ini")
else:
    config["DEFAULT"]["default_tileset"] = "default"

project_folder = config["active"].get("project_folder", None)

def default_folder(project = None):
    if project_folder == None:
        return "."
    else:
        if project is None: project = config["active"]["active_project"]
        return os.path.join(project_folder, project)

config.default_folder = default_folder
