from os.path import join
import pygame
from PPlay.window import Window
from PPlay.sprite import Sprite
from PPlayMaps import GameScenario

def convert_time(seconds: int):
    ss = seconds % 60
    mm = (seconds // 60) % 60
    # hh = (ms / (1000 * 60 * 60)) % 24
    return f"{mm:02d}:{ss:02d}"

window = Window(960, 512)
window.set_title("Pacman")
screen = Window.get_screen()
keyboard = Window.get_keyboard()

scenario = GameScenario((0, 0), (30, 16), (960, 512))
scenario.load_map("map00")
font = pygame.font.SysFont("Arial", 30)
victory_font = pygame.font.SysFont("Arial", 48)

hero = Sprite(join("res", "pacman-sprite.png"), 3)
hero.set_total_duration(900)
scenario.place_hero(hero, (0, 5))

fps = 24
frame = 0
max_speed = 8
moved_x, moved_y = False, False

score = 0
paused = False
victory = False
pause_text = font.render("Jogo Pausado", True, (255, 255, 255))
victory_text = None
subtext = None

loop = True
clock = pygame.time.Clock()
while(loop):

    if keyboard.key_pressed("ESC"):
        loop = False
    
    if keyboard.key_pressed("P"):
        paused = victory or not paused
        pygame.time.wait(200)

    if not paused:
        if (frame % (fps // max_speed)) == 0:
            moved_x, moved_y = False, False 

        if not (moved_x or moved_y):
            moved_x, moved_y = scenario.move_hero_keys()
        elif not moved_x:
            scenario.move_hero_key_x()
        elif not moved_y:
            scenario.move_hero_key_y()

        if layer := scenario.stepping_on(76):
            position = scenario.hero_position
            score += 1
            scenario.place_tile(0, position, layer)
        
        frame += 1
        scenario.update()

    if not victory and score == 128: # 128
        seconds = frame // fps
        victory, paused = True, True
        time = convert_time(seconds)
        victory_text = victory_font.render("Vitória!", True, (255, 255, 255))
        subtext = font.render(
            f"Você completou com um score de {score} em {time}", True, (255, 255, 255)
        )

    text = font.render(f"Score: {score:03d}", True, (255, 255, 255))
    scenario.draw()
    screen.blit(text, (0, 0))

    if victory:
        screen.blit(victory_text, (432, 208))
        screen.blit(subtext, (192, 256))
    elif paused:
        screen.blit(pause_text, (432, 208))

    window.update()
    clock.tick(fps)
