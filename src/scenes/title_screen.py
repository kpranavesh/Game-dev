import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import draw_rounded_rect, draw_cute_face


class Particle:
    def __init__(self, w, h):
        self.reset(w, h, initial=True)

    def reset(self, w, h, initial=False):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h) if initial else -20
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(0.3, 0.9)
        self.size = random.uniform(4, 10)
        self.alpha = random.randint(120, 220)
        self.color_idx = random.choice([0, 1, 2])
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-1.5, 1.5)
        self.w = w
        self.h = h

    def update(self):
        self.x += self.vx + math.sin(pygame.time.get_ticks() * 0.001 + self.y * 0.05) * 0.3
        self.y += self.vy
        self.angle += self.spin
        if self.y > self.h + 20:
            self.reset(self.w, self.h)

    def draw(self, surface):
        colors = [SOFT_GREEN, AMBER, SOFT_PINK]
        col = colors[self.color_idx]
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        # Draw a small leaf/petal shape
        pts = [
            (self.size, 0),
            (self.size * 2, self.size),
            (self.size, self.size * 2),
            (0, self.size),
        ]
        pygame.draw.polygon(surf, (*col, self.alpha), pts)
        rot = pygame.transform.rotate(surf, self.angle)
        surface.blit(rot, (self.x - rot.get_width()//2, self.y - rot.get_height()//2))


class TitleScreen:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None
        self.particles = [Particle(screen_w, screen_h) for _ in range(45)]
        self.heart_scale = 1.0
        self.heart_dir = 1
        self.t = 0
        self.alpha_in = 0  # fade in

        # Fonts
        self.font_title = pygame.font.SysFont("Georgia", 62, bold=True)
        self.font_sub   = pygame.font.SysFont("Georgia", 26, italic=True)
        self.font_hint  = pygame.font.SysFont("Arial", 20)
        self.font_level = pygame.font.SysFont("Georgia", 22)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_3:
                self.next_scene = SCENE_LEVEL3
                return
            if event.key == pygame.K_5:
                self.next_scene = SCENE_LEVEL5
                return
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.next_scene = SCENE_LEVEL1

    def update(self, dt):
        self.t += dt
        for p in self.particles:
            p.update()
        # Pulse heart
        self.heart_scale += self.heart_dir * dt * 0.8
        if self.heart_scale > 1.18:
            self.heart_dir = -1
        if self.heart_scale < 0.88:
            self.heart_dir = 1
        # Fade in
        if self.alpha_in < 255:
            self.alpha_in = min(255, self.alpha_in + 4)

    def draw(self, surface):
        # Sky gradient (manual)
        for y in range(self.h):
            t = y / self.h
            r = int(SKY_BLUE[0] * (1 - t) + CREAM[0] * t)
            g = int(SKY_BLUE[1] * (1 - t) + CREAM[1] * t)
            b = int(SKY_BLUE[2] * (1 - t) + CREAM[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Particles
        for p in self.particles:
            p.draw(surface)

        # Rolling hills at bottom
        hill_pts = [(0, self.h)]
        for x in range(0, self.w + 20, 10):
            y_off = math.sin(x * 0.010 + self.t * 0.3) * 22 + math.sin(x * 0.007 - self.t * 0.15) * 15
            hill_pts.append((x, self.h - 95 + y_off))
        hill_pts.append((self.w, self.h))
        pygame.draw.polygon(surface, SOFT_GREEN, hill_pts)
        # Hill highlight
        hill_pts2 = []
        for x in range(0, self.w + 20, 10):
            y_off = math.sin(x * 0.010 + self.t * 0.3) * 22 + math.sin(x * 0.007 - self.t * 0.15) * 15
            hill_pts2.append((x, self.h - 95 + y_off - 8))
        for pt in reversed([(p[0], p[1] + 3) for p in hill_pts2]):
            pass
        pygame.draw.lines(surface, LEAF_GREEN, False, hill_pts2, 3)

        # Small clouds
        for i, (cx, cy_base, size) in enumerate([
            (150, 100, 55), (420, 70, 70), (700, 120, 48), (260, 155, 38)
        ]):
            cy = cy_base + math.sin(self.t * 0.25 + i) * 6
            for dx, dy, r in [(0, 0, size), (-size*0.6, size*0.2, size*0.65),
                               (size*0.6, size*0.2, size*0.65), (0, size*0.35, size*0.7)]:
                pygame.draw.circle(surface, WHITE, (int(cx + dx), int(cy + dy)), int(r))

        # Title card background
        card_rect = pygame.Rect(self.w//2 - 270, 140, 540, 300)
        draw_rounded_rect(surface, (*CARD_BG, 230), card_rect, radius=24, shadow=True, shadow_offset=6)
        # We need to draw with alpha so use a surface
        card_surf = pygame.Surface((540, 300), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (*CARD_BG, 220), (0, 0, 540, 300), border_radius=24)
        surface.blit(card_surf, (card_rect.x, card_rect.y))
        pygame.draw.rect(surface, AMBER, card_rect, width=2, border_radius=24)

        # Title text
        title_surf = self.font_title.render("Us: The Game", True, DARK_BROWN)
        surface.blit(title_surf, (self.w//2 - title_surf.get_width()//2, 175))

        # Heart
        hs = int(32 * self.heart_scale)
        heart_y = 255
        _draw_heart(surface, self.w//2, heart_y, hs, HEART_RED)

        # Subtitle
        sub_surf = self.font_sub.render("A love story in 10 levels  ♡", True, MID_BROWN)
        surface.blit(sub_surf, (self.w//2 - sub_surf.get_width()//2, 295))

        for_surf = self.font_sub.render("Made for Vandita · April 10, 2026", True, MID_BROWN)
        surface.blit(for_surf, (self.w//2 - for_surf.get_width()//2, 330))

        # Hint (blinking)
        if int(self.t * 2) % 2 == 0:
            hint = self.font_hint.render("Press any key to begin  |  Press 3 for Yarn Crisis  |  Press 5 for Beans Park", True, MID_BROWN)
            surface.blit(hint, (self.w//2 - hint.get_width()//2, 490))

        # Two cute characters at bottom sides
        draw_cute_face(surface, 140, self.h - 60, scale=0.75,
                       skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True)
        draw_cute_face(surface, self.w - 140, self.h - 60, scale=0.75,
                       skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True)

        # Level preview at bottom of card
        lvl_surf = self.font_level.render("Level 1: Swipe Right →", True, MID_BROWN)
        surface.blit(lvl_surf, (self.w//2 - lvl_surf.get_width()//2, 550))


def _draw_heart(surface, cx, cy, size, color):
    """Draw a simple heart shape."""
    pts = []
    for i in range(360):
        angle = math.radians(i)
        x = size * (16 * math.sin(angle) ** 3) / 16
        y = -size * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)) / 16
        pts.append((cx + x, cy + y))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)
