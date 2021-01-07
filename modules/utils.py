from typing import Optional
from os import path, listdir, walk, mkdir
from shutil import copyfile
import configparser
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED
from PPlayMaps import Tileset, config as conf
from PPlayMaps.types import Color
config = conf.config
active = config["active"]

def list_projects():
    project_folder = config["active"].get("project_folder", "projects")
    return listdir(project_folder)

def list_maps():
    project_folder = config.default_folder()
    map_folder = path.join(project_folder, "maps")
    return listdir(map_folder)

def list_tilesets():
    project_folder = config.default_folder()
    tileset_folder = path.join(project_folder, "tilesets")
    return listdir(tileset_folder)

def get_filename(filepath: str):
    basename = path.basename(filepath)
    return path.splitext(basename)[0]

def export_project(name: Optional[str] = None, filepath: Optional[str] = None):
    if name is None:
        name = active["active_project"]
    if filepath is None:
        filepath = path.join(filepath, f"{name}.zip")
    
    project_folder = path.join("projects", name)
    export_folders = [
        ("PPlay", "."),
        ("PPlayMaps", "."),
        ("tilesets", [project_folder]),
        ("maps", [project_folder])
    ]

    with ZipFile(filepath, "w", ZIP_DEFLATED) as zip_file:
        for folder, param in export_folders:
            rel = path.join(*param)
            location = path.join(rel, folder)
            for root, dirs, files in walk(location):
                if not "__pycache__" in root:
                    for file in files:
                        dest = path.relpath(root, rel)
                        arcname = path.join(dest, file)
                        zip_file.write(path.join(root, file), arcname)

def import_image(filepath: str, map_name: str) -> str:
    if not path.isfile(filepath):
        raise ValueError("filepath should be of a file")

    filename = path.basename(filepath)
    project_folder: str = config.default_folder()
    save_folder = path.join(project_folder, "maps", map_name)

    copyfile(filepath, path.join(save_folder, filename))

    return filename

def import_tileset(filepath: str, tile_size: int, name: Optional[str] = None) -> str:
    if not path.isfile(filepath):
        raise ValueError("filepath should be of a file")

    if name is None:
        name = get_filename(filepath)
    
    project_folder: str = config.default_folder()
    save_folder = path.join(project_folder, "tilesets", name)
    
    image = Image.open(filepath)
    mkdir(save_folder)

    width, height = image.size
    xmax, ymax = width // tile_size, height // tile_size

    for i in range(0, ymax):
        for j in range(0, xmax):
            x, y = j * tile_size, i * tile_size
            cropbox = (x, y, x + tile_size, y + tile_size)
            n = (i * xmax) + j
            try:
                tile = image.crop(cropbox)
                tile.save(path.join(save_folder, f"{n:02d}.png"))
            except OSError as ose:
                print(f"Couldn't write tile {n:02d} to file")
                print(ose)
            except:
                print(f"Couldn't crop or save tile {n:02d}")
    
    tileset = Tileset(name, tiles = [], tile_size = tile_size, path = save_folder)
    tileset.save()

    return name

def create_project(name: str, map_name: str):
    project_folder = config.default_folder(name)
    mkdir(project_folder)
    map_folder = path.join(project_folder, "maps")
    tileset_folder = path.join(project_folder, "tilesets")
    mkdir(map_folder)
    mkdir(tileset_folder)
    project_config = configparser.ConfigParser()
    project_config.add_section("active")
    project_config.set("active", "start_map", map_name)
    with open(path.join(project_folder, "project.ini"), "w") as configfile:
        project_config.write(configfile)

def set_start_map(name: str, project: Optional[str] = None):
    project_config = configparser.ConfigParser()
    project_folder = config.default_folder(project)
    config_path = path.join(project_folder, "project.ini")
    project_config.read(config_path)
    project_config["active"]["start_map"] = name
    with open(config_path, "w") as configfile:
        project_config.write(configfile)

def hex_to_rgb(hex: str) -> Color:
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Color) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
