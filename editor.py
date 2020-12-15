import os, sys
from typing import Tuple, Optional
from pygame.locals import *
import pygame
import tkinter
from PPlayMaps import Map, Tileset, config as conf
from PPlayMaps.types import Margin, Color, Vector, Vec
from modules import Canvas, TileBar, Menu, Label, events as editor_events, utils
config = conf.config
active = config["active"]

def get_positions(margin: Margin) -> Tuple[Vector, Vector]:
    tilebar_position = Vector(0, margin.top)
    label_position = Vector(margin.left, 2)

    return tilebar_position, label_position

def label_text(layer: int = 0, mode: int = 0, movement_layer: bool = False) -> str:
    layer_label = ["1", "2", "3", "4", "Movimento (M)"]
    if movement_layer:
        layer_label[-1] = f"[{layer_label[-1]}]"
    elif layer:
        layer_label[layer - 1] = f"[{layer_label[layer - 1]}]"
    mode_label = ["L", "- Lápis |", "A", "- Área |", "B", "- Balde de Tinta |"]
    if mode:
        mode_label[(mode - 1) * 2] = f"[{mode_label[(mode - 1) * 2]}]"
    return f"Camada: {' '.join(layer_label)} | Esconder/Mostrar - H | Somente atual - T | {' '.join(mode_label)}"

def load_map(name: str, canvas: Canvas, tile_bar: TileBar) -> Tuple[Map, Tileset]:
    map = Map.load(name)
    tileset = Tileset.load(name = map.tileset)

    utils.set_start_map(name)

    canvas.set_map(map, tileset)
    tile_bar.set_tileset(tileset)

    return map, tileset

def load_project(name: str, canvas: Canvas, tile_bar: TileBar) -> Tuple[Map, Tileset]:
    active["active_project"] = name
    project_path = config.default_folder(name)
    config.read(os.path.join(project_path, "project.ini"))
    config.write_changes()
    map_name = active["start_map"]

    return load_map(map_name, canvas, tile_bar)

def init_assets(
    canvas: Canvas,
    tile_size: Vec,
    margin: Margin,
    screen_size: Vec,
    project: Optional[str] = None,
    map_name: Optional[str] = None
) -> Tuple[Map, Tileset, TileBar, Label]:
    if project is not None:
        active["active_project"] = project
    project_path = config.default_folder(project)
    config.read(os.path.join(project_path, "project.ini"))
    if map_name == None:
        map_name = active["start_map"]
    else:
        active["start_map"] = map_name

    map = Map.load(map_name)
    tileset = Tileset.load(name = map.tileset)

    tilebar_position, label_position = get_positions(margin)

    tile_bar = TileBar(tileset, tilebar_position, screen_size, tile_size)
    menu_label = Label(label_text(), label_position)

    canvas.set_map(map, tileset)

    return map, tileset, tile_bar, menu_label

def compute_dimensions() -> Tuple[Vector, Vector, Vector, Vector, Vector, Margin]:
    info = pygame.display.Info()
    (curr_w, curr_h) = current_size = Vector(info.current_w, info.current_h)

    (vw, vh) = visible_map_size = Vector(30, 16)
    (tw, th)  = (vw + 2, vh + 2)
    screen_tile_size = tx, ty = (curr_w // tw, curr_h // th)
    min_tile = min(screen_tile_size)
    # min_tile_type = "x" if min_tile == tx else "y"
    screen_tile_size = tx, ty = (min_tile, min_tile)
    (mt, mr, mb, ml) = margin = Margin(20, 0, 0, tx + 2)
    canvas_position = Vector(ml, mt)
    # canvas_size = (cw, ch) = (vw * tx, vh * ty)
    canvas_size = Vector(curr_w - mr - ml, curr_h - mt - mb)

    return (
        canvas_position,
        visible_map_size,
        canvas_size,
        current_size,
        screen_tile_size,
        margin
    )

sizer_xy = None
def init_display() -> Tuple[Canvas, pygame.Surface, Vector, Vector, Margin]:
    global sizer_xy

    tk_root = tkinter.Tk()
    tk_root.withdraw()

    pygame.init()
    sizer_xy = pygame.cursors.compile(pygame.cursors.sizer_xy_strings)
    
    screen_size = active.get("screen_size", None)

    pygame.display.init()

    if screen_size is None:
        info = pygame.display.Info()
        # print(info)
        screen_size = info.current_w, info.current_h
    else:
        screen_size = screen_size.split("x")
        screen_size = (int(screen_size[0]), int(screen_size[1]))

    # print(f"Screen size: {screen_size}")
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE, 32) # 16x9 -> 32x18
    # print(" ---------------- Screen init ---------------- ")
    # info = pygame.display.Info()
    # print(info)

    (
        canvas_position,
        visible_map_size,
        canvas_size,
        current_size,
        screen_tile_size,
        margin
    ) = compute_dimensions()

    canvas = Canvas(
        canvas_position,
        visible_map_size,
        canvas_size,
        screen_tile_size
    )

    screen.fill((128, 128, 128))
    return canvas, screen, current_size, screen_tile_size, margin

