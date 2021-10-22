
from __future__ import annotations

from dataclasses import dataclass

import pygame

class Element:
    """
    Simple drawable screen element. Has optional collision and multiple texture support
    (for layering).

    """

    _pos: tuple[float, float]
    _texture: pygame.surface.Surface

    def __init__(self, screen, pos: tuple[int, int]):
        self.screen = screen
        self.screen.add_element(self)
        self.pos = pos
        self.i = 0

    def draw(self, surface: pygame.surface.Surface) -> pygame.rect.Rect:
        return surface.blit(self.texture, self.pos)

    @property
    def pos(self) -> tuple[int, int]:
        return int(self._pos[0]), int(self._pos[1])

    @pos.setter
    def pos(self, pos: tuple[float, float]):
        self._pos = pos

    @property
    def texture(self) -> pygame.surface.Surface:
        return self._texture

    @texture.setter
    def texture(self, texture: pygame.surface.Surface):
        self._texture = texture
        self.size = texture.get_size()

    @property
    def centre(self) -> tuple[int, int]:
        dx, dy = self.size
        return int(self.pos[0] + dx / 2), int(self.pos[1] + dy / 2)

