"""
Level 7: The Charles River
===========================
Vandita proposes to Krishna on kayaks on the Charles River.
She corkscrews a letter into a bottle and floats it across.
Krishna catches it. The message unfolds line by line.
"""
import math
import random

import pygame

from src.utils.constants import (
    CREAM,
    SKY_BLUE,
    SOFT_GREEN,
    SOFT_PINK,
    AMBER,
    AMBER_DARK,
    CARD_BG,
    DARK_BROWN,
    MID_BROWN,
    HEART_RED,
    WHITE,
    GOLD,
    SCENE_LEVEL2,
)
from src.utils.draw_helpers import draw_cute_face, draw_rounded_rect


def _draw_heart(surface, cx, cy, size, color):
    pts = []
    for i in range(360):
        a = math.radians(i)
        x = size * (16 * math.sin(a) ** 3) / 16
        y = -size * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16
        pts.append((cx + x, cy + y))
    if len(pts) >= 3:
        if len(color) == 4:
            tmp = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            pygame.draw.polygon(tmp, color, pts)
            surface.blit(tmp, (0, 0))
        else:
            pygame.draw.polygon(surface, color, pts)


class HeartParticle:
    def __init__(self, cx, cy):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.2, 3.5)
        self.x = cx + random.uniform(-15, 15)
        self.y = cy + random.uniform(-10, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2.0
        self.size = random.uniform(6, 16)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.02)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.06
        self.life -= self.decay
        self.size *= 0.988

    @property
    def alive(self):
        return self.life > 0 and self.size > 1


# The message, line by line
MESSAGE_LINES = [
    "You are the best person I have ever had",
    "the pleasure of giving myself to",
    "and surrounding myself with.",
    "",
    "I am the best version of me",
    "because of you and with you",
    "and that means everything to me.",
    "",
    "You are my sun, moon, and stars.",
    "You deserve nothing but the absolute best.",
    "",
    "You are a rock and an absolute FORCE to have.",
    "Definitely increasing the avg and median IQs",
    "of every room you walk into.",
    "Our house is no exception.",
    "Me, Beans, and you.",
    "",
    "Heheh excited for whatever is to come for us",
    "because it'll be with you, my Queen.",
    "",
    "Happiest friggin birthday.",
    "Love you.",
]


