"""
Finale — The ending screen.
Mirrors the title screen visually but with Krishna + Vandita + Beans together.
Personal message. Happy tears. The whole point.
"""
import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import (
    draw_rounded_rect,
    draw_cute_face,
    draw_border_collie,
)


class Particle:
    def __init__(self, w, h):
        self.reset(w, h, initial=True)

    def reset(self, w, h, initial=False):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h) if initial else -20
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(0.2, 0.7)
        self.size = random.uniform(4, 9)
        self.alpha = random.randint(130, 220)
        self.color_idx = random.choice([0, 1, 2])
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-1.2, 1.2)
        self.w = w
        self.h = h

    def update(self):
        self.x += self.vx + math.sin(pygame.time.get_ticks() * 0.001 + self.y * 0.05) * 0.2
        self.y += self.vy
        self.angle += self.spin
        if self.y > self.h + 20:
            self.reset(self.w, self.h)

    def draw(self, surface):
        from src.utils.constants import SOFT_GREEN, AMBER, SOFT_PINK
        colors = [SOFT_GREEN, AMBER, SOFT_PINK]
        col = colors[self.color_idx]
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pts = [
            (self.size, 0),
            (self.size * 2, self.size),
            (self.size, self.size * 2),
            (0, self.size),
        ]
        pygame.draw.polygon(surf, (*col, self.alpha), pts)
        rot = pygame.transform.rotate(surf, self.angle)
        surface.blit(rot, (self.x - rot.get_width() // 2, self.y - rot.get_height() // 2))


def _draw_heart(surface, cx, cy, size, color):
    pts = []
    for i in range(360):
        angle = math.radians(i)
        x = size * (16 * math.sin(angle) ** 3) / 16
        y = -size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)) / 16
        pts.append((cx + x, cy + y))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)


