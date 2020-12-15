from os import path
import pygame
import pygame_menu
import os
from PPlayMaps import Map, config as conf
from modules import events, utils
config = conf.config
active = config["active"]

def test():
    print("test")

def list_projects():
    project_folder = config["active"].get("project_folder", "projects")
    return os.listdir(project_folder)

def list_maps():
    project_folder = config.default_folder()
    map_folder = os.path.join(project_folder, "maps")
    return os.listdir(map_folder)

class _ProjectMenu(pygame_menu.Menu):

    def __init__(self, main_menu, height, width, **kwargs):
        super().__init__(
            height,
            width,
            "Selecione o projeto",
            center_content = False,
            **kwargs
        )
        self.main_menu = main_menu
        self.update_choices()

    def open_project(self, name):
        self.main_menu.full_reset()
        self.main_menu._close()
        event = pygame.event.Event(events.CHANGE_PROJECT, project = name)
        pygame.event.post(event)

    def update_choices(self):
        self.clear()
        projects = list_projects()
        for project in projects:
            self.add_button(project, self.open_project, project)

class _MapSelectionMenu(pygame_menu.Menu):

    def __init__(self, main_menu, height, width, **kwargs):
        super().__init__(
            height,
            width,
            "Selecione o mapa",
            center_content = False,
            **kwargs
        )
        self.main_menu = main_menu
        self.update_choices()

    def open_map(self, name):
        self.main_menu.full_reset()
        self.main_menu._close()
        event = pygame.event.Event(events.CHANGE_MAP, map = name)
        pygame.event.post(event)

    def update_choices(self):
        self.clear()
        maps = list_maps()
        for map in maps:
            self.add_button(map, self.open_map, map)


class Menu(pygame_menu.Menu):

    def __init__(self, height, width, title, **kwargs) -> None:
        super().__init__(height, width, title, **kwargs)
        self._onclose = self.disable
        self.project_menu = project_menu = _ProjectMenu(self, height, width)
        self.map_selection_menu = map_selection_menu = _MapSelectionMenu(self, height, width)
        self.add_button("Selecionar Projeto", project_menu)
        self.add_button("Novo Projeto", self.create_project_menu(height, width))
        self.add_button("Selecionar Mapa", map_selection_menu)
        self.add_button("Editar Mapa", test)
        self.add_button("Novo Mapa", self.create_map_menu(height, width))
        self.add_button("Sair", pygame_menu.events.EXIT)

    def create_map_fn(self):
        events_queue = []
        data = self.create_map_menu.get_input_data()

        map_name = data["map_name"]
        map_width = data["map_width"]
        map_height = data["map_height"]
        map_color = utils.hex_to_rgb(data["map_bgcolor"])

        if self.defer is not None:
            ev = self.defer(map_name)
            events_queue.append(ev)

        project_folder = config.default_folder()
        map_path = os.path.join(project_folder, "maps", map_name)
        os.mkdir(map_path)
        map = Map(
            map_name,
            height = map_height,
            width = map_width,
            path = map_path,
            background = { "background_color": map_color }
        )

        map.save_map()
        self.full_reset()
        self._close()
        self.map_selection_menu.update_choices()

        events_queue.append(pygame.event.Event(events.CHANGE_MAP, map = map_name))

        for event in events_queue:
            pygame.event.post(event)

    def create_project_fn(self, project_name: str, map_name: str):
        data = self.create_project_menu.get_input_data()
        project_name = data["project_name"]

        utils.create_project(project_name, map_name = map_name)

        active["active_project"] = project_name
        event = pygame.event.Event(events.CHANGE_PROJECT, project = project_name)

        return event

    def create_project_defer(self):
        data = self.create_project_menu.get_input_data()
        project_name = data["project_name"]
        self.defer = lambda map_name: self.create_project_fn(project_name, map_name)

        self._open(self.create_map_menu)
    
    def create_project_menu(self, height, width):
        self.create_project_menu = menu = pygame_menu.Menu(
            height, width, "Novo projeto", center_content = False
        )
        menu.add_text_input("Nome do projeto: ", textinput_id = "project_name", align = pygame_menu.locals.ALIGN_LEFT)
        menu.add_button("Criar projeto", self.create_project_defer, align = pygame_menu.locals.ALIGN_LEFT)
        menu.add_button(
            "Voltar ao menu principal", pygame_menu.events.BACK, align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu
    
    def create_map_menu(self, height, width):
        self.create_map_menu = menu = pygame_menu.Menu(
            height, width, "Novo mapa", center_content = False
        )
        hex_chars = [f"{x:01x}" for x in range(16)] + [f"{x:01X}" for x in range(16)]
        menu.add_text_input("Nome do mapa: ", textinput_id = "map_name")
        menu.add_text_input(
            "Largura: ", textinput_id = "map_width", default = 30, maxchar = 3, maxwidth = 3, input_type = pygame_menu.locals.INPUT_INT
        )
        menu.add_text_input(
            "Altura: ", textinput_id = "map_height", default = 16, maxchar = 3, maxwidth = 3, input_type = pygame_menu.locals.INPUT_INT
        )
        menu.add_text_input(
            "Cor: #", textinput_id = "map_bgcolor", default = "000000", maxchar = 6, maxwidth = 6, valid_chars = hex_chars
        )
        menu.add_button("Criar mapa", self.create_map_fn)
        menu.add_button(
            "Voltar ao menu principal", pygame_menu.events.BACK, align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu