"""Spiellogik und Darstellung des Autobahnspiels."""

import random

import pygame

from autobahn import settings
from autobahn.sprites import Coin, EnemyCar, PlayerCar, random_free_lane

START_MENU = "start-menu"
PLAYING = "game"
GAME_OVER = "game-over"


class Game:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.state = START_MENU
        self.high_score = 0
        self.reset()

    def reset(self):
        self.player = PlayerCar()
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemy_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.score = 0
        self.lives = settings.START_LIVES
        self.level = 0
        self.frame = 0           # Frames im aktuellen Level
        self.enemy_timer = 0
        self.coin_timer = 0
        self.invulnerable = 0
        self.road_offset = 0

    @property
    def speed(self):
        return settings.LEVELS[self.level]["car_speed"]

    @property
    def time_left(self):
        return max(0, settings.LEVEL_DURATION - self.frame // settings.FPS)

    # --- Eingaben ---------------------------------------------------------

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.state in (START_MENU, GAME_OVER) and event.key == pygame.K_SPACE:
            self.reset()
            self.state = PLAYING
        elif self.state == PLAYING and event.key == pygame.K_ESCAPE:
            self.state = START_MENU

    # --- Spiellogik pro Frame ---------------------------------------------

    def update(self, keys):
        if self.state != PLAYING:
            return

        self.player.update(keys)
        self._spawn()
        self.enemy_group.update()
        self.coin_group.update()
        self._check_collisions()
        self._advance_time()

    def _spawn(self):
        self.enemy_timer += 1
        if self.enemy_timer >= settings.LEVELS[self.level]["car_frequency"]:
            lane = random_free_lane(self.enemy_group, self.rng)
            self.enemy_group.add(EnemyCar(lane, self.speed))
            self.enemy_timer = 0

        self.coin_timer += 1
        if self.coin_timer >= settings.COIN_INTERVAL:
            lane = random_free_lane(self.enemy_group, self.rng)
            self.coin_group.add(Coin(lane, self.speed))
            self.coin_timer = 0

    def _check_collisions(self):
        for _ in pygame.sprite.spritecollide(self.player, self.coin_group, True, pygame.sprite.collide_mask):
            self.score += settings.COIN_POINTS

        if self.invulnerable > 0:
            self.invulnerable -= 1
            return

        if pygame.sprite.spritecollide(self.player, self.enemy_group, True, pygame.sprite.collide_mask):
            self.lives -= 1
            self.invulnerable = settings.INVULNERABLE_FRAMES
            if self.lives <= 0:
                self.high_score = max(self.high_score, self.score)
                self.state = GAME_OVER

    def _advance_time(self):
        self.frame += 1
        self.road_offset = (self.road_offset + self.speed) % 80
        if self.time_left == 0:
            self.frame = 0
            self.level = min(self.level + 1, len(settings.LEVELS) - 1)

    # --- Darstellung --------------------------------------------------------

    def draw(self, screen, font, title_font):
        if self.state == START_MENU:
            self._draw_menu(screen, title_font, font, settings.TITLE, "Leertaste: Start  ·  Pfeiltasten: Fahren")
        elif self.state == GAME_OVER:
            self._draw_menu(screen, title_font, font, "Game Over",
                            f"Punkte: {self.score}  ·  Highscore: {self.high_score}  ·  Leertaste: Neues Spiel")
        else:
            self._draw_road(screen)
            self.coin_group.draw(screen)
            self.enemy_group.draw(screen)
            # Während der Unverwundbarkeit blinkt das Spielerauto
            if self.invulnerable // 6 % 2 == 0:
                self.player_group.draw(screen)
            self._draw_status(screen, font)

    def _draw_road(self, screen):
        screen.fill(settings.ROAD_COLOR)
        for lane in range(1, settings.LANE_COUNT):
            x = lane * settings.LANE_WIDTH
            for y in range(-80 + self.road_offset, settings.SCREEN_HEIGHT, 80):
                pygame.draw.rect(screen, settings.LINE_COLOR, (x - 2, y, 4, 40))

    def _draw_status(self, screen, font):
        lines = [
            f"Punkte: {self.score}",
            f"Level: {self.level + 1}",
            f"Zeit: {self.time_left}",
            f"Leben: {self.lives}",
        ]
        for i, text in enumerate(lines):
            surface = font.render(text, True, settings.WHITE)
            background = pygame.Surface((surface.get_width() + 12, surface.get_height() + 4), pygame.SRCALPHA)
            background.fill((0, 0, 0, 150))
            screen.blit(background, (6, 8 + i * 36))
            screen.blit(surface, (12, 10 + i * 36))

    def _draw_menu(self, screen, title_font, font, title, subtitle):
        screen.fill(settings.BLACK)
        title_surface = title_font.render(title, True, settings.YELLOW)
        subtitle_surface = font.render(subtitle, True, settings.WHITE)
        center_x, center_y = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        screen.blit(title_surface, title_surface.get_rect(center=(center_x, center_y - 40)))
        screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(center_x, center_y + 30)))


def run():
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    font = pygame.font.SysFont("arial", 30)
    title_font = pygame.font.SysFont("arial", 64, bold=True)
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                                             and game.state != PLAYING):
                pygame.quit()
                return
            game.handle_event(event)

        game.update(pygame.key.get_pressed())
        game.draw(screen, font, title_font)
        pygame.display.flip()
        clock.tick(settings.FPS)