class LevelFinale:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None
        self.t = 0.0
        self.fade_alpha = 0

        self.particles = [Particle(screen_w, screen_h) for _ in range(40)]

        self.heart_scale = 1.0
        self.heart_dir = 1

        # Two phases: message, then credits
        self.phase = "message"  # "message" -> "credits"
        self.credits_timer = 0.0

        # Fonts
        self.f_title = pygame.font.SysFont("Georgia", 48, bold=True)
        self.f_message = pygame.font.SysFont("Georgia", 22, italic=True)
        self.f_name = pygame.font.SysFont("Georgia", 28, bold=True)
        self.f_small = pygame.font.SysFont("Georgia", 18, italic=True)
        self.f_hint = pygame.font.SysFont("Arial", 18)
        self.f_credits = pygame.font.SysFont("Georgia", 20, italic=True)

    def handle_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if self.phase == "message" and self.t > 2.0:
                self.phase = "credits"
                self.credits_timer = 0.0
            elif self.phase == "credits" and self.credits_timer > 1.5:
                self.next_scene = SCENE_TITLE

    def update(self, dt):
        self.t += dt
        if self.t < 0.1 and self.phase == "message":
            from src.utils.sounds import get_sfx
            get_sfx().celebrate.play()
        self.fade_alpha = min(255, int(self.t * 100))

        for p in self.particles:
            p.update()

        self.heart_scale += self.heart_dir * dt * 0.6
        if self.heart_scale > 1.15:
            self.heart_dir = -1
        if self.heart_scale < 0.9:
            self.heart_dir = 1

        if self.phase == "credits":
            self.credits_timer += dt

    def draw(self, surface):
        # Warm gradient background (same as title but warmer)
        for y in range(self.h):
            t = y / self.h
            r = int(SKY_BLUE[0] * (1 - t) + CREAM[0] * t)
            g = int(SKY_BLUE[1] * (1 - t) + CREAM[1] * t)
            b = int(SKY_BLUE[2] * (1 - t) + CREAM[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Particles
        for p in self.particles:
            p.draw(surface)

        # Rolling hills (mirroring title screen)
        hill_pts = [(0, self.h)]
        for x in range(0, self.w + 20, 10):
            y_off = math.sin(x * 0.010 + self.t * 0.3) * 22 + math.sin(x * 0.007 - self.t * 0.15) * 15
            hill_pts.append((x, self.h - 95 + y_off))
        hill_pts.append((self.w, self.h))
        pygame.draw.polygon(surface, SOFT_GREEN, hill_pts)
        hill_pts2 = []
        for x in range(0, self.w + 20, 10):
            y_off = math.sin(x * 0.010 + self.t * 0.3) * 22 + math.sin(x * 0.007 - self.t * 0.15) * 15
            hill_pts2.append((x, self.h - 95 + y_off - 8))
        pygame.draw.lines(surface, LEAF_GREEN, False, hill_pts2, 3)

        # Clouds
        for i, (cx, cy_base, size) in enumerate([
            (150, 100, 55), (420, 70, 70), (700, 120, 48), (260, 155, 38)
        ]):
            cy = cy_base + math.sin(self.t * 0.25 + i) * 6
            for dx, dy, r in [(0, 0, size), (-size * 0.6, size * 0.2, size * 0.65),
                               (size * 0.6, size * 0.2, size * 0.65), (0, size * 0.35, size * 0.7)]:
                pygame.draw.circle(surface, WHITE, (int(cx + dx), int(cy + dy)), int(r))

        if self.phase == "message":
            self._draw_message(surface)
        elif self.phase == "credits":
            self._draw_credits(surface)

    def _draw_message(self, surface):
        alpha = min(255, self.fade_alpha)

        # Card background
        card_rect = pygame.Rect(self.w // 2 - 280, 130, 560, 320)
        draw_rounded_rect(surface, (*CARD_BG, min(230, alpha)), card_rect, radius=24, shadow=True, shadow_offset=6)

        if alpha < 40:
            return

        # Pulsing heart at top of card
        hs = int(24 * self.heart_scale)
        _draw_heart(surface, self.w // 2, 165, hs, HEART_RED)

        lines = [
            "Every level of this game is a real moment.",
            "Every moment with you is my favorite level.",
            "",
            "Me, Beans, and you. That's the whole game.",
        ]

        y_start = 200
        for i, line in enumerate(lines):
            if not line:
                continue
            s = self.f_message.render(line, True, DARK_BROWN)
            s.set_alpha(alpha)
            surface.blit(s, (self.w // 2 - s.get_width() // 2, y_start + i * 34))

        # "Happy 29th Birthday, Vandita"
        bday = self.f_name.render("Happy 29th Birthday, Nunu!", True, DARK_BROWN)
        bday.set_alpha(alpha)
        surface.blit(bday, (self.w // 2 - bday.get_width() // 2, 345))

        # Heart below name
        _draw_heart(surface, self.w // 2, 395, int(18 * self.heart_scale), HEART_RED)

        # Three characters at the bottom: Krishna, Beans, Vandita
        char_y = self.h - 65
        # Krishna (left)
        draw_cute_face(surface, self.w // 2 - 80, char_y, scale=0.8,
                       skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True)
        # Beans (center, sitting between them)
        draw_border_collie(surface, self.w // 2, char_y + 5, scale=0.6,
                          happy=True, tongue=True, pose="sit")
        # Vandita (right)
        draw_cute_face(surface, self.w // 2 + 80, char_y, scale=0.8,
                       skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True)

        # Continue hint
        if self.t > 2.0 and int(self.t * 2) % 2 == 0:
            hint = self.f_hint.render("Press any key to continue", True, MID_BROWN)
            surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 130))

    def _draw_credits(self, surface):
        alpha = min(255, int(self.credits_timer * 150))

        # Semi-transparent overlay
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((*CREAM, min(180, alpha)))
        surface.blit(overlay, (0, 0))

        if alpha < 60:
            return

        # Credits text
        lines = [
            ("Made with love, bugs, and a copious amount of flour", self.f_credits),
            ("", None),
            ("Starring:", self.f_small),
            ("Vandita  ·  Krishna  ·  Beans", self.f_name),
            ("", None),
            ("Written, coded, and debugged by Krishna", self.f_small),
        ]

        y = self.h // 2 - 120
        for text, font in lines:
            if not text:
                y += 16
                continue
            s = font.render(text, True, DARK_BROWN)
            s.set_alpha(alpha)
            surface.blit(s, (self.w // 2 - s.get_width() // 2, y))
            y += s.get_height() + 10

        # Final heart
        if self.credits_timer > 1.0:
            _draw_heart(surface, self.w // 2, y + 20, int(20 * self.heart_scale), HEART_RED)

        if self.credits_timer > 1.5 and int(self.credits_timer * 2) % 2 == 0:
            hint = self.f_hint.render("Press any key to return to title", True, MID_BROWN)
            surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))
