"""
Level 6: Will You Be Mine?
===========================
Twilight park proposal scene. Walk Krishna around, set up 6 romantic elements
one by one. Each interaction has a visual payoff. Once everything is perfect,
kneel and propose. Multi-phase ending: proposal -> "yes" -> she cries -> finale.
"""
import math
import random

import pygame

from src.utils.constants import (
    CREAM,
    SKY_BLUE,
    SOFT_GREEN,
    LEAF_GREEN,
    SOFT_PINK,
    AMBER,
    AMBER_DARK,
    CARD_BG,
    DARK_BROWN,
    MID_BROWN,
    GOLD,
    HEART_RED,
    WHITE,
    SCENE_LEVEL7,
)
from src.utils.draw_helpers import (
    draw_cute_face,
    draw_rounded_rect,
)


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
        speed = random.uniform(1.5, 4.0)
        self.x = cx + random.uniform(-20, 20)
        self.y = cy + random.uniform(-10, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2.5
        self.size = random.uniform(8, 18)
        self.life = 1.0
        self.decay = random.uniform(0.012, 0.025)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= self.decay
        self.size *= 0.985

    @property
    def alive(self):
        return self.life > 0 and self.size > 1


# The 6 setup tasks, in order
TASKS = [
    {"name": "music",    "label": "Start the music",      "done_label": "Music playing",      "emoji": "🎵"},
    {"name": "blanket",  "label": "Lay the blanket",     "done_label": "Blanket laid",       "emoji": "🧶"},
    {"name": "candles",  "label": "Light the candles",    "done_label": "Candles lit",        "emoji": "🕯️"},
    {"name": "wine",     "label": "Pour the wine",       "done_label": "Wine poured",        "emoji": "🍷"},
    {"name": "flowers",  "label": "Place the flowers",    "done_label": "Flowers placed",     "emoji": "💐"},
    {"name": "lights",   "label": "Turn on the lights",   "done_label": "Lights glowing",     "emoji": "✨"},
]


class Level6ProposalPark:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        # Player
        self.x = self.w * 0.15
        self.y = self.h * 0.68
        self.speed = 200.0
        self.facing_right = True

        # 6 interaction points spread across the park
        self.targets = [
            {"name": "music",    "x": self.w * 0.18, "y": self.h * 0.50, "on": False},
            {"name": "blanket",  "x": self.w * 0.50, "y": self.h * 0.72, "on": False},
            {"name": "candles",  "x": self.w * 0.72, "y": self.h * 0.65, "on": False},
            {"name": "wine",     "x": self.w * 0.30, "y": self.h * 0.60, "on": False},
            {"name": "flowers",  "x": self.w * 0.82, "y": self.h * 0.55, "on": False},
            {"name": "lights",   "x": self.w * 0.58, "y": self.h * 0.48, "on": False},
        ]

        self.interact_radius = 75
        self.near_target = None  # currently near target name

        # Completion feedback
        self.flash_timer = 0.0
        self.flash_text = ""
        self.completed_count = 0

        # Wine pour animation
        self.wine_pouring = False
        self.wine_pour_timer = 0.0
        self.wine_pour_duration = 1.6  # seconds to fill both glasses

        # Proposal phases
        self.phase = "setup"  # setup -> kneel -> propose -> yes -> crying -> done
        self.phase_timer = 0.0

        # Hearts
        self.hearts: list[HeartParticle] = []

        # Vandita appears after all setup, walks in from right
        self.vandita_x = self.w + 60
        self.vandita_target_x = self.w * 0.55

        # Fireflies (ambient after lights are on)
        self.fireflies = []
        for _ in range(20):
            self.fireflies.append({
                "x": random.uniform(40, screen_w - 40),
                "y": random.uniform(screen_h * 0.3, screen_h * 0.75),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.3, 0.8),
            })

        self.t = 0.0

        # Fonts
        self.f_hdr = pygame.font.SysFont("Georgia", 24, bold=True)
        self.f_sub = pygame.font.SysFont("Georgia", 18, italic=True)
        self.f_ui = pygame.font.SysFont("Arial", 18)
        self.f_ui_bold = pygame.font.SysFont("Arial", 18, bold=True)
        self.f_big = pygame.font.SysFont("Georgia", 44, bold=True)
        self.f_mid = pygame.font.SysFont("Georgia", 26, bold=True)
        self.f_small = pygame.font.SysFont("Georgia", 16, italic=True)
        self.f_task = pygame.font.SysFont("Arial", 15)
        self.f_flash = pygame.font.SysFont("Georgia", 24, bold=True)

    # ------------------------------------------------------------------ events
    def handle_event(self, event):
        if self.phase == "done":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.next_scene = SCENE_LEVEL7

            return

        if self.phase == "crying":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) and self.phase_timer > 2.0:
                self.phase = "done"
                self.phase_timer = 0.0
            return

        if self.phase in ("kneel", "propose", "yes"):
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) and self.phase_timer > 1.5:
                from src.utils.sounds import get_sfx
                if self.phase == "kneel":
                    self.phase = "propose"
                    self.phase_timer = 0.0
                    get_sfx().heartbeat.play()
                elif self.phase == "propose":
                    self.phase = "yes"
                    self.phase_timer = 0.0
                    self._spawn_hearts(self.w // 2, self.h // 2, 50)
                    get_sfx().celebrate.play()
                elif self.phase == "yes":
                    self.phase = "crying"
                    self.phase_timer = 0.0
            return

        if self.phase == "setup":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._try_interact()

    # ------------------------------------------------------------------- logic
    def _try_interact(self):
        if self.wine_pouring:
            return  # wait for pour to finish
        for t in self.targets:
            if t["on"]:
                continue
            dx = self.x - t["x"]
            dy = self.y - t["y"]
            if dx * dx + dy * dy < self.interact_radius ** 2:
                from src.utils.sounds import get_sfx
                if t["name"] == "wine":
                    # Start pour animation, don't mark done yet
                    self.wine_pouring = True
                    self.wine_pour_timer = 0.0
                    get_sfx().pour.play()
                    break
                t["on"] = True
                self.completed_count += 1
                if t["name"] == "music":
                    # Play "Right Down the Line" by Gerry Rafferty
                    import os
                    song_path = os.path.join(
                        os.path.dirname(__file__), "..", "..", "assets", "sounds", "right_down_the_line.mp3"
                    )
                    if os.path.exists(song_path):
                        try:
                            pygame.mixer.music.load(song_path)
                            pygame.mixer.music.set_volume(0.4)
                            pygame.mixer.music.play(-1)  # loop
                        except Exception:
                            pass
                get_sfx().interact.play()
                # Flash feedback
                task_info = next(tk for tk in TASKS if tk["name"] == t["name"])
                self.flash_text = f"{task_info['emoji']} {task_info['done_label']}!"
                self.flash_timer = 1.8
                self._spawn_hearts(t["x"], t["y"], 12)

                # All done? Start proposal sequence
                if self.completed_count >= len(self.targets):
                    self.phase = "vandita_entering"
                    self.phase_timer = 0.0
                break

    def _spawn_hearts(self, cx, cy, count):
        for _ in range(count):
            self.hearts.append(HeartParticle(cx, cy))

    # ------------------------------------------------------------------- update
    def update(self, dt: float):
        self.t += dt

        # Hearts
        for h in self.hearts:
            h.update()
        self.hearts = [h for h in self.hearts if h.alive]

        # Flash timer
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.phase == "setup":
            if not self.wine_pouring:
                self._update_movement(dt)
                self._update_near_target()
            else:
                self.wine_pour_timer += dt
                if self.wine_pour_timer >= self.wine_pour_duration:
                    self.wine_pouring = False
                    wine_t = next(t for t in self.targets if t["name"] == "wine")
                    wine_t["on"] = True
                    self.completed_count += 1
                    task_info = next(tk for tk in TASKS if tk["name"] == "wine")
                    self.flash_text = f"{task_info['emoji']} {task_info['done_label']}!"
                    self.flash_timer = 1.8
                    self._spawn_hearts(wine_t["x"], wine_t["y"], 12)
                    if self.completed_count >= len(self.targets):
                        self.phase = "vandita_entering"
                        self.phase_timer = 0.0

        elif self.phase == "vandita_entering":
            self.phase_timer += dt
            # Vandita walks in from right
            if self.vandita_x > self.vandita_target_x:
                self.vandita_x -= 120 * dt
            else:
                self.vandita_x = self.vandita_target_x
            # After she arrives, transition to kneel
            if self.phase_timer > 2.5:
                self.phase = "kneel"
                self.phase_timer = 0.0
                # Move Krishna near Vandita
                self.x = self.vandita_target_x - 60

        elif self.phase in ("kneel", "propose", "yes", "crying", "done"):
            self.phase_timer += dt
            # Keep spawning gentle hearts during emotional phases
            if self.phase in ("yes", "crying") and random.random() < dt * 3:
                self._spawn_hearts(
                    self.w // 2 + random.uniform(-100, 100),
                    self.h // 2 + random.uniform(-50, 50),
                    1,
                )

    def _update_movement(self, dt):
        keys = pygame.key.get_pressed()
        vx = vy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= 1
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1
            self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy += 1

        mag = math.hypot(vx, vy)
        if mag > 0:
            vx /= mag
            vy /= mag
            self.x += vx * self.speed * dt
            self.y += vy * self.speed * dt

        margin = 50
        self.x = max(margin, min(self.w - margin, self.x))
        ground_min = int(self.h * 0.42)
        self.y = max(ground_min, min(self.h - margin, self.y))

    def _update_near_target(self):
        self.near_target = None
        for t in self.targets:
            if t["on"]:
                continue
            dx = self.x - t["x"]
            dy = self.y - t["y"]
            if dx * dx + dy * dy < self.interact_radius ** 2:
                self.near_target = t["name"]
                break

    # --------------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface):
        self._draw_background(surface)
        self._draw_scenery(surface)
        self._draw_targets(surface)
        self._draw_characters(surface)
        self._draw_hearts(surface)
        self._draw_ui(surface)
        self._draw_phase_overlays(surface)

    def _draw_background(self, surface):
        # Twilight gradient
        for y in range(self.h):
            t = y / self.h
            r = int(25 * (1 - t) + 45 * t)
            g = int(20 * (1 - t) + 55 * t)
            b = int(55 * (1 - t) + 85 * t)
            surface.fill((r, g, b), pygame.Rect(0, y, self.w, 1))

        # Stars
        random.seed(99)
        for _ in range(30):
            sx = random.randint(10, self.w - 10)
            sy = random.randint(10, int(self.h * 0.35))
            brightness = 160 + int(math.sin(self.t * 2 + sx) * 60)
            size = random.choice([1, 1, 2])
            pygame.draw.circle(surface, (brightness, brightness, brightness + 20), (sx, sy), size)
        random.seed()

    def _draw_scenery(self, surface):
        base_y = int(self.h * 0.70)

        # Grass with gentle wave
        ground_pts = [(0, self.h)]
        for x in range(0, self.w + 30, 12):
            y_off = math.sin(x * 0.010 + self.t * 0.4) * 8
            ground_pts.append((x, base_y + y_off))
        ground_pts.append((self.w, self.h))
        pygame.draw.polygon(surface, (45, 95, 50), ground_pts)

        # Grass highlight
        for x in range(0, self.w + 30, 12):
            y_off = math.sin(x * 0.010 + self.t * 0.4) * 8
            pygame.draw.circle(surface, (55, 115, 60), (x, int(base_y + y_off)), 2)

        # Trees
        tree_positions = [80, 240, 520, 720, 860]
        for tx in tree_positions:
            ty = base_y - 45
            pygame.draw.rect(surface, (30, 20, 10), (tx - 5, ty, 10, 45))
            pygame.draw.circle(surface, (25, 55, 28), (tx, ty), 28)
            pygame.draw.circle(surface, (30, 65, 32), (tx - 8, ty + 5), 18)
            pygame.draw.circle(surface, (28, 58, 30), (tx + 10, ty + 3), 20)

        # String lights between trees (always visible, glow stronger when "lights" is on)
        lights_on = any(t["on"] for t in self.targets if t["name"] == "lights")
        light_y = base_y - 100
        points = []
        for i in range(len(tree_positions)):
            px = tree_positions[i]
            py = light_y + math.sin(self.t * 1.0 + i * 1.2) * 5 + (i % 2) * 8
            points.append((px, py))
        if len(points) > 1:
            pygame.draw.lines(surface, (100, 85, 60), False, points, 2)
        for i, (px, py) in enumerate(points):
            if lights_on:
                glow = 200 + int(math.sin(self.t * 3 + i * 1.5) * 55)
                pygame.draw.circle(surface, (glow, glow, int(glow * 0.7)), (int(px), int(py)), 7)
                # Glow halo
                gs = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(gs, (255, 240, 180, 40), (15, 15), 15)
                surface.blit(gs, (int(px) - 15, int(py) - 15))
            else:
                pygame.draw.circle(surface, (80, 75, 60), (int(px), int(py)), 4)

        # Fireflies (only after lights are on)
        if lights_on:
            for ff in self.fireflies:
                ff_x = ff["x"] + math.sin(self.t * ff["speed"] + ff["phase"]) * 15
                ff_y = ff["y"] + math.cos(self.t * ff["speed"] * 0.7 + ff["phase"]) * 10
                brightness = 0.5 + 0.5 * math.sin(self.t * 2 + ff["phase"])
                alpha = int(brightness * 180)
                fs = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(fs, (255, 240, 150, alpha), (5, 5), 3)
                pygame.draw.circle(fs, (255, 255, 200, alpha // 3), (5, 5), 5)
                surface.blit(fs, (int(ff_x) - 5, int(ff_y) - 5))

    def _draw_targets(self, surface):
        for t in self.targets:
            tx, ty = int(t["x"]), int(t["y"])
            name = t["name"]
            on = t["on"]

            if name == "blanket":
                rect = pygame.Rect(tx - 85, ty - 14, 170, 48)
                if on:
                    # Rich warm blanket with pattern
                    pygame.draw.rect(surface, (180, 60, 60), rect, border_radius=10)
                    pygame.draw.rect(surface, (200, 80, 70), rect, 2, border_radius=10)
                    # Plaid pattern
                    for i in range(3):
                        lx = rect.x + 20 + i * 45
                        pygame.draw.line(surface, (160, 50, 50), (lx, rect.y + 4), (lx, rect.y + 44), 2)
                    for j in range(2):
                        ly = rect.y + 16 + j * 16
                        pygame.draw.line(surface, (160, 50, 50), (rect.x + 4, ly), (rect.x + 166, ly), 2)
                else:
                    # Folded blanket (smaller, muted)
                    small = pygame.Rect(tx - 30, ty - 8, 60, 28)
                    pygame.draw.rect(surface, (140, 120, 100), small, border_radius=6)
                    pygame.draw.rect(surface, (120, 100, 80), small, 2, border_radius=6)

            elif name == "candles":
                if on:
                    # 3 lit candles
                    for i, cx in enumerate([tx - 22, tx, tx + 22]):
                        h = 24 + i * 4
                        pygame.draw.rect(surface, (240, 230, 210), (cx - 5, ty - h, 10, h), border_radius=3)
                        # Flame
                        flame_flicker = math.sin(self.t * 6 + i * 2) * 2
                        pygame.draw.circle(surface, (255, 200, 50), (cx, int(ty - h - 6 + flame_flicker)), 5)
                        pygame.draw.circle(surface, (255, 140, 30), (cx, int(ty - h - 4 + flame_flicker)), 3)
                        # Glow
                        gs = pygame.Surface((40, 40), pygame.SRCALPHA)
                        pygame.draw.circle(gs, (255, 200, 100, 30), (20, 20), 20)
                        surface.blit(gs, (cx - 20, int(ty - h - 26)))
                else:
                    # Unlit candles
                    for i, cx in enumerate([tx - 15, tx + 15]):
                        pygame.draw.rect(surface, (200, 190, 170), (cx - 4, ty - 18, 8, 18), border_radius=2)

            elif name == "wine":
                # Bottle (always upright once interacting or done)
                pouring = self.wine_pouring
                pour_progress = min(1.0, self.wine_pour_timer / self.wine_pour_duration) if pouring else 0.0

                if on or pouring:
                    # Bottle tilted while pouring, upright when done
                    bottle_surf = pygame.Surface((60, 70), pygame.SRCALPHA)
                    # Bottle body
                    pygame.draw.rect(bottle_surf, (45, 85, 55), (22, 18, 14, 36), border_radius=4)
                    # Bottle neck
                    pygame.draw.rect(bottle_surf, (35, 65, 45), (25, 4, 8, 18), border_radius=2)
                    # Label
                    pygame.draw.rect(bottle_surf, (180, 160, 120), (24, 28, 10, 14), border_radius=2)

                    if pouring:
                        # Tilt bottle
                        angle = 35 * min(1.0, pour_progress * 2)  # tilt in first half
                        rotated = pygame.transform.rotate(bottle_surf, angle)
                        surface.blit(rotated, (tx - 20 - rotated.get_width() // 2, ty - 55))

                        # Pour stream from bottle to glass
                        if pour_progress > 0.1:
                            stream_alpha = int(min(1.0, (pour_progress - 0.1) * 3) * 200)
                            stream_end_y = ty - 8
                            stream_start_y = ty - 40
                            for sy in range(stream_start_y, stream_end_y, 2):
                                wobble = math.sin(sy * 0.3 + self.t * 8) * 2
                                pygame.draw.circle(surface, (140, 30, 40, stream_alpha),
                                                   (tx + 12 + int(wobble), sy), 2)
                    else:
                        surface.blit(bottle_surf, (tx - 30, ty - 55))

                    # Glass 1 (fills first half of pour)
                    g1x, g1y = tx + 6, ty - 4
                    # Glass outline
                    pygame.draw.polygon(surface, (220, 240, 255, 180), [
                        (g1x - 7, g1y - 22), (g1x + 7, g1y - 22),
                        (g1x + 9, g1y), (g1x - 9, g1y),
                    ])
                    # Stem
                    pygame.draw.rect(surface, (200, 220, 240), (g1x - 2, g1y, 4, 8), border_radius=1)
                    # Base
                    pygame.draw.ellipse(surface, (200, 220, 240), (g1x - 8, g1y + 7, 16, 5))
                    # Wine fill
                    fill1 = min(1.0, pour_progress * 2) if pouring else 1.0
                    if fill1 > 0:
                        fill_h = int(fill1 * 16)
                        wine_rect = pygame.Rect(g1x - 6, g1y - 2 - fill_h, 12, fill_h)
                        pygame.draw.rect(surface, (140, 30, 45), wine_rect, border_radius=2)

                    # Glass 2 (fills second half of pour)
                    g2x, g2y = tx + 28, ty - 6
                    pygame.draw.polygon(surface, (220, 240, 255, 180), [
                        (g2x - 7, g2y - 24), (g2x + 7, g2y - 24),
                        (g2x + 9, g2y), (g2x - 9, g2y),
                    ])
                    pygame.draw.rect(surface, (200, 220, 240), (g2x - 2, g2y, 4, 8), border_radius=1)
                    pygame.draw.ellipse(surface, (200, 220, 240), (g2x - 8, g2y + 7, 16, 5))
                    fill2 = max(0.0, min(1.0, (pour_progress - 0.4) * 2.5)) if pouring else 1.0
                    if fill2 > 0:
                        fill_h = int(fill2 * 18)
                        wine_rect = pygame.Rect(g2x - 6, g2y - 2 - fill_h, 12, fill_h)
                        pygame.draw.rect(surface, (140, 30, 45), wine_rect, border_radius=2)

                else:
                    # Empty bottle on its side + empty glasses
                    pygame.draw.rect(surface, (80, 80, 75), (tx - 18, ty - 8, 36, 10), border_radius=4)
                    # Two empty glasses
                    for gx in [tx + 10, tx + 28]:
                        pygame.draw.polygon(surface, (180, 200, 220, 120), [
                            (gx - 5, ty - 18), (gx + 5, ty - 18),
                            (gx + 7, ty - 2), (gx - 7, ty - 2),
                        ])
                        pygame.draw.rect(surface, (180, 200, 220), (gx - 2, ty - 2, 4, 6), border_radius=1)

            elif name == "flowers":
                if on:
                    # Beautiful vase with arranged flowers
                    # Vase
                    pygame.draw.polygon(surface, (180, 160, 200), [
                        (tx - 12, ty + 4), (tx + 12, ty + 4),
                        (tx + 16, ty - 14), (tx - 16, ty - 14),
                    ])
                    pygame.draw.ellipse(surface, (160, 140, 180), (tx - 16, ty - 18, 32, 8))
                    pygame.draw.ellipse(surface, (190, 170, 210), (tx - 12, ty + 2, 24, 6))
                    # Vase pattern (cute stripe)
                    pygame.draw.line(surface, (200, 180, 220), (tx - 14, ty - 6), (tx + 14, ty - 6), 2)

                    # 7 flowers fanning out from vase
                    rng = random.Random(77)
                    flower_colors = [
                        (255, 130, 150), (255, 200, 110), (210, 140, 230),
                        (255, 170, 130), (180, 200, 255), (255, 160, 180), (200, 230, 160),
                    ]
                    for i, col in enumerate(flower_colors):
                        angle = -0.8 + i * 0.27
                        stem_len = 30 + rng.randint(0, 12)
                        sway = math.sin(self.t * 1.5 + i * 0.9) * 3
                        fx = tx + int(math.sin(angle + sway * 0.02) * stem_len)
                        fy = ty - 14 - int(math.cos(angle) * stem_len)
                        # Stem
                        pygame.draw.line(surface, (70, 130, 55), (tx, ty - 14), (fx, fy), 2)
                        # Leaf on some stems
                        if i % 3 == 0:
                            mid_x = (tx + fx) // 2
                            mid_y = (ty - 14 + fy) // 2
                            pygame.draw.ellipse(surface, (80, 150, 60), (mid_x - 4, mid_y - 2, 8, 5))
                        # Flower head: petals around center
                        for p in range(5):
                            pa = p * (math.pi * 2 / 5) + self.t * 0.3
                            px = fx + int(math.cos(pa) * 5)
                            py = fy + int(math.sin(pa) * 5)
                            pygame.draw.circle(surface, col, (px, py), 4)
                        # Center
                        pygame.draw.circle(surface, (255, 240, 180), (fx, fy), 3)
                else:
                    # Wrapped bouquet on ground (tissue paper bundle)
                    pygame.draw.polygon(surface, (200, 180, 190), [
                        (tx - 20, ty + 4), (tx + 20, ty + 4),
                        (tx + 14, ty - 16), (tx - 14, ty - 16),
                    ])
                    # Tissue paper crinkles at top
                    for i in range(5):
                        cx = tx - 12 + i * 6
                        pygame.draw.circle(surface, (220, 200, 210), (cx, ty - 16), 5)
                    # Ribbon
                    pygame.draw.line(surface, (200, 120, 140), (tx - 8, ty - 6), (tx + 8, ty - 6), 2)
                    # Small bow
                    pygame.draw.circle(surface, (220, 140, 160), (tx - 6, ty - 8), 3)
                    pygame.draw.circle(surface, (220, 140, 160), (tx + 6, ty - 8), 3)

            elif name == "music":
                if on:
                    # Cute retro radio/boombox with bouncing speaker cones
                    # Body
                    body_rect = pygame.Rect(tx - 22, ty - 18, 44, 30)
                    pygame.draw.rect(surface, (65, 55, 75), body_rect, border_radius=8)
                    pygame.draw.rect(surface, (85, 75, 95), body_rect, 2, border_radius=8)
                    # Antenna
                    antenna_sway = math.sin(self.t * 2) * 4
                    pygame.draw.line(surface, (120, 110, 130),
                                     (tx + 12, ty - 18), (tx + 16 + int(antenna_sway), ty - 38), 2)
                    pygame.draw.circle(surface, (200, 180, 220), (tx + 16 + int(antenna_sway), ty - 40), 3)
                    # Two speaker cones (pulse with beat)
                    beat = abs(math.sin(self.t * 4))
                    for sx_off in [-10, 10]:
                        sr = 7 + int(beat * 2)
                        pygame.draw.circle(surface, (45, 40, 55), (tx + sx_off, ty - 4), sr)
                        pygame.draw.circle(surface, (80, 70, 90), (tx + sx_off, ty - 4), sr - 2)
                        pygame.draw.circle(surface, (55, 50, 65), (tx + sx_off, ty - 4), 3)
                    # Dial/tuner
                    pygame.draw.rect(surface, (200, 180, 160), (tx - 6, ty - 16, 12, 4), border_radius=2)
                    # Floating music notes (more, colorful, wavy)
                    note_colors = [(255, 200, 230), (200, 220, 255), (255, 230, 180), (220, 200, 255)]
                    for i in range(5):
                        phase = self.t * 1.8 + i * 1.3
                        note_x = tx + 24 + int(math.sin(phase) * 18)
                        note_y = ty - 20 - int((phase * 12) % 55)
                        note_alpha = 220 - int((phase * 12) % 55) * 3.5
                        if note_alpha > 0:
                            note_char = ["♪", "♫", "♩", "♬", "♪"][i]
                            ns = self.f_task.render(note_char, True, note_colors[i % 4])
                            ns.set_alpha(max(0, int(note_alpha)))
                            surface.blit(ns, (note_x, note_y))
                else:
                    # Cute silent boombox (muted colors, no animation)
                    body_rect = pygame.Rect(tx - 18, ty - 14, 36, 24)
                    pygame.draw.rect(surface, (80, 75, 70), body_rect, border_radius=6)
                    pygame.draw.rect(surface, (95, 88, 82), body_rect, 2, border_radius=6)
                    # Dead speakers
                    for sx_off in [-8, 8]:
                        pygame.draw.circle(surface, (65, 60, 55), (tx + sx_off, ty - 3), 6)
                        pygame.draw.circle(surface, (75, 70, 65), (tx + sx_off, ty - 3), 3)
                    # Broken antenna
                    pygame.draw.line(surface, (100, 90, 85), (tx + 10, ty - 14), (tx + 13, ty - 22), 2)

            elif name == "lights":
                if on:
                    # Cute lantern glowing warm
                    # Lantern body
                    pygame.draw.rect(surface, (60, 55, 70), (tx - 14, ty - 20, 28, 32), border_radius=8)
                    # Glass panels with warm glow
                    glow_pulse = 0.7 + 0.3 * math.sin(self.t * 2.5)
                    glow_color = (
                        int(255 * glow_pulse),
                        int(220 * glow_pulse),
                        int(130 * glow_pulse),
                    )
                    pygame.draw.rect(surface, glow_color, (tx - 10, ty - 16, 20, 24), border_radius=4)
                    # Cross pattern on lantern glass
                    pygame.draw.line(surface, (80, 70, 60), (tx, ty - 16), (tx, ty + 8), 2)
                    pygame.draw.line(surface, (80, 70, 60), (tx - 10, ty - 4), (tx + 10, ty - 4), 2)
                    # Top cap
                    pygame.draw.rect(surface, (50, 45, 58), (tx - 16, ty - 22, 32, 5), border_radius=3)
                    # Handle
                    pygame.draw.arc(surface, (70, 65, 80),
                                    pygame.Rect(tx - 8, ty - 32, 16, 14), 0, math.pi, 2)
                    # Bottom cap
                    pygame.draw.rect(surface, (50, 45, 58), (tx - 16, ty + 10, 32, 4), border_radius=2)
                    # Warm glow halo
                    gs = pygame.Surface((60, 60), pygame.SRCALPHA)
                    pygame.draw.circle(gs, (255, 220, 130, int(35 * glow_pulse)), (30, 30), 30)
                    pygame.draw.circle(gs, (255, 240, 160, int(20 * glow_pulse)), (30, 30), 22)
                    surface.blit(gs, (tx - 30, ty - 24))
                else:
                    # Unlit lantern (dark, cold)
                    pygame.draw.rect(surface, (55, 50, 60), (tx - 14, ty - 20, 28, 32), border_radius=8)
                    pygame.draw.rect(surface, (40, 38, 48), (tx - 10, ty - 16, 20, 24), border_radius=4)
                    # Cross pattern
                    pygame.draw.line(surface, (50, 45, 55), (tx, ty - 16), (tx, ty + 8), 2)
                    pygame.draw.line(surface, (50, 45, 55), (tx - 10, ty - 4), (tx + 10, ty - 4), 2)
                    # Top cap
                    pygame.draw.rect(surface, (45, 40, 50), (tx - 16, ty - 22, 32, 5), border_radius=3)
                    # Handle
                    pygame.draw.arc(surface, (60, 55, 65),
                                    pygame.Rect(tx - 8, ty - 32, 16, 14), 0, math.pi, 2)
                    # Bottom
                    pygame.draw.rect(surface, (45, 40, 50), (tx - 16, ty + 10, 32, 4), border_radius=2)

            # Item label (when not yet activated and player is near)
            if not on and self.near_target == name:
                task_info = next(tk for tk in TASKS if tk["name"] == name)
                lbl = self.f_ui_bold.render(f"[SPACE] {task_info['label']}", True, WHITE)
                lbl_bg = pygame.Surface((lbl.get_width() + 16, lbl.get_height() + 8), pygame.SRCALPHA)
                pygame.draw.rect(lbl_bg, (0, 0, 0, 180), (0, 0, lbl_bg.get_width(), lbl_bg.get_height()), border_radius=8)
                lbl_bg.blit(lbl, (8, 4))
                surface.blit(lbl_bg, (tx - lbl_bg.get_width() // 2, ty - 55))

    def _draw_characters(self, surface):
        if self.phase == "setup":
            # Walking Krishna
            walk_bob = math.sin(self.t * 6.0) * 3
            draw_cute_face(
                surface, int(self.x), int(self.y + walk_bob), scale=0.9,
                skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True,
            )

        elif self.phase == "vandita_entering":
            # Krishna standing still
            draw_cute_face(
                surface, int(self.x), int(self.y), scale=0.9,
                skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True,
            )
            # Vandita walking in
            walk_bob = math.sin(self.t * 5.0) * 2
            draw_cute_face(
                surface, int(self.vandita_x), int(self.h * 0.68 + walk_bob), scale=0.9,
                skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True,
            )
        elif self.phase in ("kneel", "propose", "yes", "crying", "done"):
            blanket = next(t for t in self.targets if t["name"] == "blanket")
            bx = int(blanket["x"])
            by = int(blanket["y"])

            if self.phase == "kneel":
                # Krishna kneeling (drawn smaller, lower)
                draw_cute_face(
                    surface, bx - 30, by + 8, scale=0.7,
                    skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True,
                )
                # Vandita standing
                draw_cute_face(
                    surface, bx + 30, by - 5, scale=0.9,
                    skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True,
                )
            else:
                # Both together on blanket
                draw_cute_face(
                    surface, bx - 24, by + 8, scale=0.85,
                    skin=(200, 158, 115), hair=(40, 28, 15), hair_style=4, blush=True,
                )
                draw_cute_face(
                    surface, bx + 24, by + 8, scale=0.85,
                    skin=(235, 195, 160), hair=(100, 70, 40), hair_style=1, blush=True,
                )

    def _draw_hearts(self, surface):
        for h in self.hearts:
            alpha = max(0, min(255, int(h.life * 255)))
            _draw_heart(surface, int(h.x), int(h.y), int(h.size), (*HEART_RED, alpha))

    def _draw_ui(self, surface):
        # Header
        card_rect = pygame.Rect(self.w // 2 - 260, 12, 520, 42)
        draw_rounded_rect(surface, (*CARD_BG, 210), card_rect, radius=14, shadow=True, shadow_offset=3)
        hdr = self.f_hdr.render("Chapter 2  ·  Will You Be Mine?", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2, 18))

        if self.phase == "setup":
            # Task checklist on the left side
            checklist_x = 16
            checklist_y = 70
            bg = pygame.Surface((200, len(TASKS) * 26 + 16), pygame.SRCALPHA)
            pygame.draw.rect(bg, (0, 0, 0, 140), (0, 0, bg.get_width(), bg.get_height()), border_radius=10)
            surface.blit(bg, (checklist_x, checklist_y))

            for i, task in enumerate(TASKS):
                target = next(t for t in self.targets if t["name"] == task["name"])
                done = target["on"]
                label = f"{'[x]' if done else '[ ]'} {task['emoji']} {task['done_label'] if done else task['label']}"
                color = (150, 220, 150) if done else (200, 200, 210)
                txt = self.f_task.render(label, True, color)
                surface.blit(txt, (checklist_x + 10, checklist_y + 8 + i * 26))

            # Progress
            prog = f"{self.completed_count}/{len(TASKS)}"
            prog_txt = self.f_ui_bold.render(prog, True, CREAM)
            surface.blit(prog_txt, (checklist_x + 160, checklist_y + len(TASKS) * 26 - 14))

            # Bottom instruction
            if self.near_target:
                inst = "Press SPACE to interact"
            else:
                inst = "Walk to an item with WASD/arrows"
            hint = self.f_ui.render(inst, True, CREAM)
            surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 30))

        # Flash feedback for completed task
        if self.flash_timer > 0 and self.flash_text:
            alpha = min(255, int(self.flash_timer * 200))
            y_offset = (1.8 - self.flash_timer) * 30
            flash = self.f_flash.render(self.flash_text, True, GOLD)
            flash.set_alpha(alpha)
            surface.blit(flash, (self.w // 2 - flash.get_width() // 2, int(self.h * 0.35 - y_offset)))

    def _draw_phase_overlays(self, surface):
        if self.phase == "vandita_entering":
            # "She's here..." text
            if self.phase_timer > 0.8:
                alpha = min(255, int((self.phase_timer - 0.8) * 200))
                txt = self.f_sub.render("She's here...", True, CREAM)
                txt.set_alpha(alpha)
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.30))

        elif self.phase == "kneel":
            alpha = min(230, int(self.phase_timer * 150))
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(alpha * 0.3)))
            surface.blit(overlay, (0, 0))

            if self.phase_timer > 0.5:
                txt = self.f_mid.render("*gets down on one knee*", True, CREAM)
                txt.set_alpha(min(255, int((self.phase_timer - 0.5) * 200)))
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h * 0.25))

            if self.phase_timer > 1.5 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))

        elif self.phase == "propose":
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            surface.blit(overlay, (0, 0))

            # Ring
            ring_r = 22
            ring_surf = pygame.Surface((ring_r * 4, ring_r * 4), pygame.SRCALPHA)
            cx, cy = ring_r * 2, ring_r * 2
            pygame.draw.circle(ring_surf, GOLD, (cx, cy), ring_r, 4)
            pygame.draw.polygon(ring_surf, (240, 240, 255), [
                (cx, cy - ring_r - 7), (cx - 8, cy - ring_r + 5), (cx + 8, cy - ring_r + 5),
            ])
            surface.blit(ring_surf, (self.w // 2 - ring_surf.get_width() // 2, self.h // 2 - 130))

            msg = self.f_big.render("Will you marry me?", True, CREAM)
            surface.blit(msg, (self.w // 2 - msg.get_width() // 2, self.h // 2 - 30))

            if self.phase_timer > 1.5 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))

        elif self.phase == "yes":
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((*SOFT_PINK, min(140, int(self.phase_timer * 100))))
            surface.blit(overlay, (0, 0))

            if self.phase_timer > 0.3:
                txt = self.f_big.render("SHE SAID YES!", True, DARK_BROWN)
                # Bounce effect
                scale = 1.0 + max(0, 0.3 - (self.phase_timer - 0.3)) * 2
                scaled = pygame.transform.scale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
                surface.blit(scaled, (self.w // 2 - scaled.get_width() // 2, self.h // 2 - 60))

            if self.phase_timer > 1.0:
                sub = self.f_mid.render("Even though it was the sweatiest proposal speech", True, MID_BROWN)
                sub.set_alpha(min(255, int((self.phase_timer - 1.0) * 200)))
                surface.blit(sub, (self.w // 2 - sub.get_width() // 2, self.h // 2 + 10))

            if self.phase_timer > 1.5 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, MID_BROWN)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))

        elif self.phase == "crying":
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((*SOFT_PINK, min(180, int(self.phase_timer * 80) + 100)))
            surface.blit(overlay, (0, 0))

            # Tear drops animation
            for i in range(5):
                tear_x = self.w // 2 + int(math.sin(self.t * 1.5 + i * 1.3) * 80)
                tear_y = self.h // 2 - 40 + int((self.phase_timer * 30 + i * 20) % 100)
                tear_alpha = 200 - int((self.phase_timer * 30 + i * 20) % 100) * 2
                if tear_alpha > 0:
                    ts = pygame.Surface((8, 12), pygame.SRCALPHA)
                    pygame.draw.ellipse(ts, (180, 210, 240, tear_alpha), (0, 0, 8, 12))
                    surface.blit(ts, (tear_x, tear_y))

            txt1 = self.f_mid.render("*happy tears*", True, DARK_BROWN)
            surface.blit(txt1, (self.w // 2 - txt1.get_width() // 2, self.h // 2 - 60))

            if self.phase_timer > 1.0:
                txt2 = self.f_sub.render("This is just the beginning.", True, MID_BROWN)
                txt2.set_alpha(min(255, int((self.phase_timer - 1.0) * 200)))
                surface.blit(txt2, (self.w // 2 - txt2.get_width() // 2, self.h // 2))

            if self.phase_timer > 2.0 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key to continue", True, MID_BROWN)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))

        elif self.phase == "done":
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            alpha = min(255, int(self.phase_timer * 120))
            overlay.fill((0, 0, 0, int(alpha * 0.4)))
            surface.blit(overlay, (0, 0))

            if self.phase_timer > 0.5:
                txt = self.f_big.render("And they lived...", True, CREAM)
                txt.set_alpha(min(255, int((self.phase_timer - 0.5) * 150)))
                surface.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h // 2 - 30))

            if self.phase_timer > 2.0 and int(self.t * 2) % 2 == 0:
                tap = self.f_ui.render("Press any key", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h * 0.88))
