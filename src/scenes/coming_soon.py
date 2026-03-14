import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import draw_rounded_rect, draw_cute_face


def _draw_heart(surface, cx, cy, size, color):
    pts = []
    for i in range(360):
        angle = math.radians(i)
        x = size * (16 * math.sin(angle) ** 3) / 16
        y = -size * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)) / 16
        pts.append((cx + x, cy + y))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)


UPCOMING = [
    ("8", "Plot Twist", "She had a ring too"),
    ("9", "Home",       "The ending you deserve"),
]


class ComingSoonScreen:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None
        self.t = 0

        self.font_big   = pygame.font.SysFont("Georgia", 44, bold=True)
        self.font_title = pygame.font.SysFont("Georgia", 26, bold=True)
        self.font_sub   = pygame.font.SysFont("Georgia", 18, italic=True)
        self.font_hint  = pygame.font.SysFont("Arial", 20)
        self.font_lvl   = pygame.font.SysFont("Georgia", 17)
        self.font_num   = pygame.font.SysFont("Georgia", 14, bold=True)

    def handle_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.next_scene = SCENE_TITLE

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        # Background gradient
        for y in range(self.h):
            t = y / self.h
            r = int(CREAM[0] * (1 - t) + SKY_BLUE[0] * t)
            g = int(CREAM[1] * (1 - t) + SKY_BLUE[1] * t)
            b = int(CREAM[2] * (1 - t) + SKY_BLUE[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Completed-levels banner
        banner = self.font_big.render("✓ Levels 1–6 Complete! 🎉", True, DARK_BROWN)
        surface.blit(banner, (self.w//2 - banner.get_width()//2, 38))
        pygame.draw.line(surface, AMBER, (80, 92), (self.w - 80, 92), 2)

        # Coming soon label
        cs = self.font_title.render("Levels still baking...  🍞", True, MID_BROWN)
        surface.blit(cs, (self.w//2 - cs.get_width()//2, 108))

        # Level grid
        cols = 3
        pad = 18
        card_w = 240
        card_h = 68
        total_w = cols * card_w + (cols - 1) * pad
        start_x = self.w // 2 - total_w // 2
        start_y = 150

        for i, (num, title, tagline) in enumerate(UPCOMING):
            col = i % cols
            row = i // cols
            cx = start_x + col * (card_w + pad)
            cy = start_y + row * (card_h + pad)

            # Card
            rect = pygame.Rect(cx, cy, card_w, card_h)
            # Subtle float animation
            float_y = cy + math.sin(self.t * 1.2 + i * 0.7) * 3
            rect.y = int(float_y)

            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (*CARD_BG, 200), (0, 0, card_w, card_h), border_radius=14)
            pygame.draw.rect(card_surf, (*AMBER, 180), (0, 0, card_w, card_h), width=1, border_radius=14)
            surface.blit(card_surf, (rect.x, rect.y))

            # Lock icon + level number
            lock = self.font_num.render(f"Lv.{num} 🔒", True, MID_BROWN)
            surface.blit(lock, (rect.x + 10, rect.y + 8))

            # Title
            title_surf = self.font_lvl.render(title, True, DARK_BROWN)
            surface.blit(title_surf, (rect.x + 10, rect.y + 26))

            # Tagline
            tag_surf = self.font_sub.render(tagline, True, MID_BROWN)
            if tag_surf.get_width() > card_w - 20:
                tag_surf = pygame.transform.scale(tag_surf, (card_w - 20, tag_surf.get_height()))
            surface.blit(tag_surf, (rect.x + 10, rect.y + 46))

        # Pulsing heart
        hs = int(20 + math.sin(self.t * 2.5) * 5)
        _draw_heart(surface, self.w // 2, self.h - 90, hs, HEART_RED)

        note = self.font_sub.render("More levels coming soon — this is just the beginning  ♡", True, MID_BROWN)
        surface.blit(note, (self.w//2 - note.get_width()//2, self.h - 60))

        if int(self.t * 2) % 2 == 0:
            hint = self.font_hint.render("Press any key to return to title", True, MID_BROWN)
            surface.blit(hint, (self.w//2 - hint.get_width()//2, self.h - 32))
