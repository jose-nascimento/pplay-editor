import os
from PIL import Image
from modules import Map, Tileset, config as conf
config = conf.config["current"]

def save_map(project = None, map_name = None):
    if project == None: project = config["active_project"]
    if map_name == None: map_name = config["start_map"]
    # map_file = f"{map}.json"
    path = os.path.join("projects", project)
    map_path = os.path.join(path, "maps", map)
    map = Map.load_map(map_name, project)
    tileset_name = map.tileset
    tileset = Tileset.load_tiles(project = project, name = tileset_name, mode = "image")
    delta = tileset.tile_size
    map_size = (map.width * delta, map.height * delta)
    # movement_layer = map.get_movement_layer()
    layers = map.get_display_layers()
    canvas = Image.new("RGBA", map_size, map.bgcolor)
    for layer in layers:
        for y, line in enumerate(layer):
            for x, tile in enumerate(line):
                canvas.paste(tileset[tile], (x * delta, y * delta))
    canvas.save(os.path.join(map_path, f"{map_name}.png"))


def export(project = None):
    if project == None:
        project = config["active_project"]