def handle_resize(canvas: Canvas, tilebar: TileBar, label: Label):
    (
        canvas_position,
        visible_map_size,
        canvas_size,
        current_size,
        screen_tile_size,
        margin
    ) = compute_dimensions()

    canvas.on_resize(canvas_position, canvas_size, screen_tile_size)

    tilebar_position, label_position = get_positions(margin)

    tilebar.on_resize(tilebar_position, current_size, screen_tile_size)
    label.set_position(label_position)

def set_cursor(canvas: Canvas, mode: int):
    global sizer_xy
    if canvas.is_mouseouver():
        if mode == 1:
            pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            # pygame.mouse.set_cursor((24, 16), (9, 5), *sizer_x)
        if mode == 2:
            pygame.mouse.set_cursor((24, 16), (6, 6), *sizer_xy)
            # pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        if mode == 3:
            pygame.mouse.set_cursor(*pygame.cursors.diamond)
            # pygame.mouse.set_cursor((16, 24), (5, 9), *sizer_y)
    else:
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

def main():
    pygame.init()
    canvas, screen, current_size, screen_tile_size, margin = init_display()
    map, tileset, tile_bar, menu_label = init_assets(canvas, screen_tile_size, margin, current_size)
    menu = Menu(height = 500, width = 400, title = "Menu Principal", canvas = canvas)
    menu.disable()

    d = tileset.tile_size # delta
    x, y = pygame.mouse.get_pos()
    resize_count = 0
    selected_tile = tile_bar.selected_tile
    mode = 1

    mouse_left_pressed = False
    mouse_right_pressed = False
    drag_start = None
    drag_end = None
    drag_position = None
    drag_type = 0 # 1 left | -1 right

    layer = 1
    movement_layer = False

    clock = pygame.time.Clock()
    loop = True
    while loop:
        menu_label.set(label_text(layer, mode, movement_layer))
        screen.fill((128, 128, 128))
        canvas.draw_map()
        if movement_layer: canvas.blit_movement()
        tile_bar.blit()
        set_cursor(canvas, mode)

        events = pygame.event.get() 
        if menu.is_enabled():
            menu.update(events)      
        for event in events:
            if event.type == QUIT:
                loop = False
            elif event.type == pygame.VIDEORESIZE:
                resize_count += 1
                if resize_count > 1: handle_resize(canvas, tile_bar, menu_label)
            elif event.type == editor_events.CHANGE_PROJECT:
                map, tileset = load_project(event.project, canvas, tile_bar)
                selected_tile = 0
            elif event.type == editor_events.CHANGE_MAP:
                map, tileset = load_map(event.map, canvas, tile_bar)
                selected_tile = 0
            elif event.type == editor_events.CHANGE_TILESET:
                tileset_name = event.tileset
                tileset = canvas.set_tileset(tileset_name)
                selected_tile = tile_bar.set_tileset(tileset)
            elif event.type == editor_events.SAVE_CHANGES:
                map.save_map()
            elif menu.is_enabled():
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    menu.enable()
                # Salva mapa com Ctrl+S
                if event.key == K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # map.export()
                    map.save_map()
                    # utils.export_project("default")
                
                if event.key == K_c:
                    selected_tile = canvas.get_tile(canvas.get_map_xy(), layer)
                    tile_bar.set_tile(selected_tile)
                
                # =================== TOGGLE =================== #
                if event.key == K_h:
                    canvas.set_layer_visibility(layer)
                if event.key == K_t:
                    canvas.toggle_layer(layer)

                # =================== Modo de preenchimento =================== #
                if event.key == K_l:
                    mode = 1
                if event.key == K_a:
                    mode = 2
                if event.key == K_b:
                    mode = 3
                if event.key == K_m:
                    movement_layer = not movement_layer

                # =================== Rolar mapa =================== #
                if event.key == K_UP:
                    selected_tile = tile_bar.change_tile(-1)
                if event.key == K_DOWN:
                    selected_tile = tile_bar.change_tile(1)
                if event.key == K_RIGHT:
                    canvas.scroll(1, 0)
                if event.key == K_LEFT:
                    canvas.scroll(-1, 0)

                # =================== Mostra posição do mouse ===================
                if event.key == K_y:
                    print(f"Mouse pos: ({x}, {y})")
                    print(f"Screen size: {current_size}")
                    print(f"Screen tile: {screen_tile_size}")

                ################### TROCAR CAMADA ########################
                if  K_1 <= event.key <= K_4:
                    layer = event.key - 48 # K_1 = 49
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                if tile_bar.is_mouseouver() and button == BUTTON_LEFT:
                    selected_tile = tile_bar.click()
                elif button == BUTTON_LEFT:
                    if mode == 1:
                        if movement_layer:
                            canvas.place_tile(1, canvas.get_map_xy(), layer, movement_layer = True)
                        else:
                            canvas.place_tile(selected_tile, canvas.get_map_xy(), layer) # Insere tile
                    elif mode == 2:
                        if mouse_right_pressed:
                            mouse_right_pressed = False
                            drag_start = None
                            drag_position = None
                            drag_type = 0
                        elif mouse_left_pressed:
                            pass
                        else:
                            mouse_left_pressed = True
                            drag_type = 1
                            drag_start = canvas.get_map_xy()
                            drag_position = canvas.get_xy()
                    elif mode == 3:
                        if movement_layer:
                            canvas.flood_fill(1, canvas.get_map_xy(), layer, movement_layer = True)
                        else:
                            canvas.flood_fill(selected_tile, canvas.get_map_xy(), layer)
                        
                elif button == BUTTON_RIGHT:
                    if mode == 1:
                        canvas.place_tile(0, canvas.get_map_xy(), layer, movement_layer = movement_layer) # Remove tile
                    elif mode == 2:
                        if mouse_left_pressed:
                            mouse_left_pressed = False
                            drag_start = None
                            drag_position = None
                            drag_type = 0
                        elif mouse_right_pressed:
                            pass
                        else:
                            mouse_right_pressed = True
                            drag_type = -1
                            drag_start = canvas.get_map_xy()
                            drag_position = canvas.get_xy()
                    elif mode == 3:
                        canvas.flood_fill(0, canvas.get_map_xy(), layer, movement_layer = movement_layer)
                
                # Trocar tile atual - Roda do mouse
                if canvas.is_mouseouver():
                    if button == 4: # para baixo
                        canvas.scroll(0, -1)
                    if button == 5: # para cima
                        canvas.scroll(0, 1)
                elif tile_bar.is_mouseouver():
                    if button == 4: # para baixo
                        selected_tile = tile_bar.scroll(-1)
                    if button == 5: # para cima
                        selected_tile = tile_bar.scroll(1)

            elif event.type == pygame.MOUSEBUTTONUP:
                if mode == 2:
                    button = event.button
                    if button == BUTTON_LEFT and mouse_left_pressed:
                        mouse_left_pressed = False
                        drag_end = canvas.get_map_xy()
                    elif button == BUTTON_RIGHT and mouse_right_pressed:
                        mouse_right_pressed = False
                        drag_end = canvas.get_map_xy()
        
        if (mouse_left_pressed or mouse_right_pressed) and mode == 2:
            mx, my = canvas.get_xy()
            px, py = drag_position
            if px > mx:
                px, mx = mx, px
            if py > my:
                py, my = my, py
            dx, dy = (abs(px - mx) + 1, abs(py - my))
            drag_pos = (px * d, py * d)
            drag_len = (dx * d, dy * d)
            drag_rect = (*drag_pos, *drag_len)
            pygame.draw.rect(canvas.display, (24, 144, 255), drag_rect, width = 1)
            drag_surface = pygame.Surface(drag_len)
            drag_surface.set_alpha(96)
            drag_surface.fill((24, 144, 255))
            canvas.display.blit(drag_surface, drag_pos)

        if drag_start and drag_end:
            if movement_layer:
                fill_tile = 1 if drag_type == 1 else 0
            else:
                fill_tile = selected_tile if drag_type == 1 else 0
            canvas.fill_area(
                fill_tile, 
                drag_start,
                drag_end,
                layer,
                movement_layer = movement_layer,
            )
            drag_start, drag_end, drag_position = None, None, None
            drag_type = 0

        # canvas.pointer_tile(selected_tile)
        tile_bar.draw_self(screen)
        menu_label.blit(screen)
        canvas.draw_self(screen)
        if menu.is_enabled():
            menu.draw(screen)
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()