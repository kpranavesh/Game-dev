import math
import random
from dataclasses import dataclass

import pygame

from src.utils.constants import (
    SCREEN_W,
    SCREEN_H,
    CREAM,
    SKY_BLUE,
    SOFT_GREEN,
    LEAF_GREEN,
    AMBER,
    AMBER_DARK,
    CARD_BG,
    HEART_RED,
    DARK_BROWN,
    MID_BROWN,
    SCENE_LEVEL6,
)
from src.utils.draw_helpers import draw_border_collie, draw_rounded_rect


@dataclass
class Ball:
    x: float
    y: float
    collected: bool = False


@dataclass
class Puddle:
    x: float
    y: float
    w: int
    h: int


class Level5BeansPark:
    """
    Level 5 – Beans at the Park

    You control Beans zooming around a twilight park, collecting three tennis balls
    before the sun fully sets. It should feel like real border-collie zoomies:
    quick starts, wide turns, happy tail, tongue out always.
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        # Beans physics
        self.bx = self.w // 2
        self.by = int(self.h * 0.65)
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 260.0
        self.accel = 520.0
        self.friction = 0.78

        # World elements
        self.balls: list[Ball] = [
            Ball(self.w * 0.22, self.h * 0.58),
            Ball(self.w * 0.78, self.h * 0.60),
            Ball(self.w * 0.50, self.h * 0.42),
        ]
        self.puddles: list[Puddle] = [
            Puddle(int(self.w * 0.30), int(self.h * 0.70), 90, 32),
            Puddle(int(self.w * 0.64), int(self.h * 0.74), 110, 34),
        ]

        self.collected = 0
        self.timer = 0.0
        self.time_limit = 55.0  # generous; this is a cozy level
        self.slow_timer = 0.0

        self.hearts: list[tuple[float, float, float]] = []  # (x, y, life)

        # Fonts
        self.f_hdr = pygame.font.SysFont("Georgia", 22, bold=True)
        self.f_sub = pygame.font.SysFont("Georgia", 18, italic=True)
        self.f_ui = pygame.font.SysFont("Arial", 18)
        self.f_big = pygame.font.SysFont("Georgia", 40, bold=True)

        self.clear_timer = 0.0
        self.cleared = False

    # ------------------------------------------------------------------ events
    def handle_event(self, event):
        # After clear, any key/mouse moves on to next scene
        if self.cleared and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.next_scene = SCENE_LEVEL6

    # ----------------------------------------------------------------- helpers
    def _spawn_heart_burst(self, x: float, y: float):
        for _ in range(18):
            # (x, y, life)
            self.hearts.append([x, y, 1.0])

    # ------------------------------------------------------------------- update
    def update(self, dt: float):
        self.timer += dt

        keys = pygame.key.get_pressed()
        ax = ay = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= self.accel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += self.accel
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= self.accel
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += self.accel

        if self.slow_timer > 0:
            self.slow_timer -= dt
            ax *= 0.35
            ay *= 0.35

        # Integrate velocity
        self.vx += ax * dt
        self.vy += ay * dt

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        # Apply friction
        self.vx *= self.friction ** (dt * 60)
        self.vy *= self.friction ** (dt * 60)

        self.bx += self.vx * dt
        self.by += self.vy * dt

        # Soft bounds inside the park
        margin = 70
        self.bx = max(margin, min(self.w - margin, self.bx))
        ground_y_min = int(self.h * 0.40)
        self.by = max(ground_y_min, min(self.h - margin, self.by))

        # Collect balls
        for ball in self.balls:
            if ball.collected:
                continue
            dx = self.bx - ball.x
            dy = self.by - ball.y
            if dx * dx + dy * dy < (48 * 48):
                ball.collected = True
                self.collected += 1
                self._spawn_heart_burst(ball.x, ball.y - 18)

        # Puddles slow Beans down a bit
        for puddle in self.puddles:
            r = pygame.Rect(puddle.x, puddle.y, puddle.w, puddle.h)
            if r.collidepoint(int(self.bx), int(self.by) + 20):
                self.vx *= 0.45
                self.vy *= 0.45
                self.slow_timer = 0.8

        # Hearts
        new_hearts: list[tuple[float, float, float]] = []
        for x, y, life in self.hearts:
            life -= dt * 0.9
            if life <= 0:
                continue
            y -= dt * 30
            new_hearts.append((x, y, life))
        self.hearts = new_hearts

        # Win condition
        if not self.cleared and self.collected >= len(self.balls):
            self.cleared = True
            self.clear_timer = 0.0

        if self.cleared:
            self.clear_timer += dt
            # Auto-advance after a few seconds if they don't press anything
            if self.clear_timer > 6.0 and self.next_scene is None:
                self.next_scene = SCENE_LEVEL6

    # --------------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface):
        # Background gradient (late afternoon sky)
        for y in range(self.h):
            t = y / self.h
            r = int(SKY_BLUE[0] * (1 - t) + CREAM[0] * t)
            g = int(SKY_BLUE[1] * (1 - t) + CREAM[1] * t)
            b = int(SKY_BLUE[2] * (1 - t) + CREAM[2] * t)
            surface.fill((r, g, b), pygame.Rect(0, y, self.w, 1))

        # Rolling park ground
        ground_pts = [(0, self.h)]
        t = pygame.time.get_ticks() * 0.0004
        base_y = int(self.h * 0.68)
        for x in range(0, self.w + 30, 12):
            y_off = math.sin(x * 0.010 + t) * 12 + math.sin(x * 0.023 - t * 1.5) * 8
            ground_pts.append((x, base_y + y_off))
        ground_pts.append((self.w, self.h))
        pygame.draw.polygon(surface, SOFT_GREEN, ground_pts)

        # Foreground grass edge
        for x in range(0, self.w + 16, 16):
            y = base_y - 10 + int(math.sin(t * 2 + x * 0.15) * 4)
            pygame.draw.line(surface, LEAF_GREEN, (x, y), (x, y + 16), 3)

        # Fence posts in the back
        fence_y = base_y - 36
        for x in range(-20, self.w + 20, 40):
            pygame.draw.rect(surface, AMBER_DARK, (x, fence_y, 10, 54), border_radius=3)
        pygame.draw.line(surface, AMBER, (0, fence_y + 8), (self.w, fence_y + 8), 4)
        pygame.draw.line(surface, AMBER, (0, fence_y + 28), (self.w, fence_y + 28), 4)

        # Header card
        card_rect = pygame.Rect(self.w // 2 - 260, 22, 520, 78)
        draw_rounded_rect(surface, (*CARD_BG, 235), card_rect, radius=20, shadow=True, shadow_offset=5)
        hdr = self.f_hdr.render("Level 5  ·  Beans at the Park", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2, 30))

        sub = self.f_sub.render("Zoom around the park and fetch every ball before it gets too dark.", True, MID_BROWN)
        surface.blit(sub, (self.w // 2 - sub.get_width() // 2, 56))

        # Timer + score
        remaining = max(0, int(self.time_limit - self.timer))
        ui_text = self.f_ui.render(f"Balls fetched: {self.collected}/{len(self.balls)}   Time: {remaining}s", True, DARK_BROWN)
        surface.blit(ui_text, (24, 20))

        # Puddles
        for p in self.puddles:
            ellipse_rect = pygame.Rect(p.x, p.y, p.w, p.h)
            pygame.draw.ellipse(surface, (120, 170, 210), ellipse_rect)
            pygame.draw.ellipse(surface, (90, 135, 180), ellipse_rect, 2)

        # Balls
        for ball in self.balls:
            if ball.collected:
                continue
            x = int(ball.x)
            y = int(ball.y)
            # Tennis ball
            pygame.draw.circle(surface, (205, 240, 120), (x, y), 12)
            pygame.draw.circle(surface, (170, 210, 95), (x, y), 12, 2)
            pygame.draw.arc(surface, (230, 255, 210), pygame.Rect(x - 14, y - 12, 20, 24), -0.5, 1.3, 2)

        # Beans – always in full zoomies pose
        bounce_y = int(math.sin(pygame.time.get_ticks() * 0.006) * 6)
        draw_border_collie(
            surface,
            int(self.bx),
            int(self.by) + bounce_y,
            scale=1.0,
            happy=True,
            tongue=True,
            pose="free",
        )

        # Hearts from ball pickups
        for x, y, life in self.hearts:
            alpha = int(life * 230)
            size = int(12 * life + 6)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pts = []
            for i in range(360):
                a = math.radians(i)
                hx = size * (16 * math.sin(a) ** 3) / 16
                hy = -size * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16
                pts.append((size + hx, size + hy))
            if len(pts) >= 3:
                pygame.draw.polygon(surf, (*HEART_RED, alpha), pts)
            surface.blit(surf, (x - size, y - size))

        # Hints
        hint = self.f_ui.render("Move Beans with WASD or arrow keys. Avoid puddles, fetch all the balls.", True, DARK_BROWN)
        surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))

        # Clear overlay
        if self.cleared:
            alpha = min(200, int(self.clear_timer * 90) + 40)
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha // 2))
            surface.blit(overlay, (0, 0))

            msg = self.f_big.render("Good girl, Beans! 💖", True, CREAM)
            surface.blit(msg, (self.w // 2 - msg.get_width() // 2, self.h // 2 - 50))

            sub2 = self.f_sub.render("Walk a bit further into the park…", True, CREAM)
            surface.blit(sub2, (self.w // 2 - sub2.get_width() // 2, self.h // 2 + 4))

            if int(self.clear_timer * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key to continue", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h // 2 + 40))

