from os import path
from typing import List, Optional, Tuple
import pygame
from tkinter.filedialog import asksaveasfile, asksaveasfilename
import pygame_menu
import os
from PPlayMaps import Map, config as conf
from modules import Canvas, events, utils
config = conf.config
active = config["active"]

def tileset_index(tilesets, tileset_name) -> int:
    for i, (title, name) in enumerate(tilesets):
        if name == tileset_name:
            return i
    return 0

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
        event = pygame.event.Event(events.CHANGE_PROJECT, project = name)

        self.main_menu.open_save_prompt([event])

    def update_choices(self):
        self.clear()
        projects = utils.list_projects()
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
        event = pygame.event.Event(events.CHANGE_MAP, map = name)

        self.main_menu.open_save_prompt([event])

    def update_choices(self):
        self.clear()
        maps = utils.list_maps()
        for map in maps:
            self.add_button(map, self.open_map, map)


class Menu(pygame_menu.Menu):

    def __init__(self, height, width, title, canvas: Optional[Canvas] = None, **kwargs) -> None:
        super().__init__(height, width, title, **kwargs)

        self._onclose = self.disable
        self.defer = None
        self.event_queue = []
        self.canvas = canvas

        self.project_menu = project_menu = _ProjectMenu(self, height, width)
        self.map_selection_menu = map_selection_menu = _MapSelectionMenu(self, height, width)
        self.map_creation_menu = map_creation_menu =  self.create_map_menu("Novo mapa", height, width)
        self.save_prompt = save_prompt = pygame_menu.Menu(
            250, 750, "Salvar", columns = 2, rows = 3, center_content = False
        )

        self.add_button("Selecionar Projeto", project_menu)
        self.add_button("Novo Projeto", self.create_project_menu(height, width))
        self.add_button("Selecionar Mapa", map_selection_menu)
        if canvas is not None:
            self.add_button("Editar Mapa", self.map_edit_menu)
        self.add_button("Novo Mapa", map_creation_menu)
        self.add_button("Exportar como imagem", self.ask_save)
        self.add_button("Sair", pygame_menu.events.EXIT)

        save_prompt.add_label("Salvar alterações?", align = pygame_menu.locals.ALIGN_LEFT)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_button(" Sim", self.post_save_event, align = pygame_menu.locals.ALIGN_LEFT)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_button("Não ", self.close_prompt, align = pygame_menu.locals.ALIGN_RIGHT)

    def ask_save(self):
        filename = asksaveasfilename(defaultextension = ".png", filetypes = [("Imagem", ".png")])

        if filename:
            self.canvas.export_image(filename)

    def post_save_event(self):
        event = pygame.event.Event(events.SAVE_CHANGES)
        pygame.event.post(event)

        self.close_prompt()

    def close_prompt(self):
        for event in self.event_queue:
            pygame.event.post(event)

        self.full_reset()
        self._close()

    def open_save_prompt(self, events: List[pygame.event.Event] = []):
        self.event_queue.extend(events)
        self._open(self.save_prompt)

    def update_tilesets(self, tilesets: Optional[List[Tuple[str, Optional[str]]]] = None):
        if tilesets is None:
            tilesets = [("", None)] + [(ts, ts) for ts in utils.list_tilesets()]
        
        self.tileset_selector.update_elements(tilesets)

    def create_map_fn(self):
        data = self.map_creation_menu.get_input_data()

        map_name = data["map_name"]
        map_width = data["map_width"]
        map_height = data["map_height"]
        map_tileset = data["map_tileset"][0]
        if map_tileset == "": map_tileset = None
        map_color = data["map_bgcolor"]

        if self.defer is not None: self.defer(map_name)

        project_folder = config.default_folder()
        map_path = os.path.join(project_folder, "maps", map_name)
        os.mkdir(map_path)
        map = Map(
            map_name,
            height = map_height,
            width = map_width,
            path = map_path,
            tileset = map_tileset,
            background = { "background_color": map_color }
        )

        map.save_map()
        self.map_selection_menu.update_choices()

        event = pygame.event.Event(events.CHANGE_MAP, map = map_name)
        self.event_queue.append(event)

        self.open_save_prompt()

    def edit_map_fn(self):
        data = self.edit_menu.get_input_data()
        params = self.map_params

        self.edit_menu = None
        self.map_params = None

        map_width = data["map_width"]
        map_height = data["map_height"]
        map_tileset = data["map_tileset"][0]
        if map_tileset == "": map_tileset = None
        map_color = data["map_bgcolor"]
        map_size = (map_width, map_height)

        old_width = params["width"]
        old_height = params["height"]
        old_tileset = params["tileset"]
        old_color = params["bgcolor"]
        old_size = (old_width, old_height)

        if map_size != old_size:
            self.canvas.resize(map_size)
        if map_tileset != old_tileset:
            event = pygame.event.Event(events.CHANGE_TILESET, tileset = map_tileset)
            self.event_queue.append(event)
        if map_color != old_color:
            self.canvas.set_bgcolor(map_color)
        
        self.close_prompt()        

    def create_project_fn(self, project_name: str, map_name: str):
        data = self.create_project_menu.get_input_data()
        project_name = data["project_name"]

        utils.create_project(project_name, map_name = map_name)

        event = pygame.event.Event(events.CHANGE_PROJECT, project = project_name)
        self.event_queue.append(event)

    def create_project_defer(self, *args):
        data = self.create_project_menu.get_input_data()
        project_name = data["project_name"]

        active["active_project"] = project_name
        self.update_tilesets([("", None)])
        self.defer = lambda map_name: self.create_project_fn(project_name, map_name)

        self._open(self.create_map_menu)
    
    def create_project_menu(self, height, width):
        self.create_project_menu = menu = pygame_menu.Menu(
            height, 800, "Novo projeto", center_content = False
        )
        menu.add_text_input(
            "Nome do projeto: ",
            textinput_id = "project_name",
            onreturn = self.create_project_defer,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_vertical_margin(150)
        menu.add_button(
            "Criar projeto",
            self.create_project_defer,
        )
        menu.add_button(
            "Voltar ao menu principal",
            pygame_menu.events.BACK,
            align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu
    
    def create_map_menu(
            self, title, height, width, defaults: dict = {}, mode: str = "new"
        ) -> pygame_menu.Menu:
        menu = pygame_menu.Menu(
            500, 800, title, center_content = False
        )
        tilesets: List[Tuple[str, Optional[str]]] = [("", None)] + [
            (ts, ts) for ts in utils.list_tilesets()
        ]

        menu.add_text_input(
            "Nome do mapa: ",
            textinput_id = "map_name",
            default = defaults.get("name", ""),
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_text_input(
            "Largura: ",
            textinput_id = "map_width",
            maxchar = 3,
            maxwidth = 3,
            default = defaults.get("width", 30),
            input_type = pygame_menu.locals.INPUT_INT,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_text_input(
            "Altura: ",
            textinput_id = "map_height",
            maxchar = 3,
            maxwidth = 3,
            default = defaults.get("height", 16),
            input_type = pygame_menu.locals.INPUT_INT,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_color_input(
            "Cor de fundo: ",
            color_id = "map_bgcolor",
            color_type = "hex",
            default = utils.rgb_to_hex(defaults.get("bgcolor", (0, 0, 0))),
            align = pygame_menu.locals.ALIGN_LEFT
        )
        map_tileset = defaults.get("tileset", None)
        default_tileset = tileset_index(tilesets, map_tileset)
        tileset_selector = menu.add_selector(
            "Selecione o tileset",
            tilesets,
            selector_id = "map_tileset",
            default = default_tileset,
            align = pygame_menu.locals.ALIGN_LEFT
        )

        menu.add_vertical_margin(50)

        if mode == "new":
            menu.add_button("Criar mapa", self.create_map_fn)
            self.tileset_selector = tileset_selector
        else:
            menu.add_button("Aplicar mudanças", self.edit_map_fn)
        
        menu.add_button(
            "Voltar ao menu principal", pygame_menu.events.BACK, align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu
    
    def map_edit_menu(self):
        self.map_params = params = self.canvas.get_map_params()
        self.edit_menu = edit_menu = self.create_map_menu(
            "Editar mapa", 500, 800, defaults = params, mode = "edit"
        )
        self._open(edit_menu)
