
from __future__ import annotations

import os
import shutil
import sys
import time
from collections.abc import Sequence
from contextlib import suppress
from functools import cache, lru_cache
from typing import Callable

import pygame

from element import Element
from pygcontext import PygContext

# event codes. VSCODE doesn't recognise pygame.<event_name> properly so they're relisted here.
MMOTION, KDOWN, KUP, MBDOWN, MBUP, QUIT = 1024, 768, 769, 1025, 1026, 256
WINSHOW, ACTIVATED, FOCUS = 32774, 32768, 32785
TEXT_EDIT, VIDEO, WINEXPOSED = 770, 32770, 32776
TEXT_ENTER, UNFOCUS = 771, 32786
M_WHEEL, RESIZE = 1027, 32778
SET_RESIZABLE = 16
NOT_RESIZABLE = 0
LEFT_CLICK = 1
SRCALPHA = 65536
# this is purely a vscode workaround

# no longer needed due to PyLance update but will stay for now


# keyboard keys.
PAGE_UP, PAGE_DOWN = 1073741899, 1073741902

# work out where the program is running to find texture files.
ROUTE = "\\".join(sys.argv[0].split("\\")[:-1:]) + "\\"
ROUTE_ALT = "/".join(sys.argv[0].split("/")[:-1:]) + "/"
# sometimes the route given by sys.argv[0] uses `/` as a split and sometimes `\`
# so this hack fixes that
if len(ROUTE) < len(ROUTE_ALT):
    ROUTE = ROUTE_ALT
TEXTURE_ROUTES = ROUTE + "assets/"
LOG_ROUTES = ROUTE + "logs/"

# hacky assemble textures folder
try:
    os.mkdir(TEXTURE_ROUTES)
except OSError:
    pass

IMAGE_EXTENSIONS = (".jpg", ".png")
# pull files from top level and place in assets/
for route in os.listdir("."):
    if os.path.isfile(route) and route[-4::] in IMAGE_EXTENSIONS:
        try:
            shutil.copy(route, TEXTURE_ROUTES + route)
        except shutil.SameFileError:
            pass
        try:
            os.remove(route)
        except FileNotFoundError:
            pass


# texture loading utilities
# all textures loaded once are cached until the application closes
@cache 
def load_texture(route: str) -> pygame.surface.Surface:
    try:
        return pygame.image.load(TEXTURE_ROUTES + route).convert_alpha()
    except FileNotFoundError:
        raise

# a large amount of cache is allocated to scaling since lots of scaled draw calls
# need to be made when the screen chages that are expensive even if most of the
# objects on screen will have the exact same scale as they had previously
@lru_cache(maxsize=128)
def load_and_scale(route: str, scale: tuple[float, float]):
    start = load_texture(route)
    size = start.get_size()
    tSize = round(scale[0] * size[0]), round(scale[1] * size[1])
    clean = pygame.Surface(tSize, SRCALPHA)
    pygame.transform.smoothscale(start, tSize, clean)
    return clean

# a very large cache is allocated to rotation because, in most cases, it is only
# expected that small textures are being rotated and only one at a time, increasing
# the chance of cache hits and reducing the cost of each cached element
#@lru_cache(maxsize=512)
#def load_and_scale_and_rotate(route: str, scale: tuple[float], rotation: Angle, offset: Vector = V(0, 0)) -> Render:
#    start = load_and_scale(route, scale, offset).texture
#    return Render(pygame.transform.rotate(start, -rotation.angle), offset)
# depreciated for superpong performance test

# mass loading not cached to reduce redundency
#def load_textures(routes: Sequence[str]) -> tuple[pygame.Surface]:
#    return tuple((load_texture(route) for route in routes))

#def load_and_scale_all(routes: str, scale: Vector) -> tuple[pygame.Surface]:
#    return tuple((load_and_scale(route, scale) for route in routes))