class Level7Kayak:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None
        self.t = 0.0

        # River line
        self.river_y = int(self.h * 0.55)

        # Phases: intro -> bottle_floating -> catch -> reading -> done
        self.phase = "intro"
        self.phase_timer = 0.0

        # Vandita's kayak (left side)
        self.v_kayak_x = self.w * 0.22
        self.v_kayak_y = self.river_y + 20

        # Krishna's kayak (right side)
        self.k_kayak_x = self.w * 0.78
        self.k_kayak_y = self.river_y + 30

        # Bottle
        self.bottle_x = self.v_kayak_x + 30
        self.bottle_y = self.v_kayak_y - 10
        self.bottle_target_x = self.k_kayak_x - 40
        self.bottle_bobbing = True

        # Message reading
        self.lines_revealed = 0
        self.line_timer = 0.0
        self.scroll_offset = 0.0

        # Hearts
        self.hearts: list[HeartParticle] = []

        # Water ripples
        self.ripples: list[dict] = []

        # Fonts
        self.f_hdr = pygame.font.SysFont("Georgia", 24, bold=True)
        self.f_sub = pygame.font.SysFont("Georgia", 18, italic=True)
        self.f_ui = pygame.font.SysFont("Arial", 18)
        self.f_big = pygame.font.SysFont("Georgia", 36, bold=True)
        self.f_mid = pygame.font.SysFont("Georgia", 22, bold=True)
        self.f_letter = pygame.font.SysFont("Georgia", 17, italic=True)
        self.f_letter_bold = pygame.font.SysFont("Georgia", 18, bold=True)
        self.f_small = pygame.font.SysFont("Georgia", 15, italic=True)

    def handle_event(self, event):
        if event.type not in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            return

        if self.phase == "intro" and self.phase_timer > 2.0:
            self.phase = "bottle_floating"
            self.phase_timer = 0.0
            self._add_ripple(self.bottle_x, self.bottle_y + 10)
            from src.utils.sounds import get_sfx
            get_sfx().splash.play()

        elif self.phase == "catch" and self.phase_timer > 1.0:
            self.phase = "reading"
            self.phase_timer = 0.0
            self.lines_revealed = 0
            self.line_timer = 0.0

        elif self.phase == "reading":
            from src.utils.sounds import get_sfx
            get_sfx().heartbeat.play()
            # Reveal next chunk of lines (3-4 at a time, or skip to end)
            target = min(len(MESSAGE_LINES), self.lines_revealed + 4)
            # Skip blank lines
            while target < len(MESSAGE_LINES) and MESSAGE_LINES[target - 1] == "":
                target += 1
            self.lines_revealed = min(len(MESSAGE_LINES), target)
            if self.lines_revealed >= len(MESSAGE_LINES):
                self.phase = "done"
                self.phase_timer = 0.0
                self._spawn_hearts(self.w // 2, self.h // 2, 40)
                from src.utils.sounds import get_sfx
                get_sfx().celebrate.play()

        elif self.phase == "done" and self.phase_timer > 1.5:
            self.next_scene = SCENE_LEVEL2

    def _spawn_hearts(self, cx, cy, count):
        for _ in range(count):
            self.hearts.append(HeartParticle(cx, cy))

    def _add_ripple(self, x, y):
        self.ripples.append({"x": x, "y": y, "r": 3, "alpha": 200})

    def update(self, dt):
        self.t += dt
        self.phase_timer += dt

        # Hearts
        for h in self.hearts:
            h.update()
        self.hearts = [h for h in self.hearts if h.alive]

        # Ripples
        for r in self.ripples:
            r["r"] += dt * 25
            r["alpha"] -= dt * 80
        self.ripples = [r for r in self.ripples if r["alpha"] > 0]

        if self.phase == "bottle_floating":
            # Bottle drifts from Vandita to Krishna
            progress = min(1.0, self.phase_timer / 3.5)
            eased = 1 - (1 - progress) ** 2  # ease out
            self.bottle_x = self.v_kayak_x + 30 + (self.bottle_target_x - self.v_kayak_x - 30) * eased
            self.bottle_y = self.river_y + 10 + math.sin(self.t * 3) * 4

            # Add ripples as bottle moves
            if random.random() < dt * 3:
                self._add_ripple(self.bottle_x, self.bottle_y + 8)

            if progress >= 1.0:
                self.phase = "catch"
                self.phase_timer = 0.0
                self._spawn_hearts(self.k_kayak_x, self.k_kayak_y - 20, 15)

        elif self.phase == "reading":
            # Auto-reveal lines slowly if player doesn't press
            self.line_timer += dt
            if self.line_timer > 2.5 and self.lines_revealed < len(MESSAGE_LINES):
                self.lines_revealed = min(len(MESSAGE_LINES), self.lines_revealed + 1)
                self.line_timer = 0.0

            # Gentle hearts during reading
            if random.random() < dt * 0.8:
                self._spawn_hearts(
                    self.w // 2 + random.uniform(-150, 150),
                    self.h * 0.3,
                    1,
                )

        elif self.phase == "done":
            if random.random() < dt * 2:
                self._spawn_hearts(
                    self.w // 2 + random.uniform(-100, 100),
                    self.h // 2 + random.uniform(-50, 50),
                    1,
                )

    def draw(self, surface):
        self._draw_sky(surface)
        self._draw_boston_skyline(surface)
        self._draw_river(surface)
        self._draw_kayaks(surface)
        self._draw_bottle(surface)
        self._draw_ripples(surface)
        self._draw_hearts(surface)
        self._draw_ui(surface)
        self._draw_phase_overlay(surface)

    def _draw_sky(self, surface):
        # Golden hour gradient
        for y in range(self.river_y):
            t = y / self.river_y
            r = int(255 * (1 - t) * 0.85 + 60 * t)
            g = int(180 * (1 - t) * 0.7 + 100 * t)
            b = int(100 * (1 - t) * 0.5 + 160 * t)
            surface.fill((min(255, r), min(255, g), min(255, b)), pygame.Rect(0, y, self.w, 1))

        # Sun setting
        sun_x = self.w * 0.5
        sun_y = self.river_y - 60
        # Sun glow
        for radius in [50, 40, 30, 20]:
            alpha = int(30 + (50 - radius) * 2)
            gs = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 200, 100, alpha), (radius, radius), radius)
            surface.blit(gs, (int(sun_x) - radius, int(sun_y) - radius))
        pygame.draw.circle(surface, (255, 220, 130), (int(sun_x), int(sun_y)), 18)

        # Clouds
        random.seed(55)
        for _ in range(4):
            cx = random.randint(50, self.w - 50)
            cy = random.randint(30, self.river_y - 100)
            size = random.randint(25, 45)
            # Tinted by sunset
            cloud_color = (255, 235, 210)
            for dx, dy, r in [(0, 0, size), (-size * 0.5, 3, size * 0.6), (size * 0.5, 3, size * 0.6)]:
                pygame.draw.circle(surface, cloud_color, (int(cx + dx), int(cy + dy)), int(r))
        random.seed()

    def _draw_boston_skyline(self, surface):
        # Simplified Boston/Cambridge skyline silhouette
        skyline_y = self.river_y - 8
        buildings = [
            (60, 35), (90, 55), (120, 40), (160, 70), (200, 45),
            (250, 60), (300, 80), (340, 50), (380, 65), (420, 90),
            (470, 55), (520, 70), (560, 45), (610, 60), (660, 75),
            (710, 50), (760, 40), (810, 55), (860, 35),
        ]
        silhouette_color = (40, 35, 50)
        for bx, bh in buildings:
            pygame.draw.rect(surface, silhouette_color,
                             (bx - 12, skyline_y - bh, 24, bh))
            # Some buildings get a pointed top
            if bh > 60:
                pygame.draw.polygon(surface, silhouette_color, [
                    (bx - 12, skyline_y - bh),
                    (bx + 12, skyline_y - bh),
                    (bx, skyline_y - bh - 15),
                ])
        # Tree line along river bank
        for tx in range(20, self.w, 35):
            pygame.draw.circle(surface, (30, 50, 35), (tx, skyline_y + 2), 12)

    def _draw_river(self, surface):
        # River fills bottom portion
        for y in range(self.river_y, self.h):
            t = (y - self.river_y) / (self.h - self.river_y)
            r = int(40 * (1 - t) + 25 * t)
            g = int(80 * (1 - t) + 55 * t)
            b = int(130 * (1 - t) + 90 * t)
            surface.fill((r, g, b), pygame.Rect(0, y, self.w, 1))

        # Water shimmer / reflections
        for i in range(12):
            shimmer_x = (i * 80 + int(self.t * 20)) % (self.w + 40) - 20
            shimmer_y = self.river_y + 15 + i * 12 + math.sin(self.t * 1.5 + i) * 4
            shimmer_w = 30 + int(math.sin(self.t * 2 + i * 0.7) * 10)
            alpha = 40 + int(math.sin(self.t * 2 + i) * 20)
            ss = pygame.Surface((shimmer_w, 3), pygame.SRCALPHA)
            pygame.draw.rect(ss, (200, 220, 255, alpha), (0, 0, shimmer_w, 3), border_radius=2)
            surface.blit(ss, (shimmer_x, int(shimmer_y)))

        # Sun reflection on water
        sun_x = self.w * 0.5
        for i in range(8):
            ref_y = self.river_y + 5 + i * 10
            ref_w = 15 - i
            wobble = math.sin(self.t * 3 + i * 0.8) * (3 + i * 2)
            if ref_w > 0:
                alpha = 80 - i * 8
                rs = pygame.Surface((ref_w * 2, 4), pygame.SRCALPHA)
                pygame.draw.rect(rs, (255, 220, 140, alpha), (0, 0, ref_w * 2, 4), border_radius=2)
                surface.blit(rs, (int(sun_x - ref_w + wobble), ref_y))

    def _draw_kayaks(self, surface):
        # Vandita's kayak (left, red)
        vx = int(self.v_kayak_x)
        vy = int(self.v_kayak_y + math.sin(self.t * 1.8) * 3)
        self._draw_kayak(surface, vx, vy, (180, 55, 55), (150, 40, 40))
        # Vandita sitting in kayak
        draw_cute_face(surface, vx, vy - 28, scale=0.7,
                       skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True)
        # Paddle
        paddle_angle = math.sin(self.t * 2) * 0.3
        p1x = vx - 30 + int(math.cos(paddle_angle) * 25)
        p1y = vy - 10 + int(math.sin(paddle_angle) * 15)
        p2x = vx + 30 - int(math.cos(paddle_angle) * 25)
        p2y = vy + 5 - int(math.sin(paddle_angle) * 15)
        pygame.draw.line(surface, (140, 120, 80), (p1x, p1y), (p2x, p2y), 3)
        # Paddle blades
        pygame.draw.ellipse(surface, (160, 140, 90), (p1x - 6, p1y - 3, 12, 10))
        pygame.draw.ellipse(surface, (160, 140, 90), (p2x - 6, p2y - 3, 12, 10))

        # Krishna's kayak (right, blue)
        kx = int(self.k_kayak_x)
        ky = int(self.k_kayak_y + math.sin(self.t * 1.8 + 1.2) * 3)
        self._draw_kayak(surface, kx, ky, (55, 80, 140), (40, 60, 110))
        # Krishna sitting
        draw_cute_face(surface, kx, ky - 28, scale=0.7,
                       skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True)
        # Paddle
        paddle_angle2 = math.sin(self.t * 2 + 0.5) * 0.3
        p1x = kx - 30 + int(math.cos(paddle_angle2) * 25)
        p1y = ky - 10 + int(math.sin(paddle_angle2) * 15)
        p2x = kx + 30 - int(math.cos(paddle_angle2) * 25)
        p2y = ky + 5 - int(math.sin(paddle_angle2) * 15)
        pygame.draw.line(surface, (140, 120, 80), (p1x, p1y), (p2x, p2y), 3)
        pygame.draw.ellipse(surface, (160, 140, 90), (p1x - 6, p1y - 3, 12, 10))
        pygame.draw.ellipse(surface, (160, 140, 90), (p2x - 6, p2y - 3, 12, 10))

    def _draw_kayak(self, surface, cx, cy, color, dark_color):
        # Kayak hull shape
        pts = [
            (cx - 50, cy), (cx - 40, cy - 10), (cx - 10, cy - 14),
            (cx + 10, cy - 14), (cx + 40, cy - 10), (cx + 50, cy),
            (cx + 40, cy + 6), (cx - 40, cy + 6),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, dark_color, pts, 2)
        # Seat area
        pygame.draw.ellipse(surface, dark_color, (cx - 12, cy - 12, 24, 10))

    def _draw_bottle(self, surface):
        if self.phase in ("intro", "bottle_floating"):
            bx = int(self.bottle_x)
            by = int(self.bottle_y)

            # Cork-sealed bottle with letter visible inside
            # Bottle body (glass, slightly transparent looking)
            pygame.draw.rect(surface, (180, 220, 200), (bx - 5, by - 14, 10, 20), border_radius=4)
            pygame.draw.rect(surface, (160, 200, 180), (bx - 5, by - 14, 10, 20), 2, border_radius=4)
            # Cork
            pygame.draw.rect(surface, (180, 150, 100), (bx - 3, by - 18, 6, 6), border_radius=2)
            # Letter inside (tiny scroll)
            pygame.draw.rect(surface, (240, 230, 200), (bx - 3, by - 10, 6, 12), border_radius=1)
            # Tiny text lines on letter
            for i in range(3):
                pygame.draw.line(surface, (160, 140, 120),
                                 (bx - 2, by - 8 + i * 4), (bx + 2, by - 8 + i * 4), 1)

            # Water wake behind bottle when floating
            if self.phase == "bottle_floating":
                for i in range(3):
                    wake_x = bx - 8 - i * 6
                    wake_y = by + 8
                    alpha = 100 - i * 30
                    ws = pygame.Surface((8, 3), pygame.SRCALPHA)
                    pygame.draw.ellipse(ws, (200, 220, 255, alpha), (0, 0, 8, 3))
                    surface.blit(ws, (wake_x, wake_y))

    def _draw_ripples(self, surface):
        for r in self.ripples:
            if r["alpha"] > 0:
                rs = pygame.Surface((int(r["r"]) * 2, int(r["r"]) * 2), pygame.SRCALPHA)
                pygame.draw.circle(rs, (200, 220, 255, int(r["alpha"])),
                                   (int(r["r"]), int(r["r"])), int(r["r"]), 2)
                surface.blit(rs, (int(r["x"] - r["r"]), int(r["y"] - r["r"])))

    def _draw_hearts(self, surface):
        for h in self.hearts:
            alpha = max(0, min(255, int(h.life * 255)))
            _draw_heart(surface, int(h.x), int(h.y), int(h.size), (*HEART_RED, alpha))

    def _draw_ui(self, surface):
        # Header
        card_rect = pygame.Rect(self.w // 2 - 240, 12, 480, 42)
        draw_rounded_rect(surface, (*CARD_BG, 200), card_rect, radius=14, shadow=True, shadow_offset=3)
        hdr = self.f_hdr.render("Chapter 3  ·  The Charles River", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2, 18))

    def _draw_phase_overlay(self, surface):
        if self.phase == "intro":
            if self.phase_timer > 0.5:
                alpha = min(255, int((self.phase_timer - 0.5) * 180))
                txt = self.f_sub.render("Charles River, Boston. Two kayaks. One question.", True, CREAM)
                txt.set_alpha(alpha)
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.82))

            if self.phase_timer > 2.0 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.90))

        elif self.phase == "bottle_floating":
            progress = min(1.0, self.phase_timer / 3.5)
            if progress < 0.3:
                txt = self.f_sub.render("She puts a letter in a bottle...", True, CREAM)
                txt.set_alpha(min(255, int(self.phase_timer * 200)))
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.82))
            elif progress < 0.7:
                txt = self.f_sub.render("...corks it, and sends it across.", True, CREAM)
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.82))

        elif self.phase == "catch":
            alpha = min(255, int(self.phase_timer * 200))
            txt = self.f_mid.render("He catches it. Opens the cork.", True, CREAM)
            txt.set_alpha(alpha)
            surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.82))

            if self.phase_timer > 1.0 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key to read", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.90))

        elif self.phase == "reading":
            # Letter overlay - parchment style
            margin = 60
            letter_rect = pygame.Rect(margin, 65, self.w - margin * 2, self.h - 130)

            # Parchment background
            parchment = pygame.Surface((letter_rect.width, letter_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(parchment, (250, 240, 220, 240),
                             (0, 0, letter_rect.width, letter_rect.height), border_radius=12)
            # Subtle paper texture lines
            for i in range(0, letter_rect.height, 28):
                pygame.draw.line(parchment, (230, 218, 195, 60),
                                 (20, i), (letter_rect.width - 20, i), 1)
            # Border
            pygame.draw.rect(parchment, (200, 180, 150, 180),
                             (0, 0, letter_rect.width, letter_rect.height), 2, border_radius=12)
            surface.blit(parchment, (letter_rect.x, letter_rect.y))

            # Render revealed lines
            y_pos = letter_rect.y + 24
            for i in range(min(self.lines_revealed, len(MESSAGE_LINES))):
                line = MESSAGE_LINES[i]
                if not line:
                    y_pos += 14
                    continue

                # Last two lines are bold (the birthday + love you)
                is_bold = (i >= len(MESSAGE_LINES) - 2 and line)
                font = self.f_letter_bold if is_bold else self.f_letter
                color = DARK_BROWN if not is_bold else (160, 50, 60)

                # Fade in the most recently revealed lines
                line_alpha = 255
                if i >= self.lines_revealed - 3:
                    age = (self.lines_revealed - i) / 3
                    line_alpha = min(255, int(age * 255 + 100))

                txt = font.render(line, True, color)
                txt.set_alpha(line_alpha)
                surface.blit(txt, (letter_rect.x + 30, y_pos))
                y_pos += 24

            # "Press any key for more" or "press to continue"
            if self.lines_revealed < len(MESSAGE_LINES):
                if int(self.t * 2) % 2 == 0:
                    more = self.f_ui.render("Press any key to read more...", True, MID_BROWN)
                    surface.blit(more, (self.w // 2 - more.get_width() // 2, self.h - 50))
            else:
                if int(self.t * 2) % 2 == 0:
                    more = self.f_ui.render("Press any key to continue", True, MID_BROWN)
                    surface.blit(more, (self.w // 2 - more.get_width() // 2, self.h - 50))

        elif self.phase == "done":
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            alpha = min(200, int(self.phase_timer * 120))
            overlay.fill((*SOFT_PINK, alpha))
            surface.blit(overlay, (0, 0))

            if self.phase_timer > 0.5:
                pass  # clean transition to finale

            if self.phase_timer > 1.5 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, MID_BROWN)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))
