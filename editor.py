import os
from pygame.locals import *
import pygame
from time import time
from tkinter import filedialog
from PPlayMaps import Map, Tileset, config as conf, tileset
from modules import Canvas, TileBar, tile_bar
config = conf.config
active = config["active"]

class Label:
    def __init__(self, text, x, y):
        self.x = x
        self.y = y
        self.surface = font.render(text, 1, (255, 255, 255))
        self.surface.fill((0,0,0))

    def set(self, text, color = "White"):
        self.surface = font.render(text, 1, pygame.Color(color))
        size = w, h = self.surface.get_size()
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.surface2 = pygame.Surface(size)
        self.surface2.blit(self.surface, (0, 0))

def init_assets(canvas: Canvas, project = None, map_name = None):
    if project is not None:
        active["active_project"] = project
    project_path = config.default_folder(project)
    config.read(os.path.join(project_path, "project.ini"))
    if map_name == None:
        map_name = active["start_map"]
    else:
        active["start_map"] = map_name

    canvas_tile_size = canvas.screen_tile_size

    map = Map.load(map_name)
    tileset = Tileset.load(name = map.tileset)
    tile_bar = TileBar(tileset, (1, 20), canvas_tile_size, 16)

    canvas.set_map(map, tileset)

    return map, tileset, tile_bar


pygame.font.init()
font = pygame.font.SysFont("Arial", 14)
sizer_xy = None
def init_display():
    global sizer_xy

    pygame.init()
    sizer_xy = pygame.cursors.compile(pygame.cursors.sizer_xy_strings)
    
    screen_size = active["screen_size"]
    screen_size = screen_size.split("x")
    screen_size = (sw, sh) = (int(screen_size[0]), int(screen_size[1]))

    # screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE, 32) # 16x9 / 32x16
    # info = pygame.display.Info()
    # screen_size = (sw, sh) = info.current_w, info.current_h
    
    visible_map_size = (vw, vh) = (30, 15)
    total_size = (tw, th)  = (vw + 2, vh + 1)
    # tile_size = tx, ty = (sw // tw, sh // th)
    tile_size = (tx, ty) = (48, 48)
    margin = (mt, mr, mb, ml) = (20, 0, 0, tx + 2)
    canvas_position = (cx, cy) = (ml, mt)
    canvas_size = (cw, ch) = (vw * tx, vh * ty)

    canvas = Canvas(canvas_position, visible_map_size, canvas_size)
    # cx, cy = canvas.position
    # cw, ch = canvas.size

    window_size = (tw * tx, th * ty) # 1490, 788 -> 1440, 768 + (50, 20) -> 30x48, 16x48
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE, 32) # 16x9 / 32x16
    screen.fill((128, 128, 128))
    return canvas, screen, window_size

def tiles_onscroll(selected_tile, direction, size):
    selected_tile += direction
    if selected_tile < 0:
        selected_tile = size - 1
    if selected_tile > size - 1:
        selected_tile = 0
    return selected_tile

def label_text(layer, mode, movement_layer = False):
    layer_label = ["1", "2", "3", "4", "Movimento (M)"]
    if movement_layer:
        layer_label[-1] = f"[{layer_label[-1]}]"
    else:
        layer_label[layer - 1] = f"[{layer_label[layer - 1]}]"
    mode_label = ["L", "- Lápis |", "A", "- Área |", "B", "- Balde de Tinta |"]
    mode_label[(mode - 1) * 2] = f"[{mode_label[(mode - 1) * 2]}]"
    return f"Camada: {' '.join(layer_label)} | Esconder/Mostrar - H | Somente atual - T | {' '.join(mode_label)}"

