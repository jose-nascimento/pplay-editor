import os
import configparser
config = configparser.ConfigParser()

if "config.ini" in os.listdir():
    config.read("config.ini")
else:
    config.add_section("active")

project_folder = config["active"].get("project_folder", None)

def write_changes():
    with open("config.ini", "w") as configfile:
        config.write(configfile)

def default_folder(project = None):
    if project_folder == None:
        return "."
    else:
        if project is None: project = config["active"]["active_project"]
        return os.path.join(project_folder, project)

config.default_folder = default_folder
config.write_changes = write_changes
