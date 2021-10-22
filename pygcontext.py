
from __future__ import annotations

import pygame


class ContextReset(Exception):
    pass

class PygContext:

    def __init__(self, screen):
        self.screen = screen
        self.outcode = 0

    def start(self):
        self.screen.new_context(self)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, execls, exeins, tb):
        self.screen.elements = []

    def starting(self):
        pass

    def mouse_move(self, event: pygame.event.Event): pass
    def key_down(self, key: int): pass
    def key_up(self, key: int): pass
    def mouse_down(self, key: int, pos: tuple[int, int]): pass
    def mouse_up(self, key: int, pos: tuple[int, int]): pass
    def window_shown(self, event: pygame.event.Event): pass
    def activated(self, event: pygame.event.Event): pass
    def focussed(self, event: pygame.event.Event): pass
    def video(self, event: pygame.event.Event): pass
    def exposed(self, event: pygame.event.Event): pass
    def typing(self, event: pygame.event.Event): pass
    def unfocussed(self, event: pygame.event.Event): pass
    def mouse_wheel(self, event: pygame.event.Event): pass
    def resize(self, size: tuple[int, int]): pass
    def post_init(self): pass
    def quit(self): pass
    def update(self): pass