def set_cursor(canvas: Canvas, mode: int):
    global sizer_xy
    pos = pygame.mouse.get_pos()
    if canvas.get_rect().collidepoint(pos):
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
    canvas, screen, window_size = init_display()
    map, tileset, tile_bar = init_assets(canvas)
    d = tileset.tile_size # delta
    clock = pygame.time.Clock()
    pos = x, y = pygame.mouse.get_pos()
    selected_tile = 0
    mode = 1

    mouse_left_pressed = False
    mouse_right_pressed = False
    drag_start = None
    drag_end = None
    drag_type = 0 # 1 left | -1 right

    layer = 1
    movement_layer = False
    menu_label = Label(label_text(1, 1), 15, 0)

    loop = True
    while loop:
        menu_label.set(label_text(layer, mode, movement_layer))
        screen.fill((128, 128, 128))
        canvas.draw_map()
        if movement_layer: canvas.blit_movement()
        tile_bar.blit(selected_tile)
        set_cursor(canvas, mode)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    loop = False
                # Salva mapa com 's'
                if event.key == K_s:
                    # num_file = len(os.listdir())
                    # map_name = f"map{num_file}.png"
                    # pygame.image.save(screen, map_name)
                    map.export()
                    map.save_map()
                    # os.startfile(map_name)
                
                if event.key == K_c:
                    selected_tile = map.get_tile(canvas.get_xy(), layer)
                
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

                # =================== Mostra posição do mouse ===================
                if event.key == K_y:
                    x, y = pygame.mouse.get_pos()
                    text = font.render(f"{x}, {y}", 1, (255, 69, 0))
                    canvas.display.blit(text, (5, 5))

                ################### TROCAR CAMADA ########################
                if  K_1 <= event.key <= K_4:
                    layer = event.key - 48 # K_1 = 49
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                if button == BUTTON_LEFT:
                    if mode == 1:
                        if movement_layer:
                            map.place_tile(1, canvas.get_xy(), layer, movement_layer = True)
                        else:
                            map.place_tile(selected_tile, canvas.get_xy(), layer) # Insere tile
                    elif mode == 2:
                        if mouse_right_pressed:
                            mouse_right_pressed = False
                            drag_start = None
                            drag_type = 0
                        elif mouse_left_pressed:
                            pass
                        else:
                            mouse_left_pressed = True
                            drag_type = 1
                            drag_start = canvas.get_xy()
                    elif mode == 3:
                        if movement_layer:
                            map.flood_fill(1, canvas.get_xy(), layer, movement_layer = True)
                        else:
                            map.flood_fill(selected_tile, canvas.get_xy(), layer)
                        
                elif button == BUTTON_RIGHT:
                    if mode == 1:
                        map.place_tile(0, canvas.get_xy(), layer, movement_layer = movement_layer) # Remove tile
                    elif mode == 2:
                        if mouse_left_pressed:
                            mouse_left_pressed = False
                            drag_start = None
                            drag_type = 0
                        elif mouse_right_pressed:
                            pass
                        else:
                            mouse_right_pressed = True
                            drag_type = -1
                            drag_start = canvas.get_xy()
                    elif mode == 3:
                        map.flood_fill(0, canvas.get_xy(), layer, movement_layer = movement_layer)

            elif event.type == pygame.MOUSEBUTTONUP:
                if mode == 2:
                    button = event.button
                    if button == BUTTON_LEFT and mouse_left_pressed:
                        mouse_left_pressed = False
                        drag_end = canvas.get_xy()
                    elif button == BUTTON_RIGHT and mouse_right_pressed:
                        mouse_right_pressed = False
                        drag_end = canvas.get_xy()
            
            # Trocar tile atual - Roda do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # para baixo
                    selected_tile = tiles_onscroll(selected_tile, -1, len(tileset))
                if event.button == 5: # para cima
                    selected_tile = tiles_onscroll(selected_tile, 1, len(tileset))
        
        if (mouse_left_pressed or mouse_right_pressed) and mode == 2:
            mx, my = canvas.get_xy()
            px, py = drag_start
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
            map.fill_area(
                fill_tile, 
                drag_start,
                drag_end,
                layer,
                movement_layer = movement_layer,
            )
            drag_start, drag_end = None, None
            drag_type = 0

        # canvas.pointer_tile(selected_tile)
        tile_bar.draw_self(screen)
        screen.blit(menu_label.surface, (50, 2))
        canvas.draw_self(screen)
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()