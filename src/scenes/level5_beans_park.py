"""
Level 5 — Beans at Harris Park (Medford, MA)
==========================================
Pseudo-3D endless runner (Temple Run / Subway Surfers–style depth cues):
three lanes converge to a vanishing point, scale & parallax by depth,
procedural difficulty ramp, lives, and ball-chase beats.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

import pygame

from src.utils.constants import (
    CREAM,
    HEART_RED,
    DARK_BROWN,
    MID_BROWN,
    SCENE_FINALE,
    GOLD,
    NOPE_RED,
    LIKE_GREEN,
    WHITE,
)
from src.utils.draw_helpers import draw_border_collie, draw_rounded_rect


# ── Perspective (behind-the-runner: lanes converge toward horizon) ─────────
LANE_COUNT = 3
LANE_SPREAD_BOTTOM = 118.0  # half-spacing between outer lanes at player row
GROUND_Y_FRAC = 0.78
HORIZON_Y_FRAC = 0.34
Z_MAX_DRAW = 1550.0  # world units: far clip (obstacles beyond appear at horizon)
Z_DEPTH_CURVE = 0.62  # <1 = stronger perspective squash toward horizon

# Physics — ~20% gentler than prior build (clearer, less chaos)
PACE = 0.80
GRAVITY = 2480.0
JUMP_V = -640.0
BASE_SCROLL_SPEED = 360.0 * PACE
MAX_SCROLL_SPEED = 640.0 * PACE
LANE_SWITCH_BASE = 7.5
LANE_SWITCH_MAX = 12.0

# Collision: only when obstacle is in this slice along the track (world z)
HIT_Z_MIN = 18.0
HIT_Z_MAX = 92.0

# Medford + “runner” track colors (Subway Surfers–style clarity)
PARK_NAME = "Harris Park"
PARK_SUB = "Park run"
TRACK_ASPHALT = (62, 68, 78)
TRACK_ASPHALT_DARK = (48, 52, 60)
TRACK_EDGE = (245, 248, 255)
RAIL_YELLOW = (255, 214, 48)
RAIL_YELLOW_DARK = (230, 170, 30)
GRASS_BRIGHT = (94, 168, 92)
GRASS_SHADOW = (72, 138, 72)
OUTLINE = (28, 32, 40)
HAZARD_TINT = (255, 92, 92)
PICKUP_GLOW = (255, 220, 120)


class ObsKind(Enum):
    PUDDLE = auto()
    DOG = auto()
    BENCH = auto()
    TREAT = auto()
    BALL = auto()
    CONE = auto()  # low profile — must jump or lane change


@dataclass
class Obstacle:
    kind: ObsKind
    lane: int
    world_x: float
    width: float = 72.0
    height: float = 48.0
    collected: bool = False
    hit: bool = False


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: Tuple[int, int, int]
    size: float


class Level5BeansPark:
    """
    Perspective runner: z = distance along track ahead of player (world_x - scroll).
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        self.vanish_x = screen_w * 0.5
        self.ground_y = screen_h * GROUND_Y_FRAC
        self.horizon_y = screen_h * HORIZON_Y_FRAC

        self.world_scroll = 0.0
        self.scroll_speed = BASE_SCROLL_SPEED

        self.lane = 1.0
        self.lane_target = 1

        self.on_ground = True
        self.jump_v = 0.0
        self.jump_y = 0.0

        self.distance_m = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.treats = 0
        self.lives = 3
        self.phase = "run"
        self.ball_chase_timer = 0.0
        self.ball_chase_duration = 6.2
        self.ball_world_x = 0.0
        self.ball_lane = 1.0
        self._ball_phase_started = False

        self.obstacles: List[Obstacle] = []
        self._spawn_cursor = 420.0
        self._rng = random.Random(42)
        self._pattern_cooldown = 0

        self.particles: List[Particle] = []
        self.screen_shake = 0.0
        self.hit_flash = 0.0

        self.win_distance_m = 320.0
        self.cleared = False
        self.clear_timer = 0.0
        self.fail_timer = 0.0
        self.failed = False

        # Tutorial stays until player clicks Start or presses Space/Enter
        self.tutorial_open = True
        self._tutorial_start_rect = pygame.Rect(screen_w // 2 - 150, screen_h - 118, 300, 54)

        self.f_hdr = pygame.font.SysFont("Georgia", 22, bold=True)
        self.f_sub = pygame.font.SysFont("Georgia", 16, italic=True)
        self.f_ui = pygame.font.SysFont("Arial", 18, bold=True)
        self.f_small = pygame.font.SysFont("Arial", 13, bold=True)
        self.f_big = pygame.font.SysFont("Georgia", 36, bold=True)
        self.f_goal = pygame.font.SysFont("Arial", 17, bold=True)
        self.f_tut_title = pygame.font.SysFont("Arial", 26, bold=True)
        self.f_tut = pygame.font.SysFont("Arial", 17, bold=True)
        self.f_legend = pygame.font.SysFont("Arial", 14, bold=True)

        self._build_initial_world()

    # --- difficulty 0..1 from distance + time --------------------------------
    def _difficulty(self) -> float:
        """0..1 ramp; scaled down ~20% so intensity rises more slowly."""
        d = self.distance_m / 500.0
        s = self.world_scroll / 12000.0
        raw = 0.22 + d * 0.44 + s * 0.28
        return max(0.0, min(1.0, raw * PACE))

    def _lane_switch_speed(self) -> float:
        return LANE_SWITCH_BASE + (LANE_SWITCH_MAX - LANE_SWITCH_BASE) * self._difficulty()

    # --- projection -----------------------------------------------------------
    def _z_ahead(self, ob: Obstacle) -> float:
        return ob.world_x - self.world_scroll

    def _depth_t(self, z: float) -> float:
        """t=0 at horizon, t=1 at player row."""
        t = 1.0 - (z / Z_MAX_DRAW)
        t = max(0.0, min(1.0, t))
        return t ** Z_DEPTH_CURVE

    def _lane_screen_x(self, lane: float, t: float) -> float:
        lane = max(0.0, min(2.0, lane))
        return self.vanish_x + (lane - 1.0) * LANE_SPREAD_BOTTOM * t

    def _ground_screen_y(self, t: float) -> float:
        return self.horizon_y + (self.ground_y - self.horizon_y) * t

    def _beans_screen(self) -> Tuple[float, float, float]:
        """Beans at full depth (t=1)."""
        t = 1.0
        bx = self._lane_screen_x(self.lane, t)
        by = self._beans_feet_y()
        return bx, by, t

    def _obstacle_screen(self, ob: Obstacle) -> Tuple[float, float, float, float]:
        """sx, sy_feet, depth_t, scale for drawing."""
        z = self._z_ahead(ob)
        t = self._depth_t(z)
        sx = self._lane_screen_x(float(ob.lane), t)
        sy = self._ground_screen_y(t)
        scale = 0.22 + 0.78 * (t ** 0.95)
        return sx, sy, t, scale

    def _beans_feet_y(self) -> float:
        return self.ground_y + self.jump_y

    # ------------------------------------------------------------------ world
    def _build_initial_world(self):
        x = self._spawn_cursor
        for _ in range(15):
            x = self._spawn_chunk(x)
        self._spawn_cursor = x

    def _spawn_chunk(self, start_x: float) -> float:
        diff = self._difficulty()
        # Wider gaps = easier to read what’s coming
        gap_min = 70 + (1.0 - diff) * 110
        gap_max = 135 + (1.0 - diff) * 145
        x = start_x + self._rng.uniform(gap_min, gap_max)

        if self.phase == "ball_chase":
            return x + 280

        roll = self._rng.random()

        # Fewer double-hazard packs (less chaos)
        if self._pattern_cooldown <= 0 and self._rng.random() < 0.09 + diff * 0.06:
            self._spawn_pattern_pack(x, diff)
            self._pattern_cooldown = self._rng.randint(3, 7)
            return x + 175 + diff * 50

        self._pattern_cooldown = max(0, self._pattern_cooldown - 1)

        hz = 0.06 + diff * 0.10
        if roll < 0.18 + hz:
            kind = ObsKind.PUDDLE
        elif roll < 0.35 + hz:
            kind = ObsKind.DOG
        elif roll < 0.48 + hz:
            kind = ObsKind.BENCH
        elif roll < 0.54 + diff * 0.06:
            kind = ObsKind.CONE
        elif roll < 0.72:
            kind = ObsKind.TREAT
        else:
            return x + self._rng.uniform(130 + (1 - diff) * 100, 240)

        lane = self._pick_lane_biased(diff)
        w, h = 72, 44
        if kind == ObsKind.BENCH:
            w, h = 88, 38
        if kind == ObsKind.CONE:
            w, h = 36, 52
        self.obstacles.append(Obstacle(kind=kind, lane=lane, world_x=x, width=w, height=h))
        return x + 95 + (1.0 - diff) * 35

    def _pick_lane_biased(self, diff: float) -> int:
        if self._rng.random() < 0.22 + diff * 0.18:
            return self._rng.choice([0, 2])
        return self._rng.randint(0, 2)

    def _spawn_pattern_pack(self, x: float, diff: float):
        """Tight sequences — spaced farther apart than before."""
        lanes = [0, 1, 2]
        self._rng.shuffle(lanes)
        a, b = lanes[0], lanes[1]
        if self._rng.random() < 0.5:
            self.obstacles.append(Obstacle(ObsKind.PUDDLE, a, x, 72, 40))
            self.obstacles.append(
                Obstacle(ObsKind.DOG, b, x + 118 + diff * 18, 56, 42)
            )
        else:
            self.obstacles.append(Obstacle(ObsKind.CONE, a, x, 36, 52))
            self.obstacles.append(
                Obstacle(ObsKind.BENCH, b, x + 110 + diff * 22, 88, 38)
            )

    def _spawn_ball_chase_event(self):
        ahead = self.world_scroll + self.w + 260
        self.ball_world_x = ahead
        self.ball_lane = float(self.lane_target)
        self.phase = "ball_chase"
        self.ball_chase_timer = 0.0
        self._ball_phase_started = True
        self.obstacles.append(
            Obstacle(ObsKind.BALL, int(round(self.ball_lane)), ahead, 44, 38)
        )

    # ----------------------------------------------------------------- events
    def handle_event(self, event: pygame.event.Event):
        if self.cleared and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.next_scene = SCENE_FINALE
            return
        if self.failed and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._reset_run()
            return

        if self.tutorial_open:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                self.tutorial_open = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._tutorial_start_rect.collidepoint(event.pos):
                    self.tutorial_open = False
                return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.lane_target = max(0, self.lane_target - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.lane_target = min(LANE_COUNT - 1, self.lane_target + 1)
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.on_ground:
                    self.jump_v = JUMP_V
                    self.on_ground = False
                    from src.utils.sounds import get_sfx
                    get_sfx().jump.play()

    # ----------------------------------------------------------------- update
    def update(self, dt: float):
        if self.cleared:
            self.clear_timer += dt
            if self.clear_timer > 8.0 and self.next_scene is None:
                self.next_scene = SCENE_FINALE
            return
        if self.failed:
            self.fail_timer += dt
            return

        if self.tutorial_open:
            return

        diff = self._difficulty()
        lsp = self._lane_switch_speed()
        if self.lane < self.lane_target:
            self.lane = min(self.lane_target, self.lane + lsp * dt)
        elif self.lane > self.lane_target:
            self.lane = max(self.lane_target, self.lane - lsp * dt)

        if not self.on_ground:
            self.jump_v += GRAVITY * dt
            self.jump_y += self.jump_v * dt
            if self.jump_y >= 0:
                self.jump_y = 0.0
                self.jump_v = 0.0
                self.on_ground = True

        # Speed ramp (gentler — ~20% less pressure vs old tuning)
        tscroll = self.world_scroll / 7200.0
        self.scroll_speed = min(
            MAX_SCROLL_SPEED,
            BASE_SCROLL_SPEED + tscroll * 76 * PACE + diff * 44 * PACE,
        )
        self.world_scroll += self.scroll_speed * dt
        self.distance_m += self.scroll_speed * dt * 0.012

        if self.phase == "ball_chase":
            self.ball_chase_timer += dt
            self.ball_world_x += self.scroll_speed * 1.08 * dt
            wave = math.sin(self.ball_chase_timer * 3.4) * 0.1
            self.ball_lane = max(0.0, min(2.0, 1.0 + wave))
            for ob in self.obstacles:
                if ob.kind == ObsKind.BALL:
                    ob.world_x = self.ball_world_x
                    ob.lane = int(round(self.ball_lane))
                    break
            if self.ball_chase_timer >= self.ball_chase_duration:
                self.phase = "run"
                self.score += 200 + int(self.combo * 1.5)
                self.combo = min(self.combo + 2, 99)
                bx, _, _ = self._beans_screen()
                self._spawn_particles(bx, self._beans_feet_y() - 40, 28, HEART_RED)
                self._ball_phase_started = False
                self.obstacles = [o for o in self.obstacles if o.kind != ObsKind.BALL]

        while self._spawn_cursor < self.world_scroll + self.w + 1100:
            self._spawn_cursor = self._spawn_chunk(self._spawn_cursor)

        if (
            self.phase == "run"
            and not self._ball_phase_started
            and 92 < self.distance_m < 118
        ):
            self._spawn_ball_chase_event()

        self._collisions()
        self._cull_obstacles()

        if not self.cleared and self.distance_m >= self.win_distance_m:
            self.cleared = True
            self.clear_timer = 0.0
            self.score += 250 + self.treats * 18 + int(self.max_combo * 5)
            from src.utils.sounds import get_sfx
            get_sfx().celebrate.play()

        new_p: List[Particle] = []
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt * 1.85
            p.vy += 440 * dt
            if p.life > 0:
                new_p.append(p)
        self.particles = new_p

        if self.screen_shake > 0:
            self.screen_shake -= dt * 4.2
        if self.hit_flash > 0:
            self.hit_flash -= dt * 2.2
    def _cull_obstacles(self):
        """Drop passed obstacles to keep list small."""
        keep: List[Obstacle] = []
        for ob in self.obstacles:
            z = self._z_ahead(ob)
            if ob.kind == ObsKind.BALL:
                keep.append(ob)
                continue
            if z > -220:
                keep.append(ob)
        self.obstacles = keep

    def _collisions(self):
        bx, _, _ = self._beans_screen()
        feet_y = self._beans_feet_y()
        hit_w, hit_h = 52, 80
        hitbox = pygame.Rect(int(bx - hit_w // 2), int(feet_y - hit_h), hit_w, hit_h)

        for ob in self.obstacles:
            if ob.hit or ob.collected:
                continue
            z = self._z_ahead(ob)
            if z < HIT_Z_MIN or z > HIT_Z_MAX:
                continue

            _, _, _, sc = self._obstacle_screen(ob)
            sx = self._lane_screen_x(float(ob.lane), 1.0)
            sy = self._ground_screen_y(1.0)
            # Scale hitbox at collision plane
            hw = int(ob.width * 0.85 * sc)
            hh = int(ob.height * 0.9 * sc)

            if ob.kind == ObsKind.TREAT:
                ty = sy - int(26 * sc)
                rect = pygame.Rect(int(sx - 18 * sc), int(ty - 12 * sc), int(36 * sc), int(34 * sc))
                if hitbox.colliderect(rect):
                    ob.collected = True
                    self.treats += 1
                    self.score += 28 + self.combo * 3
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    self._spawn_particles(bx, feet_y - 50, 8, GOLD)
                    from src.utils.sounds import get_sfx
                    get_sfx().pickup.play()
                continue

            if ob.kind == ObsKind.BALL:
                if self.phase != "ball_chase":
                    continue
                rect = pygame.Rect(int(sx - 22 * sc), int(sy - 48 * sc), int(44 * sc), int(42 * sc))
                if hitbox.colliderect(rect):
                    ob.collected = True
                    self.score += 150 + int(self.combo * 2)
                    self._spawn_particles(bx, feet_y - 45, 22, HEART_RED)
                continue

            rect = pygame.Rect(int(sx - hw // 2), int(sy - hh), hw, hh)

            if not hitbox.colliderect(rect):
                continue

            if ob.kind == ObsKind.PUDDLE:
                if self.on_ground and self.jump_y >= -6:
                    ob.hit = True
                    self._hurt("slip")
            elif ob.kind == ObsKind.DOG:
                if int(round(self.lane)) == ob.lane and self.jump_y > -38:
                    ob.hit = True
                    self._hurt("dog")
                elif int(round(self.lane)) == ob.lane and self.jump_y <= -38:
                    self.score += 15
            elif ob.kind == ObsKind.BENCH:
                if self.jump_y > -48:
                    ob.hit = True
                    self._hurt("bench")
            elif ob.kind == ObsKind.CONE:
                if int(round(self.lane)) == ob.lane and self.jump_y > -22:
                    ob.hit = True
                    self._hurt("cone")

    def _hurt(self, reason: str):
        from src.utils.sounds import get_sfx
        get_sfx().hit.play()
        self.combo = 0
        self.hit_flash = 0.42
        self.screen_shake = 0.20
        self.score = max(0, self.score - 55)
        self.lives -= 1
        bx, _, _ = self._beans_screen()
        self._spawn_particles(bx, self._beans_feet_y() - 30, 14, NOPE_RED)
        if self.lives <= 0:
            self.failed = True
            self.fail_timer = 0.0

    def _spawn_particles(self, x: float, y: float, n: int, color: Tuple[int, int, int]):
        for _ in range(n):
            self.particles.append(
                Particle(
                    x=x + random.uniform(-22, 22),
                    y=y + random.uniform(-12, 12),
                    vx=random.uniform(-150, 150),
                    vy=random.uniform(-260, -90),
                    life=random.uniform(0.35, 0.85),
                    color=color,
                    size=random.uniform(3, 9),
                )
            )

    def _reset_run(self):
        self.failed = False
        self.fail_timer = 0.0
        self.world_scroll = 0.0
        self.lane = 1.0
        self.lane_target = 1
        self.jump_y = 0.0
        self.jump_v = 0.0
        self.on_ground = True
        self.obstacles.clear()
        self._spawn_cursor = 420.0
        self._rng = random.Random(42)
        self._pattern_cooldown = 0
        self._build_initial_world()
        self.phase = "run"
        self._ball_phase_started = False
        self.distance_m = 0.0
        self.score = 0
        self.combo = 0
        self.treats = 0
        self.lives = 3
        self.max_combo = 0
        self.tutorial_open = False

    # --------------------------------------------------------------------- draw
    @staticmethod
    def _stroke_ellipse(surf, rect, fill, stroke, width=2):
        pygame.draw.ellipse(surf, fill, rect)
        pygame.draw.ellipse(surf, stroke, rect, max(1, width))

    @staticmethod
    def _stroke_circle(surf, pos, r, fill, stroke, width=2):
        pygame.draw.circle(surf, fill, pos, r)
        pygame.draw.circle(surf, stroke, pos, r, max(1, width))

    def draw(self, surface: pygame.Surface):
        shake_x = int((random.random() - 0.5) * 14 * min(1, self.screen_shake * 5))
        shake_y = int((random.random() - 0.5) * 14 * min(1, self.screen_shake * 5))

        # Sky — vivid cyan → warm (mobile-runner pop)
        for y in range(self.h):
            t = y / self.h
            r = int(120 + (220 - 120) * t * 0.85)
            g = int(205 + (245 - 205) * t * 0.5)
            b = int(255 - t * 35)
            surface.fill((r, g, b), pygame.Rect(0, y, self.w, 1))

        # Horizon haze / air perspective
        haze = pygame.Surface((self.w, int(self.h * 0.48)), pygame.SRCALPHA)
        for yy in range(haze.get_height()):
            a = int(28 * (1 - yy / max(1, haze.get_height())))
            pygame.draw.line(haze, (255, 255, 255, a), (0, yy), (self.w, yy))
        surface.blit(haze, (0, 0))

        t_anim = pygame.time.get_ticks() * 0.00012
        for layer, speed, col in [(0.07, 0.2, (55, 125, 175)), (0.1, 0.14, (40, 110, 155))]:
            for i in range(-1, 7):
                bx = int(i * 200 - (self.world_scroll * speed) % 200 + shake_x)
                by = int(self.horizon_y - 24 + math.sin(t_anim + i) * 4 + shake_y)
                pygame.draw.rect(
                    surface,
                    col,
                    pygame.Rect(bx, by, 145, 168),
                    border_radius=6,
                )

        # Mystic river band
        river_y = int(self.h * 0.388)
        pygame.draw.rect(surface, (72, 130, 195), pygame.Rect(0, river_y, self.w, 36))
        pygame.draw.rect(surface, (110, 175, 230), pygame.Rect(0, river_y, self.w, 4))
        for wx in range(-int(self.world_scroll * 0.4) % 64, self.w + 64, 64):
            pygame.draw.line(
                surface, (190, 225, 255), (wx, river_y + 8), (wx + 32, river_y + 28), 2
            )

        gy = int(self.ground_y)
        hy = int(self.horizon_y)
        cx = int(self.vanish_x + shake_x)

        # Grass sides (cartoon bright)
        path_left = [(0, self.h), (cx - 300, gy + 2), (cx - 48, hy), (0, hy + 6)]
        path_right = [(self.w, self.h), (cx + 300, gy + 2), (cx + 48, hy), (self.w, hy + 6)]
        pygame.draw.polygon(surface, GRASS_BRIGHT, path_left)
        pygame.draw.polygon(surface, GRASS_SHADOW, path_left, 2)
        pygame.draw.polygon(surface, GRASS_BRIGHT, path_right)
        pygame.draw.polygon(surface, GRASS_SHADOW, path_right, 2)

        # Asphalt runway (3 lanes)
        mid_pts = [
            (cx - 220, gy + 12),
            (cx - 32, hy + 6),
            (cx + 32, hy + 6),
            (cx + 220, gy + 12),
        ]
        pygame.draw.polygon(surface, TRACK_ASPHALT, mid_pts)
        pygame.draw.polygon(surface, OUTLINE, mid_pts, 3)

        # White outer rails (Subway-style borders)
        for sign in (-1, 1):
            o1 = (cx + sign * (220 + 8), gy + 12)
            o2 = (cx + sign * 40, hy + 8)
            pygame.draw.line(surface, TRACK_EDGE, o1, o2, 5)
            pygame.draw.line(surface, OUTLINE, o1, o2, 2)

        # Lane dividers — single crisp line each (less visual noise)
        for lane_i in range(4):
            lx = cx + (lane_i - 1.5) * LANE_SPREAD_BOTTOM
            pygame.draw.line(
                surface,
                RAIL_YELLOW,
                (int(lx), gy + 5 + shake_y),
                (cx, hy + 18 + shake_y),
                2,
            )

        # Center-lane motion streaks (fewer lines = calmer)
        scroll_phase = (self.world_scroll * 1.1) % 100
        for i in range(-1, 9):
            z0 = i * 100 + scroll_phase
            z1 = z0 + 42
            t0 = self._depth_t(z0)
            t1 = self._depth_t(z1)
            if t0 <= 0.03 or t1 <= 0.03:
                continue
            y0 = self._ground_screen_y(t0)
            y1 = self._ground_screen_y(t1)
            x0l = self._lane_screen_x(1.0, t0)
            x1l = self._lane_screen_x(1.0, t1)
            pygame.draw.line(surface, RAIL_YELLOW_DARK, (int(x0l), int(y0)), (int(x1l), int(y1)), max(1, int(3 * t0)))

        # Horizon fence (simplified)
        fy = hy + 12
        for fx in range(-40, self.w + 60, 28):
            pygame.draw.rect(surface, (95, 70, 45), (fx + shake_x, fy + shake_y, 8, 26), border_radius=2)
            pygame.draw.rect(surface, OUTLINE, (fx + shake_x, fy + shake_y, 8, 26), 1, border_radius=2)
        pygame.draw.line(surface, (255, 200, 90), (0, fy + 3), (self.w, fy + 3), 3)

        # Obstacles: back-to-front (far z first)
        sorted_obs = sorted(self.obstacles, key=lambda o: -self._z_ahead(o))

        def draw_ob(ob: Obstacle):
            if ob.collected and ob.kind != ObsKind.BALL:
                return
            z = self._z_ahead(ob)
            if z > Z_MAX_DRAW + 200 or z < 12:
                return
            sx, sy, t, sc = self._obstacle_screen(ob)
            sx += shake_x
            sy += shake_y
            sh = int(ob.height * sc)
            sw = int(ob.width * sc)

            # Contact shadow
            shadow_y = sy + 4
            pygame.draw.ellipse(
                surface,
                (22, 26, 32),
                pygame.Rect(int(sx - sw * 0.55), int(shadow_y - 6 * sc), int(sw * 1.1), int(14 * sc)),
            )

            ol = max(2, int(3 * sc))

            if ob.kind == ObsKind.PUDDLE:
                pr = pygame.Rect(int(sx - sw // 2), int(sy - 8 * sc), sw, int(22 * sc))
                self._stroke_ellipse(surface, pr, (90, 170, 255), OUTLINE, ol)
                # gloss
                gr = pr.inflate(-int(8 * sc), -int(4 * sc))
                gr.move_ip(0, -int(2 * sc))
                pygame.draw.ellipse(surface, (200, 235, 255), gr)
            elif ob.kind == ObsKind.DOG:
                body = pygame.Rect(int(sx - sw // 2), int(sy - sh), sw, int(36 * sc))
                pygame.draw.ellipse(surface, (155, 105, 75), body)
                pygame.draw.ellipse(surface, OUTLINE, body, ol)
                self._stroke_circle(
                    surface,
                    (int(sx - 8 * sc), int(sy - sh + 12 * sc)),
                    int(10 * sc),
                    (175, 130, 100),
                    OUTLINE,
                    max(1, ol - 1),
                )
                self._stroke_circle(
                    surface,
                    (int(sx + 8 * sc), int(sy - sh + 12 * sc)),
                    int(10 * sc),
                    (175, 130, 100),
                    OUTLINE,
                    max(1, ol - 1),
                )
                self._stroke_circle(
                    surface,
                    (int(sx), int(sy - sh + 22 * sc)),
                    int(8 * sc),
                    (95, 70, 55),
                    OUTLINE,
                    max(1, ol - 1),
                )
            elif ob.kind == ObsKind.BENCH:
                r1 = pygame.Rect(int(sx - sw // 2), int(sy - sh), sw, int(20 * sc))
                pygame.draw.rect(surface, (125, 95, 65), r1, border_radius=max(2, int(4 * sc)))
                pygame.draw.rect(surface, OUTLINE, r1, ol, border_radius=max(2, int(4 * sc)))
                r2 = pygame.Rect(int(sx - sw // 2 + 2), int(sy - 6 * sc), sw - 4, int(8 * sc))
                pygame.draw.rect(surface, (95, 70, 50), r2, border_radius=2)
            elif ob.kind == ObsKind.CONE:
                pts = [
                    (sx, sy - sh),
                    (sx - sw // 2, sy),
                    (sx + sw // 2, sy),
                ]
                pygame.draw.polygon(surface, (255, 135, 45), pts)
                pygame.draw.polygon(surface, OUTLINE, pts, ol)
                pygame.draw.line(surface, (255, 220, 200), (sx, sy - sh), (sx, sy - int(8 * sc)), 2)
            elif ob.kind == ObsKind.TREAT:
                tx, ty = int(sx), int(sy - sh + 12 * sc)
                tr = int(12 * sc)
                # glow ring
                pygame.draw.circle(surface, PICKUP_GLOW, (tx, ty), tr + 4)
                self._stroke_circle(surface, (tx, ty), tr, (255, 190, 95), OUTLINE, ol)
                pygame.draw.circle(surface, (255, 235, 160), (tx - tr // 3, ty - tr // 3), max(2, tr // 4))
            elif ob.kind == ObsKind.BALL:
                if ob.collected:
                    return
                tx, ty = int(sx), int(sy - sh + 14 * sc)
                tr = int(12 * sc)
                self._stroke_circle(surface, (tx, ty), tr, (255, 245, 160), OUTLINE, ol)
                pygame.draw.circle(surface, (80, 200, 90), (tx - tr // 3, ty - tr // 3), max(2, tr // 3))
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (int(sx - 8 * sc), int(sy - sh + 10 * sc)),
                    (int(sx + 8 * sc), int(sy - sh + 18 * sc)),
                    2,
                )

        for ob in sorted_obs:
            draw_ob(ob)

        # Beans (always near camera)
        bx, _, _ = self._beans_screen()
        bx += shake_x
        by = int(self._beans_feet_y() + shake_y)
        bounce = int(math.sin(pygame.time.get_ticks() * 0.014) * 5)
        draw_border_collie(
            surface,
            bx,
            by + bounce,
            scale=1.08,
            happy=not self.failed,
            tongue=True,
            pose="run",
            pose_elapsed_ms=float(pygame.time.get_ticks()),
        )

        # HUD — goal-first
        card = pygame.Rect(12, 8, self.w - 24, 86)
        draw_rounded_rect(surface, (255, 252, 245), card, radius=16, shadow=True, shadow_offset=3)
        pygame.draw.rect(surface, OUTLINE, card, 2, border_radius=16)

        goal_line = self.f_goal.render(
            f"GOAL: Reach {self.win_distance_m:.0f} m  (finish line)   ·   You have {self.lives} lives",
            True,
            (25, 45, 80),
        )
        surface.blit(goal_line, (24, 14))

        hdr = self.f_hdr.render(f"Chapter 6  ·  Beans at {PARK_NAME}", True, DARK_BROWN)
        surface.blit(hdr, (24, 38))

        ui = self.f_ui.render(
            f"{self.distance_m:.0f} m   ·   Score {self.score}   ·   Treats {self.treats}   ·   Combo ×{self.combo}",
            True,
            DARK_BROWN,
        )
        surface.blit(ui, (24, 62))

        hx = self.w - 130
        hf = pygame.font.SysFont("Arial", 24, bold=True)
        for i in range(3):
            col = HEART_RED if i < self.lives else (210, 200, 200)
            surface.blit(hf.render("♥", True, col), (hx + i * 36, 22))

        diff_pct = int(self._difficulty() * 100)
        dtxt = self.f_small.render(f"Pace {diff_pct}% (rises slowly)", True, (90, 70, 50))
        surface.blit(dtxt, (self.w - 130, 58))

        # Bottom legend — 3 lines: buttons, treats/ball, hearts
        leg_h = 58
        leg_y = self.h - leg_h
        pygame.draw.rect(surface, (252, 250, 245), (0, leg_y, self.w, leg_h))
        pygame.draw.line(surface, OUTLINE, (0, leg_y), (self.w, leg_y), 2)

        fs = pygame.font.SysFont("Arial", 13, bold=True)
        row_a = fs.render(
            "MOVE:  ← or A = left lane   ·   → or D = right lane      "
            "|      JUMP:  Space  or  ↑  or  W   (over hazards)",
            True,
            DARK_BROWN,
        )
        surface.blit(row_a, (10, leg_y + 5))
        col_pick = (180, 110, 0)
        col_ball = (22, 120, 55)
        row_b = fs.render(
            "TREATS (gold):  no extra button — steer into the treat’s lane; it collects when Beans touches it.     ",
            True,
            col_pick,
        )
        surface.blit(row_b, (10, leg_y + 22))
        row_c = fs.render(
            "BALL (FETCH):  same idea — move into the ball’s lane so Beans touches it.     ♥ = lives left",
            True,
            col_ball,
        )
        surface.blit(row_c, (10, leg_y + 38))

        if self.phase == "ball_chase":
            pygame.draw.rect(surface, (255, 240, 120), (self.w // 2 - 280, 96, 560, 40), border_radius=8)
            pygame.draw.rect(surface, OUTLINE, (self.w // 2 - 280, 96, 560, 40), 2, border_radius=8)
            banner = self.f_ui.render(
                "FETCH —  steer into the ball’s lane so Beans touches it (same as treats)",
                True,
                (120, 40, 20),
            )
            surface.blit(banner, (self.w // 2 - banner.get_width() // 2, 104))

        # Full-screen how-to — stays until Start / Space / Enter
        if self.tutorial_open:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((15, 25, 45, 210))
            surface.blit(overlay, (0, 0))

            panel = pygame.Rect(self.w // 2 - 400, 28, 800, 560)
            draw_rounded_rect(surface, (255, 252, 248), panel, radius=20, shadow=True, shadow_offset=6)
            pygame.draw.rect(surface, OUTLINE, panel, 3, border_radius=20)

            title = self.f_tut_title.render("HOW TO PLAY", True, (30, 50, 120))
            surface.blit(title, (self.w // 2 - title.get_width() // 2, 44))

            lines = [
                "Beans runs forward automatically. Things come toward you on three lanes.",
                "",
                "— BUTTONS (only these do anything) —",
                "    ←  or  A          =  move one lane left",
                "    →  or  D          =  move one lane right",
                "    Space  or  ↑  or  W  =  jump (use over hazards when needed)",
                "    There is NO “pick up” or “grab” key.",
                "",
                "— GOLD TREATS —",
                "    Use ← A / → D so Beans is in the SAME lane as the treat.",
                "    When it reaches you, it collects by itself (touch = auto pickup).",
                "",
                "— RED / ORANGE HAZARDS —",
                "    Don’t let Beans hit them: jump and/or change lanes.",
                "    Puddles & benches: usually JUMP. Dogs & cones: lane change OR jump.",
                "",
                "— TENNIS BALL (FETCH) —",
                "    Same as treats: move into the ball’s lane so Beans touches it.",
                "",
                f"— GOAL —  Reach {self.win_distance_m:.0f} m.  Hearts = mistakes left.",
                "",
                "When you’re ready, press the green button (or Space / Enter).",
            ]
            y = 88
            for line in lines:
                col = (35, 38, 45)
                if line.startswith("—"):
                    col = (90, 50, 140)
                elif "NO " in line and "grab" in line:
                    col = (160, 70, 40)
                surf = self.f_tut.render(line, True, col)
                surface.blit(surf, (panel.x + 24, y))
                y += 24

            btn_w, btn_h = 300, 54
            self._tutorial_start_rect = pygame.Rect(self.w // 2 - btn_w // 2, self.h - 118, btn_w, btn_h)
            br = self._tutorial_start_rect
            pygame.draw.rect(surface, LIKE_GREEN, br, border_radius=12)
            pygame.draw.rect(surface, OUTLINE, br, 3, border_radius=12)
            lbl = self.f_tut_title.render("Start run", True, WHITE)
            surface.blit(lbl, (br.centerx - lbl.get_width() // 2, br.centery - lbl.get_height() // 2))
            sub = self.f_small.render("or Space / Enter  ·  take your time reading above", True, (35, 80, 40))
            surface.blit(sub, (self.w // 2 - sub.get_width() // 2, br.bottom + 10))

        for p in self.particles:
            s = int(p.size * p.life)
            if s < 1:
                continue
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), s)

        if self.hit_flash > 0:
            ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            ov.fill((255, 190, 190, int(90 * self.hit_flash)))
            surface.blit(ov, (0, 0))

        if self.cleared:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            surface.blit(overlay, (0, 0))
            msg = self.f_big.render("Good girl, Beans! 💖", True, CREAM)
            surface.blit(msg, (self.w // 2 - msg.get_width() // 2, self.h // 2 - 52))
            s2 = self.f_sub.render(
                f"Lap clear · {self.treats} treats · best combo x{self.max_combo} · lives left {self.lives}",
                True,
                CREAM,
            )
            surface.blit(s2, (self.w // 2 - s2.get_width() // 2, self.h // 2 + 2))
            tap = self.f_ui.render("Press any key to continue", True, CREAM)
            if int(self.clear_timer * 2) % 2 == 0:
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h // 2 + 42))

        if self.failed:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((35, 0, 0, 190))
            surface.blit(overlay, (0, 0))
            m = self.f_big.render("Out of hearts — try again?", True, CREAM)
            surface.blit(m, (self.w // 2 - m.get_width() // 2, self.h // 2 - 28))
            t = self.f_ui.render("Press any key to retry", True, CREAM)
            surface.blit(t, (self.w // 2 - t.get_width() // 2, self.h // 2 + 22))

