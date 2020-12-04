import pickle
import os
from modules import config as conf
config = conf.config["current"]

class Map:

    def __init__(self, name, bgcolor = (0, 0, 0), height = 16, width = 30):
        self.name = name
        self.layers = [self.init_layer(), self.init_layer(), self.init_layer(), self.init_layer()]
        self.bgcolor = bgcolor
        self.height = height
        self.width = width

    def save_map(self, path = None):
        if path == None:
            path = os.path.join("projects", config["active_project"])
        with open(os.path.join(path, "maps", f"{self.name}.pkl"), "wb") as file:
            pickle.dump(self, file)

    def clear_layer(self, index):
        layer = index - 1
        self.layers[layer] = Map.init_layer()

    def place_tile(self, tile, pos, z):
        x, y = pos
        self.layers[z - 1][y][x] = tile

    def fill_area(self, tile, start, end, layer):
        mp = self.layers[layer - 1]
        x0, y0 = start
        x1, y1 = end
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        x1 += 1
        for line in mp[y0:y1]:
            for x, _ in enumerate(line[x0:x1]):
                line[x + x0] = tile
            # for x, _ in enumerate(line):
            #     if x0 <= x < x1:
            #         line[x] = tile
    
    def flood_fill(self, tile, point, layer):
        mp = self.layers[layer - 1]
        stack = [point]
        ymax = len(mp) - 1
        xmax = len(mp[0]) - 1
        target_tile = mp[point[1]][point[0]]

        while(len(stack)):
            x, y = stack.pop()
            if mp[y][x] == target_tile:
                mp[y][x] = tile
                if x > 0: stack.append((x - 1, y))
                if x < xmax: stack.append((x + 1, y))
                if y > 0: stack.append((x, y - 1))
                if y < ymax: stack.append((x, y + 1))
    
    def get_tile(self, pos, z):
        x, y = pos
        return self.layers[z - 1][y][x]

    @staticmethod
    def load_map(name = None, project = None):
        if name == None: name = config["start_map"]
        if project == None: project = config["active_project"]
        path = os.path.join("projects", project, "maps")
        filename = f"{name}.pkl"
        if filename in os.listdir(path):
            with open(os.path.join(path, filename), "rb") as file:
                mp = pickle.load(file)
                mp.height = 16
                mp.width = 30
            return mp
        else:
            raise FileNotFoundError

    def init_layer(self):
        # 30x16
        line = [0] * self.width
        layer = line * self.height
        return layer