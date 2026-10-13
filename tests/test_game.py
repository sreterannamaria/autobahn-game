import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from autobahn import settings  # noqa: E402
from autobahn.game import GAME_OVER, PLAYING, START_MENU, Game  # noqa: E402
from autobahn.sprites import Coin, EnemyCar, random_free_lane  # noqa: E402


class Keys:
    """Ersetzt pygame.key.get_pressed() mit einer festen Menge gedrückter Tasten."""

    def __init__(self, *pressed):
        self.pressed = set(pressed)

    def __getitem__(self, key):
        return key in self.pressed


@pytest.fixture
def game():
    pygame.init()
    g = Game(rng=random.Random(1))
    g.state = PLAYING
    yield g
    pygame.quit()


def press(game, key):
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


def test_space_starts_and_escape_returns_to_menu(game):
    game.state = START_MENU
    press(game, pygame.K_SPACE)
    assert game.state == PLAYING
    press(game, pygame.K_ESCAPE)
    assert game.state == START_MENU


@pytest.mark.parametrize("key", [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
def test_player_stays_on_screen(game, key):
    for _ in range(500):
        game.player.update(Keys(key))
    screen = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    assert screen.contains(game.player.rect)


def test_collecting_a_coin_adds_points(game):
    coin = Coin(lane=0, speed=0)
    coin.rect.center = game.player.rect.center
    game.coin_group.add(coin)
    game._check_collisions()
    assert game.score == settings.COIN_POINTS
    assert not game.coin_group


def test_collision_costs_a_life_and_grants_short_invulnerability(game):
    for _ in range(2):
        enemy = EnemyCar(lane=0, speed=0)
        enemy.rect.center = game.player.rect.center
        game.enemy_group.add(enemy)
    game._check_collisions()
    assert game.lives == settings.START_LIVES - 1
    game._check_collisions()  # zweites Auto trifft während der Unverwundbarkeit
    assert game.lives == settings.START_LIVES - 1


def test_last_life_ends_the_game_and_keeps_high_score(game):
    game.lives = 1
    game.score = 40
    enemy = EnemyCar(lane=0, speed=0)
    enemy.rect.center = game.player.rect.center
    game.enemy_group.add(enemy)
    game._check_collisions()
    assert game.state == GAME_OVER
    assert game.high_score == 40


def test_level_increases_after_level_duration_and_stops_at_last_level(game):
    for _ in range(settings.LEVEL_DURATION * settings.FPS):
        game._advance_time()
    assert game.level == 1
    game.level = len(settings.LEVELS) - 1
    for _ in range(settings.LEVEL_DURATION * settings.FPS):
        game._advance_time()
    assert game.level == len(settings.LEVELS) - 1


def test_enemies_leave_the_screen_and_are_removed(game):
    enemy = EnemyCar(lane=2, speed=settings.SCREEN_HEIGHT)
    game.enemy_group.add(enemy)
    game.enemy_group.update()
    game.enemy_group.update()
    assert not game.enemy_group


def test_new_enemies_do_not_spawn_on_top_of_each_other():
    pygame.init()
    blocking = [EnemyCar(lane=lane, speed=0) for lane in range(settings.LANE_COUNT - 1)]
    assert random_free_lane(blocking) == settings.LANE_COUNT - 1


def test_game_runs_for_a_while_without_errors(game):
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 30)
    for _ in range(30 * settings.FPS):
        game.update(Keys(pygame.K_LEFT))
        game.draw(screen, font, font)
        if game.state == GAME_OVER:
            break
    assert game.state in (PLAYING, GAME_OVER)
