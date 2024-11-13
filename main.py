from email.mime import image
import pygame
import random
import sys
from pygame.locals import *

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (0, 255, 255)

# Spielkonstanten
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
LANE_WIDTH = SCREEN_WIDTH // 6
CAR_WIDTH = 60
CAR_HEIGHT = 120
FPS = 60

# Levels: Autos pro Level und Geschwindigkeit
LEVELS = [
    {'car_speed': 5, 'car_frequency': 50},  # Level 1
    {'car_speed': 7, 'car_frequency': 40},  # Level 2
    {'car_speed': 9, 'car_frequency': 30},  # Level 3
    {'car_speed': 11, 'car_frequency': 20},  # Level 4
    # Weitere Levels können hier hinzugefügt werden
]

GAME_STATE = "start-menu"



# Initialisiere pygame
pygame.init()

# Setze das Fenster
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Autobahnspiel")

# Schriftart für die Anzeige
font = pygame.font.SysFont(None, 36)

# Zeit und Level
level = 0
level_timer = 60  # 60 Sekunden pro Level
score = 0

# Spielstatus
clock = pygame.time.Clock()

# Spieler-Auto-Klasse
class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.image.load("assets/images/main_car.png").convert()
        self.image = pygame.transform.scale(self.image, (100, 180))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 10
    
    def update(self, keys):
        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.top < SCREEN_HEIGHT:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.bottom > 0:
            self.rect.y += self.speed

# Gegner-Auto-Klasse
class EnemyCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.image.load("assets/images/enemy_car.png").convert()
        self.image = pygame.transform.scale(self.image, (100, 180))
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([i * LANE_WIDTH for i in range(6)])
        self.rect.y = -CAR_HEIGHT
        self.speed = LEVELS[level]['car_speed']
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # Entfernt das Auto, wenn es den Bildschirm verlässt

# Münzen-Klasse
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/images/coin.png").convert()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([i * LANE_WIDTH for i in range(6)])
        self.rect.y = random.randint(0, SCREEN_HEIGHT // 2)
    
    def update(self):
        pass  # Münzen bewegen sich nicht

# Funktion, um den Timer, Punktestand und Level anzuzeigen
def draw_status(screen, score, level, time_left):
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level+1}", True, WHITE)
    timer_text = font.render(f"Time: {time_left}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(timer_text, (10, 90))

# Funktion, um das Startmenu darzustellen
def draw_start_menu():
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('arial', 40)
    title = font.render('My Game', True, (155, 255, 255))
    start_button = font.render('(space) Start', True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH/2 - title.get_width()/2, SCREEN_HEIGHT/2 - title.get_height()/2))
    screen.blit(start_button, (SCREEN_WIDTH/2 - start_button.get_width()/2, SCREEN_HEIGHT/2 + start_button.get_height()/2))
    pygame.display.update()

# Hauptspiel-Funktion
def main_game():
    global level, level_timer, score, GAME_STATE
    player = PlayerCar()
    player_group = pygame.sprite.Group(player)
    enemy_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()

    enemy_timer = 0
    coin_timer = 0
    game_timer = 0

    running = True
    while running:
        # Ereignisprüfung
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if GAME_STATE == "start-menu":
            draw_start_menu()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                GAME_STATE = "game"

        if GAME_STATE == "game":        
            keys = pygame.key.get_pressed()
            player.update(keys)

            if keys[pygame.K_ESCAPE]:
                GAME_STATE = "start-menu"
            
            # Autos generieren
            enemy_timer += 1
            if enemy_timer >= LEVELS[level]['car_frequency']:
                enemy_car = EnemyCar()
                enemy_group.add(enemy_car)
                enemy_timer = 0
            
            # Münzen generieren
            coin_timer += 1
            if coin_timer >= 300:  # alle 5 Sekunden
                coin = Coin()
                coin_group.add(coin)
                coin_timer = 0

            # Aktualisiere Gegner und Münzen
            enemy_group.update()
            coin_group.update()

            # Kollisionen prüfen
            if pygame.sprite.spritecollide(player, enemy_group, True):
                score -= 10  # Punkteabzug bei Kollision
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 10  # Punkte für das Einsammeln einer Münze
            
            # Bildschirm aktualisieren
            screen.fill(BLACK)
            player_group.draw(screen)
            enemy_group.draw(screen)
            coin_group.draw(screen)
            
            # Timer und Level berechnen
            game_timer += 1
            time_left = max(0, level_timer - game_timer // FPS)
            if time_left == 0:
                game_timer = 0
                level += 1
                if level >= len(LEVELS):
                    level = len(LEVELS) - 1  # Maximallevel
                level_timer = 60  # Zurücksetzen des Level-Timers

            # Statusleiste anzeigen
            draw_status(screen, score, level, time_left)

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    print("new branch")
    main_game()
