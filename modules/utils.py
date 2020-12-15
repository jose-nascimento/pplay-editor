import os
import configparser
from typing import Optional
from zipfile import ZipFile, ZIP_DEFLATED
from PPlayMaps import Color, config as conf
config = conf.config

def export_project(name: str, path: Optional[str] = None):
    project_folder = os.path.join("projects", name)
    if path is None:
        path = "."
    filename = os.path.join(path, f"{name}.zip")
    export_folders = [("PPlayMaps", "."), ("tilesets", [project_folder]), ("maps", [project_folder])]
    with ZipFile(filename, "w", ZIP_DEFLATED) as zip_file:
        for folder, param in export_folders:
            rel = os.path.join(*param)
            location = os.path.join(rel, folder)
            for root, dirs, files in os.walk(location):
                if not "__pycache__" in root:
                    for file in files:
                        dest = os.path.relpath(root, rel)
                        arcname = os.path.join(dest, file)
                        zip_file.write(os.path.join(root, file), arcname)

def create_project(name: str, map_name: str):
    project_folder = config.default_folder(name)
    os.mkdir(project_folder)
    map_folder = os.path.join(project_folder, "maps")
    tileset_folder = os.path.join(project_folder, "tilesets")
    os.mkdir(map_folder)
    os.mkdir(tileset_folder)
    project_config = configparser.ConfigParser()
    project_config.add_section("active")
    project_config.set("active", "start_map", map_name)
    with open(os.path.join(project_folder, "project.ini"), "w") as configfile:
        project_config.write(configfile)

def set_start_map(name: str, project: Optional[str] = None):
    project_config = configparser.ConfigParser()
    project_folder = config.default_folder(project)
    config_path = os.path.join(project_folder, "project.ini")
    project_config.read(config_path)
    project_config["active"]["start_map"] = name
    with open(config_path, "w") as configfile:
        project_config.write(configfile)

def hex_to_rgb(hex: str) -> Color:
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