class Screen:
    done: bool = False
    elements: list[Element]
    surface: pygame.surface.Surface
    colour: pygame.Color
    flags: int = NOT_RESIZABLE
    _caption: str = "Unnamed Pyg Render"
    _size: tuple[int, int] = 800, 600
    keys: set[int]
    mkeys: set[int]
    selectedID: int
    selectable: list[Element]
    context: PygContext
    def __init__(self):
        self.context = None
        self.elements = []
        pygame.font.init()
        pygame.display.set_mode(self._size, self.flags)
        pygame.display.set_caption(self.caption)
        self.surface = pygame.display.get_surface()
        self.keys, self.mkeys = set(), set()
        self.caption = Screen._caption

    def new_context(self, context: PygContext):
        self.context = context
        self.handlers: dict[int, Callable] = {
            MMOTION: self._mouse_move,
            KDOWN: self._key_down,
            KUP: self._key_up,
            MBDOWN: self._mouse_down,
            MBUP: self._mouse_up,
            QUIT: self._quit,
            WINSHOW: self._window_shown,
            ACTIVATED: self._activated,
            FOCUS: self._focussed,
            TEXT_EDIT: lambda e: None,
            VIDEO: self._video,
            WINEXPOSED: self._exposed,
            TEXT_ENTER: self._typing,
            UNFOCUS: self._unfocussed,
            M_WHEEL: self._mouse_wheel,
            RESIZE: self._resize,
            32783: lambda e: None, # window enter
            32784: lambda e: None, # window leave
            32777: lambda e: None, # window moved
            32779: lambda e: None, # window size changed
            32769: lambda e: None, # video resize
            32787: lambda e: None, # window closed
            32780: lambda e: None, # window minimised
            32782: lambda e: None, # window restored
            32781: lambda e: None, # window maximised
            2304: lambda e: None, # capture frame
        }

    def add_element(self, element: Element):
        self.elements.append(element)

    def _mouse_move(self, event: pygame.event.Event): 
        self.context.mouse_move(event)

    def _window_shown(self, event: pygame.event.Event): 
        self.context.window_shown(event)

    def _activated(self, event: pygame.event.Event): 
        self.context.activated(event)

    def _focussed(self, event: pygame.event.Event): 
        self.context.focussed(event)

    def _video(self, event: pygame.event.Event): 
        self.context.video(event)

    def _exposed(self, event: pygame.event.Event): 
        self.context.exposed(event)

    def _typing(self, event: pygame.event.Event): 
        self.context.typing(event)

    def _unfocussed(self, event: pygame.event.Event): 
        self.context.unfocussed(event)

    def _mouse_wheel(self, event: pygame.event.Event): 
        self.context.mouse_wheel(event)

    def _resize(self, size: tuple[int, int]): 
        self.context.resize(size)

    def _post_init(self): 
        self.context.post_init()

    def _quit(self): 
        self.context.quit()

    def _update(self): 
        self.context.update()

    def _key_down(self, event: pygame.event.Event): 
        self.keys.add(event.key)
        self.context.key_down(event.key)
    
    def _key_up(self, event: pygame.event.Event): 
        self.keys.remove(event.key)
        self.context.key_up(event.key)

    def _mouse_down(self, event: pygame.event.Event): 
        self.mkeys.add(event.button)
        self.context.mouse_down(event.button, event.pos)

    def _mouse_up(self, event: pygame.event.Event): 
        self.mkeys.remove(event.button)
        self.context.mouse_up(event.button, event.pos)

    def resize(self, event: pygame.event.Event):
        self._size = self.surface.get_size()
        self.context.resize(self.size)
        self.changed = True

    def quit(self, event: pygame.event.Event):
        self.changed = True
        self.done = True
        self.context.quit()

    def render(self, fr: float):
        self.context.update()
        for element in self.elements:
            element.draw(self.surface)
        pygame.display.flip()

    def prepare_context(self):
        if not isinstance(self.context, PygContext):
            raise AttributeError(f"Pyg <{self.__class__.__qualname__}> {self} has context {self.context} {self.context.__class__.__qualname__}")
        self.last = time.time()
        self.changed = True
        self.clock = pygame.time.Clock()
        self.done = False
        self._post_init()
        self.context.resize(self.surface.get_size())
        self.context.starting()

    def run(self, fr: float):
        self.prepare_context()
        self.surface = pygame.display.get_surface()
        startTime = time.time()
        frames = 0
        while not self.done:
            for event in pygame.event.get():
                with suppress(KeyError):
                    self.handlers[event.type](event)
            self.render(fr)
            frames += 1
            if time.time() - startTime > 20:
                self.done = False
                # debug profile shutdown
        self.context.quit()
    
    @property
    def caption(self) -> str:
        return self._caption

    @caption.setter
    def caption(self, caption: str):
        self._caption = caption
        pygame.display.set_caption(caption)

    @property
    def selected(self) -> Element:
        return self.selectable[self.selectedID % len(self.selectable)]

    @selected.setter
    def selected(self, selected: Element):
        if isinstance(selected, Element):
            index = self.selectable.index(selected)
            if index != -1:
                self.selectedID = self.selectable.index(selected)

    @property
    def size(self) -> tuple[int, int]:
        return self.surface.get_size()

def main():
    Screen.size = 1600, 1200
    s = Screen()
    with PygContext(s):
        s.run(144, 30)

if __name__ == "__main__":
    main()

