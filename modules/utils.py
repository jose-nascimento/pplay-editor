import os
import configparser
from typing import Optional
from zipfile import ZipFile, ZIP_DEFLATED
from PPlayMaps import config as conf
from PPlayMaps.types import Color
config = conf.config

def list_projects():
    project_folder = config["active"].get("project_folder", "projects")
    return os.listdir(project_folder)

def list_maps():
    project_folder = config.default_folder()
    map_folder = os.path.join(project_folder, "maps")
    return os.listdir(map_folder)

def list_tilesets():
    project_folder = config.default_folder()
    tileset_folder = os.path.join(project_folder, "tilesets")
    return os.listdir(tileset_folder)

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

def rgb_to_hex(rgb: Color) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
