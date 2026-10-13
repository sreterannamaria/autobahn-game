"""Sprites: Spielerauto, Gegnerautos und Münzen."""

import random

import pygame

from autobahn import settings


def load_image(name, size):
    """Lädt ein Bild mit Transparenz und skaliert es auf die gewünschte Grösse."""
    image = pygame.image.load(settings.IMAGE_DIR / name)
    if pygame.display.get_surface() is not None:
        image = image.convert_alpha()  # convert() würde den transparenten Hintergrund schwarz füllen
    return pygame.transform.smoothscale(image, size)


def lane_center(lane):
    return lane * settings.LANE_WIDTH + settings.LANE_WIDTH // 2


class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("main_car.png", settings.PLAYER_SIZE)
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = settings.PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        # Das Auto bleibt immer vollständig im Bild
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, lane, speed):
        super().__init__()
        self.image = load_image("enemy_car.png", settings.ENEMY_SIZE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(centerx=lane_center(lane), bottom=0)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()  # Entfernt das Auto, wenn es den Bildschirm verlässt


class Coin(pygame.sprite.Sprite):
    """Münzen liegen auf der Strasse und bewegen sich mit ihr nach unten."""

    def __init__(self, lane, speed):
        super().__init__()
        self.image = load_image("coin.png", settings.COIN_SIZE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(centerx=lane_center(lane), bottom=0)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()


def random_free_lane(blocking_sprites, rng=random):
    """Wählt eine Spur, in der am oberen Rand gerade kein Gegner startet."""
    blocked = {s.rect.centerx // settings.LANE_WIDTH for s in blocking_sprites if s.rect.top < settings.ENEMY_SIZE[1]}
    free = [lane for lane in range(settings.LANE_COUNT) if lane not in blocked]
    return rng.choice(free or list(range(settings.LANE_COUNT)))
