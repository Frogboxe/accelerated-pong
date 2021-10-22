
from __future__ import annotations

import time
from random import randint

import pongaccelerated as pong
from element import Element
from pyg import (LOG_ROUTES, TEXTURE_ROUTES, Screen, load_and_scale,
                 load_texture)
from pygcontext import PygContext


class Display(Screen):
    _size = (pong.PAGEX, pong.PAGEY)

class Ball(Element):
    def __init__(self, screen, i: int):
        super().__init__(screen, (0, 0))
        self.texture = load_and_scale(f"{str(randint(0, 5))}.png", (pong.BALLX, pong.BALLY))
        self.i = i

    @property
    def pos(self) -> tuple[int, int]:
        rec = pong.balls[self.i]
        return rec.x, rec.y

    @pos.setter
    def pos(self, pos: tuple[int]):
        return

class Paddle(Element):
    def __init__(self, screen, pos: tuple[int, int]):
        super().__init__(screen, pos)
        self.texture = load_and_scale(f"{str(randint(0, 4))}.png", (pong.PADDLEX, pong.PADDLEY))

class BlackBackground(Element):
    def __init__(self, screen):
        super().__init__(screen, (0, 0))
        print(load_and_scale("background.png", (pong.PAGEX, pong.PAGEY)))
        self.texture = load_and_scale("background.png", (pong.PAGEX, pong.PAGEY))
        self.i = 1


INPUT_SMOOTHING = 4
X_SCALE = 100
Y_SCALE = 300

class PongGameContext(PygContext):

    BallType: type = Ball
    last: float
    ballCount: int = 800
    
    background: BlackBackground
    balls: list[Ball]
    paddles: list[Paddle]
    dt: float = 0

    def start(self):
        super().start()
        self.exitCode = 0
        self.last = time.time()
        pong.initialise_balls(pong.balls)
        pong.initialise_paddles(pong.paddles)
        self.background = BlackBackground(self.screen)
        self.balls = [Ball(self.screen, i) for i in range(pong.ballCount)]
        self.paddles = [Paddle(self.screen, (rec.x, rec.y)) for rec in pong.paddles]

    def game_pong(self):
        self.screen.caption = "Pong"

    def handle_input(self, dt: float):
        keys = self.screen.keys
        if 119 in keys: # w
            dya = -Y_SCALE
        elif 115 in keys: # s
            dya = Y_SCALE
        else:
            dya = 0
        if 97 in keys:
            dxa = -X_SCALE
        elif 100 in keys:
            dxa = X_SCALE
        else:
            dxa = 0
        if 1073741906 in keys: # up arrow
            dyb = -Y_SCALE
        elif 1073741905 in keys: # down arrow
            dyb = Y_SCALE
        else:
            dyb = 0
        if 1073741904 in keys: # left arrow
            dxb = -X_SCALE
        elif 1073741903 in keys: # right arrow
            dxb = X_SCALE
        else:
            dxb = 0
        pong.paddleInput[0].x = dxa
        pong.paddleInput[0].y = dya
        pong.paddleInput[1].x = dxb
        pong.paddleInput[1].y = dyb
        pong.move_paddles(pong.paddles, pong.paddleInput, dt)


    def key_down(self, k: int):
        if 32 in self.screen.keys:
            self.screen.done = True
            self.exitCode = 1

    def handle_tick(self) -> float:
        ctime = time.time()
        dt = ctime - self.last
        self.last = ctime
        pong.tick(pong.balls, pong.paddles, pong.paddleInput, dt)
        return dt

    def handle_elements(self):
        for i, paddle in enumerate(pong.paddles):
            self.paddles[i].pos = paddle.x, paddle.y

    def update(self):
        self.handle_input(self.dt)
        self.dt = self.handle_tick()
        self.handle_elements()

def main(d: bool = True):
    if d:
        TEXTURE_ROUTES, LOG_ROUTES = "\\assets", "\\logs"
    screen = Display()
    with PongGameContext(screen):
        screen.run(144)

if __name__ == "__main__":
    main(False)


