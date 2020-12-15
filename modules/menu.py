from typing import List, Optional, Tuple
import pygame
from tkinter.filedialog import asksaveasfilename, askopenfilename
import pygame_menu
from pygame_menu.widgets import TextInput
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
        self.tile_size_list = [
            ("16x16", 16), ("20x20", 20), ("32x32", 32), ("48x48", 48), ("64x64", 64)
        ]

        self.project_menu = project_menu = _ProjectMenu(self, height, width)
        self.map_selection_menu = map_selection_menu = _MapSelectionMenu(self, height, width)
        self.map_creation_menu = map_creation_menu =  self.create_map_menu("Novo mapa", height, width)
        self.menu_help = menu_help = self.help_menu(height, width)
        self.save_prompt = save_prompt = pygame_menu.Menu(
            250, 750, "Salvar", columns = 2, rows = 3, center_content = False
        )
        self.tileset_import_menu = tileset_import_menu = self.import_tileset_menu(height, width)

        self.add_button("Selecionar Projeto", project_menu)
        self.add_button("Novo Projeto", self.create_project_menu(height, width))
        self.add_button("Selecionar Mapa", map_selection_menu)
        if canvas is not None:
            self.add_button("Editar Mapa", self.map_edit_menu)
        self.add_button("Novo Mapa", map_creation_menu)
        self.add_button("Exportar como imagem", self.ask_save)
        self.add_button("Importar tileset", tileset_import_menu)
        self.add_button("Exportar projeto", self.export_project_fn)
        self.add_button("Ajuda", menu_help)
        self.add_button("Sair", pygame_menu.events.EXIT)

        save_prompt.add_label("Salvar alterações?", align = pygame_menu.locals.ALIGN_LEFT)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_button(
            "Sim", self.post_save_event, align = pygame_menu.locals.ALIGN_LEFT
        ).set_margin(30, 0)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_vertical_margin(50)
        save_prompt.add_button(
            "Não", self.close_prompt, align = pygame_menu.locals.ALIGN_RIGHT
        ).set_margin(-30, 0)

    def ask_save(self):
        filename = asksaveasfilename(defaultextension = ".png", filetypes = [("Imagem", ".png")])

        if filename:
            self.canvas.export_image(filename)

    def export_project_fn(self):
        filepath = asksaveasfilename(
            defaultextension = ".zip",
            filetypes = [("Arquivo comprimido", ".zip")],
            title = "Exportar projeto"
        )

        if filepath:
            event = pygame.event.Event(events.EXPORT_PROJECT, path = filepath)
            self.event_queue.append(event)
            self.open_save_prompt()

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
        bgimage_path = data["bgimage_path"]
        background = { "background_color": map_color }

        if self.defer is not None: self.defer(map_name)

        project_folder = config.default_folder()
        map_path = os.path.join(project_folder, "maps", map_name)
        os.mkdir(map_path)

        if bgimage_path:
            bgimage = utils.import_image(bgimage_path, map_name)
            background["image"] = bgimage

        map = Map(
            map_name,
            height = map_height,
            width = map_width,
            path = map_path,
            tileset = map_tileset,
            background = background
        )

        map.save_map()
        self.map_selection_menu.update_choices()

        event = pygame.event.Event(events.CHANGE_MAP, map = map_name)
        self.event_queue.append(event)

        self.open_save_prompt()

    def edit_map_fn(self):
        data = self.edit_menu.get_input_data()
        params = self.map_params
        canvas = self.canvas

        self.edit_menu = None
        self.map_params = None

        map_width = data["map_width"]
        map_height = data["map_height"]
        map_tileset = data["map_tileset"][0]
        if map_tileset == "": map_tileset = None
        map_color = data["map_bgcolor"]
        bgimage_path = data["bgimage_path"]
        if bgimage_path == "": bgimage_path = None

        map_name = params["name"]
        old_width = params["width"]
        old_height = params["height"]
        old_tileset = params["tileset"]
        old_color = params["bgcolor"]
        old_bgimage = params["bgimage"]

        map_size = (map_width, map_height)
        old_size = (old_width, old_height)

        if bgimage_path != old_bgimage:
            if bgimage_path:
                bgimage = utils.import_image(bgimage_path, map_name)
                canvas.set_bgimage(bgimage)
            else:
                canvas.unset_bgimage()
        if map_size != old_size:
            canvas.resize(map_size)
        if map_color != old_color:
            canvas.set_bgcolor(map_color)
        if map_tileset != old_tileset:
            event = pygame.event.Event(events.CHANGE_TILESET, tileset = map_tileset)
            self.event_queue.append(event)
        
        self.close_prompt()        

    def help_menu(self, height, width):
        menu = pygame_menu.Menu(
            700, 800, "Ajuda", center_content = False
        )
        
        first_label = menu.add_label(
            "Menu principal: [ESC]",
            align = pygame_menu.locals.ALIGN_LEFT
        )
        font_info = first_label.get_font_info()
        print(f"font info: {font_info}")
        font_config = {
            "font": font_info["name"],
            "font_size": 25,
            "color": font_info["color"],
            "selected_color": font_info["selected_color"],
            "background_color": None
        }
        first_label.set_font(**font_config)
        menu.add_label(
            "Trocar layer: teclas [1] - [4]",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Editar movimento: [M]",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Esconder layer atual: H",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Mostrar apenas layer atual: [T]",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Trocar tile atual: setas do teclado [cima]/[baixo] ou clicar no tile",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Mover mapa: scroll cima/baixo, setas do teclado [<-]/[->]",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Mover barra de tileset: scroll, com mouse em cima dela",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Posicionar tile: botão esquerdo do mouse",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Limpar tile: botão direito do mouse",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)
        menu.add_label(
            "Trocar modo de preenchimento: Teclas [L], [A], [B]",
            align = pygame_menu.locals.ALIGN_LEFT
        ).set_font(**font_config)

        menu.add_vertical_margin(50)
        menu.add_button(
            "Voltar ao menu principal",
            pygame_menu.events.BACK,
            align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu

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

    def bgimage_dialog(self, path_input: TextInput):
        value = path_input.get_value()
        initialfile = value or None
        filepath = askopenfilename(
            initialfile = initialfile,
            filetypes = [
                (
                    "Arquivos de Imagem",
                    (".png", ".jpg", ".bmp", ".tiff", ".webp")
                )
            ]
        )

        if filepath:
            path_input.set_value(filepath)

    def import_tileset_fn(self):
        data = self.tileset_import_menu.get_input_data()

        tileset_name = data["tileset_name"]
        tileset_path = data["tileset_path"]
        tile_size_index = data["tile_size"][1]
        tile_size = self.tile_size_list[tile_size_index][1]

        tileset_name = utils.import_tileset(tileset_path, tile_size, name = tileset_name)
        self.update_tilesets()

        self._back()

    def tileset_dialog(self, path_input: TextInput, name_input: Optional[TextInput] = None):
        value = path_input.get_value()
        initialfile = value or None
        filepath = askopenfilename(
            initialfile = initialfile,
            filetypes = [
                (
                    "Arquivos de Imagem",
                    (".png", ".jpg", ".bmp", ".tiff", ".webp")
                )
            ]
        )

        if filepath:
            path_input.set_value(filepath)
            if name_input and not name_input.get_value():
                name = utils.get_filename(filepath)
                name_input.set_value(name)      

    def import_tileset_menu(self, height, width):
        menu = pygame_menu.Menu(
            height, width, "Importar tileset", center_content = False
        )

        tileset_name = menu.add_text_input(
            "Nome do tileset: ",
            textinput_id = "tileset_name",
            align = pygame_menu.locals.ALIGN_LEFT
        )
        tileset_path = menu.add_text_input(
            "Arquivo: ",
            textinput_id = "tileset_path",
            maxwidth = 10,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_button(
            "Abrir arquivo",
            self.tileset_dialog,
            tileset_path,
            tileset_name,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_selector(
            "Tamanho dos tiles: ",
            self.tile_size_list,
            selector_id = "tile_size",
            align = pygame_menu.locals.ALIGN_LEFT
        )

        menu.add_button(
            "Importar",
            self.import_tileset_fn,
            align = pygame_menu.locals.ALIGN_CENTER
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
            650, 800, title, center_content = False
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
        bgimage_default = defaults.get("bgimage", None) or ""
        menu.add_label("Imagem de fundo: ", align = pygame_menu.locals.ALIGN_LEFT)
        bgimage_path = menu.add_text_input(
            "> ",
            textinput_id = "bgimage_path",
            maxwidth = 10,
            default = bgimage_default,
            align = pygame_menu.locals.ALIGN_LEFT
        )
        menu.add_button(
            "Abrir imagem",
            self.bgimage_dialog,
            bgimage_path,
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
            "Voltar ao menu principal",
            pygame_menu.events.BACK,
            align = pygame_menu.locals.ALIGN_CENTER
        )

        return menu
    
    def map_edit_menu(self):
        self.map_params = params = self.canvas.get_map_params()
        self.edit_menu = edit_menu = self.create_map_menu(
            "Editar mapa", 500, 800, defaults = params, mode = "edit"
        )
        self._open(edit_menu)
