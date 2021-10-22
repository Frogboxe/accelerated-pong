
from __future__ import annotations

from random import randint, random, randrange

import numpy as np
from numba import njit, prange


class FakeBall: x: float; y: float; dx: float; dy: float
class FakePaddle: x: float; y: float

BALL = np.dtype([('x', np.float64),
                 ('y', np.float64),
                 ('dx', np.float64),
                 ('dy', np.float64)])

PADDLE = np.dtype([('x', np.float64), ('y', np.float64)])

BALLX = 5
BALLY = 5
PADDLEX = 60
PADDLEY = 600

TX, TY = 60, 60
TDX, TDY = 0.2, 0.2

PAGEX = 1500
PAGEY = 1000

BALLDX, BALLDY = 50, 50
BALLRX, BALLRY = 40, 40
BALLRXH, BALLRYH = BALLRX / 2, BALLRY / 2

SCORE_ZONE_WIDTH = 20

ballCount, paddleCount = 4_000, 2

@njit(parallel=True)
def initialise_balls(balls: list[FakeBall]):
    for i in prange(ballCount):
        x, y = PAGEX / 2, PAGEY / 2
        dx, dy = BALLDX + (BALLRX * random() + BALLRXH), BALLDY + (BALLRXH + random() * BALLRY)
        balls[i].x = x
        balls[i].y = y
        balls[i].dx = dx * randrange(-1, 3, 2)
        balls[i].dy = dy * randrange(-1, 3, 2)

@njit()
def initialise_paddles(paddles: list[FakePaddle]):
    paddles[0].x = PAGEX / 6
    paddles[1].x = 5 * PAGEX / 6
    paddles[0].y = PAGEY / 2
    paddles[1].y = PAGEY / 2

@njit()
def move_paddles(paddles: list[FakePaddle], paddleInput: list[FakePaddle], dt: np.float64):
    p1i, p2i = paddleInput[0], paddleInput[1]
    paddles[0].x += p1i.x * dt
    paddles[0].y += p1i.y * dt
    paddles[1].x += p2i.x * dt
    paddles[1].y += p2i.y * dt

@njit(parallel=False, nogil=True, nopython=True, fastmath=True)
def tick(balls: list[FakeBall], paddles: list[FakePaddle], paddleInput: list[FakePaddle], dt: np.float64):
    # all ball -> paddle / wall collision
    #xr, yr, dxr, dyr = balls.view(np.recarray), balls.view
    for i in prange(ballCount):
        # setup
        record = balls[i]
        x, y, dx, dy = record.x, record.y, record.dx, record.dy
        dx = dx + (-TDX * (dx > TX)) + (TDX * (dx < -TX))
        dy = dy + (-TDY * (dy > TY)) + (TDY * (dy < -TY))
        cbx, cby = x + BALLX, y + BALLY
        cx, cy = x + dx * dt, y + dy * dt
        # paddle collision
        for j in prange(paddleCount):
            precord = paddles[j]
            px, py = precord.x, precord.y
            wx, wy = px + PADDLEX, py + PADDLEY
            lc = px <= x <= wx
            rc = px <= cbx <= wx
            tc = py <= y <= wy
            bc = py <= cby <= wy
            tlc = lc & tc
            trc = rc & tc
            blc = lc & bc
            brc = rc & bc
            if tlc & trc:
                dy = abs(dy)
            elif blc & brc:
                dy = -abs(dy)
            elif tlc & blc:
                dx = abs(dx)
            elif trc & brc:
                dx = -abs(dx)
            elif tlc:
                dx, dy = abs(dx), abs(dy)
            elif trc:
                dx, dy = -abs(dx), abs(dy)
            elif blc:
                dx, dy = abs(dx), -abs(dy)
            elif brc:
                dx, dy = -abs(dx), -abs(dy)
            if tlc | trc | blc | brc:
                r = paddleInput[j]
                dx, dy = dx + 24 * r.x * dt, dy + 24 * r.y * dt
        # wall collision
        if cbx > PAGEX:
            dx = -abs(dx)
        elif cx < 0:
            dx = abs(dx)
        if cby > PAGEY:
            dy = -abs(dy)
        elif cy < 0:
            dy = abs(dy)
        # collapse
        balls[i].x, balls[i].y, balls[i].dx, balls[i].dy = cx, cy, dx, dy

    return balls

ballBuffer = np.zeros(ballCount * len(BALL)).reshape((ballCount, len(BALL))).astype(np.float64)
balls = np.recarray(ballCount, dtype=BALL, buf=ballBuffer)

paddleBuffer = np.zeros(paddleCount * len(PADDLE)).reshape((paddleCount, len(PADDLE))).astype(np.float64)
paddles = np.recarray(paddleCount, dtype=PADDLE, buf=paddleBuffer)

paddleInputBuffer = np.zeros(paddleCount * len(PADDLE)).reshape((paddleCount, len(PADDLE))).astype(np.float64)
paddleInput = np.recarray(paddleCount, dtype=PADDLE, buf=paddleInputBuffer)

