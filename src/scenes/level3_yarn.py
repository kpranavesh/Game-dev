"""
Level 3: Yarn Crisis
=====================
Catch falling yarn balls before Beans steals them!
3 waves of increasing speed. Click to catch.
"""
import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import draw_border_collie, draw_vandita

YARN_COLORS = [
    (220, 130, 155),   # rose pink
    (130, 175, 220),   # soft blue
    (220, 195, 100),   # warm yellow
    (155, 200, 155),   # sage green
    (200, 155, 210),   # lavender
]

WAVES = [
    {"count": 10, "need": 6,  "speed_range": (80,  140), "interval": 1.2},
    {"count": 14, "need": 9,  "speed_range": (110, 175), "interval": 0.95},
    {"count": 18, "need": 10, "speed_range": (140, 210), "interval": 0.75},
]

BALL_R = 18


class YarnBall:
    def __init__(self, x: float, speed: float, color: tuple):
        self.x      = float(x)
        self.y      = float(-BALL_R)
        self.speed  = speed
        self.color  = color
        self.r      = BALL_R
        self.caught = False
        self.stolen = False
        # Gentle side wobble so they drift slightly
        self._phase = random.uniform(0, math.pi * 2)
        self._amp   = random.uniform(10, 22)
        self._freq  = random.uniform(1.1, 2.0)
        self._base_x = float(x)
        self._t     = 0.0

    def update(self, dt: float):
        self._t  += dt
        self.y   += self.speed * dt
        self.x    = self._base_x + math.sin(self._t * self._freq + self._phase) * self._amp

    @property
    def alive(self) -> bool:
        return not self.caught and not self.stolen


class Level3Yarn:
    INTRO       = "intro"
    PLAYING     = "playing"
    ROUND_OK    = "round_ok"
    ROUND_FAIL  = "round_fail"
    LEVEL_CLEAR = "level_clear"

    INTRO_DUR      = 2.2
    ROUND_OK_DUR   = 1.8
    ROUND_FAIL_DUR = 1.8

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        self.t            = 0.0
        self.state        = self.INTRO
        self.intro_timer  = 0.0
        self.wave_idx     = 0

        # Wave state
        self.balls: list[YarnBall] = []
        self.spawned     = 0
        self.caught      = 0
        self.stolen      = 0
        self.spawn_timer = 0.0

        # Feedback
        self.fb_timer    = 0.0
        self.clear_timer = 0.0
        self.clear_alpha = 0

        # Beans
        self.beans_x     = float(screen_w // 2)
        self.beans_dir   = 1    # 1=right, -1=left
        self.beans_speed = 110.0

        # Click pop flashes
        self.flashes: list[dict] = []

        # Floor where stolen balls land
        self.floor_y = screen_h - 95

        # Vandita sits at top center
        self.vandita_cy = 195

        # Fonts
        self.f_title = pygame.font.SysFont("Georgia", 46, bold=True)
        self.f_sub   = pygame.font.SysFont("Georgia", 22, italic=True)
        self.f_hint  = pygame.font.SysFont("Arial", 20)
        self.f_hdr   = pygame.font.SysFont("Georgia", 20)
        self.f_big   = pygame.font.SysFont("Georgia", 52, bold=True)
        self.f_score = pygame.font.SysFont("Georgia", 24, bold=True)
        self.f_cmd   = pygame.font.SysFont("Georgia", 28, bold=True)
        self.f_btn   = pygame.font.SysFont("Georgia", 17, bold=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def wave(self) -> dict:
        return WAVES[self.wave_idx]

    def _start_wave(self):
        self.state       = self.PLAYING
        self.balls       = []
        self.spawned     = 0
        self.caught      = 0
        self.stolen      = 0
        self.spawn_timer = 0.0
        self.beans_speed = 110.0

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if self.state == self.PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Catch the first ball the click hits
                for ball in self.balls:
                    if ball.alive:
                        if math.hypot(ball.x - mx, ball.y - my) <= ball.r + 10:
                            ball.caught = True
                            self.caught += 1
                            from src.utils.sounds import get_sfx
                            get_sfx().pop.play()
                            self.flashes.append({
                                "x": ball.x, "y": ball.y,
                                "timer": 0.45, "color": ball.color,
                            })
                            break

        elif self.state == self.LEVEL_CLEAR:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.next_scene = SCENE_LEVEL5

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self.t += dt

        # Flashes
        for f in self.flashes:
            f["timer"] -= dt
        self.flashes = [f for f in self.flashes if f["timer"] > 0]

        if self.state == self.INTRO:
            self.intro_timer += dt
            if self.intro_timer >= self.INTRO_DUR:
                self._start_wave()

        elif self.state == self.PLAYING:
            w = self.wave
            # Spawn
            if self.spawned < w["count"]:
                self.spawn_timer += dt
                if self.spawn_timer >= w["interval"]:
                    self.spawn_timer = 0.0
                    x     = random.randint(60, self.w - 60)
                    speed = random.uniform(*w["speed_range"])
                    color = random.choice(YARN_COLORS)
                    self.balls.append(YarnBall(x, speed, color))
                    self.spawned += 1

            # Update balls
            for ball in self.balls:
                if ball.alive:
                    ball.update(dt)
                    if ball.y >= self.floor_y:
                        ball.stolen = True
                        self.stolen += 1
                        from src.utils.sounds import get_sfx
                        get_sfx().woof.play()

            # Beans AI: target nearest ball near floor, else patrol
            targets = [b for b in self.balls if b.alive and b.y > self.floor_y - 160]
            if targets:
                target_x = min(targets, key=lambda b: abs(b.x - self.beans_x)).x
                if self.beans_x < target_x - 5:
                    self.beans_x  += self.beans_speed * dt
                    self.beans_dir = 1
                elif self.beans_x > target_x + 5:
                    self.beans_x  -= self.beans_speed * dt
                    self.beans_dir = -1
            else:
                self.beans_x += self.beans_dir * self.beans_speed * dt
                if self.beans_x > self.w - 60:
                    self.beans_dir = -1
                elif self.beans_x < 60:
                    self.beans_dir = 1
            self.beans_x = max(40.0, min(float(self.w - 40), self.beans_x))

            # Beans speeds up as wave goes on
            self.beans_speed = min(240, self.beans_speed + dt * 15)

            # Wave end check
            live = [b for b in self.balls if b.alive]
            if self.spawned >= w["count"] and not live:
                from src.utils.sounds import get_sfx
                if self.caught >= w["need"]:
                    self.state    = self.ROUND_OK
                    self.fb_timer = 0.0
                    get_sfx().success.play()
                else:
                    self.state    = self.ROUND_FAIL
                    self.fb_timer = 0.0
                    get_sfx().fail.play()

        elif self.state == self.ROUND_OK:
            self.fb_timer += dt
            if self.fb_timer >= self.ROUND_OK_DUR:
                self.wave_idx += 1
                if self.wave_idx >= len(WAVES):
                    self.state       = self.LEVEL_CLEAR
                    self.clear_timer = 0.0
                else:
                    self._start_wave()

        elif self.state == self.ROUND_FAIL:
            self.fb_timer += dt
            if self.fb_timer >= self.ROUND_FAIL_DUR:
                self._start_wave()   # retry same wave

        elif self.state == self.LEVEL_CLEAR:
            self.clear_timer += dt
            if self.clear_timer < 0.1:
                from src.utils.sounds import get_sfx
                get_sfx().celebrate.play()
            self.clear_alpha  = min(255, int(self.clear_timer * 130))
            if self.clear_timer >= 3.0:
                self.next_scene = SCENE_LEVEL5

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface):
        # Warm cream background
        for y in range(self.h):
            frac = y / self.h
            r = int(CREAM[0] * (1 - frac) + 215 * frac)
            g = int(CREAM[1] * (1 - frac) + 198 * frac)
            b = int(CREAM[2] * (1 - frac) + 178 * frac)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Floor strip
        pygame.draw.rect(surface, SOFT_GREEN,
                         pygame.Rect(0, self.floor_y, self.w, self.h - self.floor_y))
        pygame.draw.rect(surface, LEAF_GREEN,
                         pygame.Rect(0, self.floor_y, self.w, 4))

        # Header
        hdr = self.f_hdr.render("Chapter 5  ·  Yarn Crisis", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2, 14))

        # Wave progress dots
        for i in range(len(WAVES)):
            dx  = self.w // 2 + (i - 1) * 30
            dy  = 44
            filled = i < self.wave_idx or self.state == self.LEVEL_CLEAR
            active = i == self.wave_idx
            col = AMBER if filled else (SOFT_GREEN if active else CREAM_DARK)
            pygame.draw.circle(surface, col, (dx, dy), 10)
            pygame.draw.circle(surface, AMBER_DARK, (dx, dy), 10, 2)

        # Vandita crocheting at top center
        draw_vandita(surface, self.w // 2, self.vandita_cy, scale=0.78, looking_down=False)

        # Yarn / crochet hook visual hint
        hook_x = self.w // 2 + 28
        hook_y = self.vandita_cy - 20
        pygame.draw.line(surface, AMBER_DARK, (hook_x, hook_y), (hook_x + 14, hook_y + 30), 3)
        pygame.draw.circle(surface, DARK_BROWN, (hook_x + 14, hook_y + 30), 4)

        # Yarn string trailing down from Vandita
        if self.state == self.PLAYING:
            start = (hook_x, hook_y + 30)
            ctrl1 = (hook_x + 30, hook_y + 80)
            ctrl2 = (hook_x - 20, hook_y + 130)
            end   = (hook_x + 10, hook_y + 170)
            pts = [_bezier(start, ctrl1, ctrl2, end, t / 20) for t in range(21)]
            for k in range(len(pts) - 1):
                pygame.draw.line(surface, AMBER_DARK, pts[k], pts[k + 1], 2)

        # Score bar
        if self.state == self.PLAYING:
            w = self.wave
            remaining = w["count"] - self.spawned + len([b for b in self.balls if b.alive])
            sc = self.f_score.render(
                f"Caught: {self.caught} / {w['need']}   Lost: {self.stolen}   Left: {remaining}",
                True, DARK_BROWN,
            )
            pygame.draw.rect(surface, (*CARD_BG, 200),
                             pygame.Rect(self.w // 2 - sc.get_width() // 2 - 12,
                                         self.h - 52, sc.get_width() + 24, 36),
                             border_radius=10)
            surface.blit(sc, (self.w // 2 - sc.get_width() // 2, self.h - 45))

            hint = self.f_hint.render("Click the yarn balls to catch them!", True, MID_BROWN)
            surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 78))

        # Yarn balls
        for ball in self.balls:
            if not ball.caught:
                self._draw_yarn_ball(surface, ball)

        # Click pop flashes
        for f in self.flashes:
            prog  = 1 - f["timer"] / 0.45
            alpha = int((1 - prog) * 200)
            size  = BALL_R + int(prog * 30)
            fs    = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(fs, (*f["color"], alpha), (size, size), size)
            surface.blit(fs, (int(f["x"]) - size, int(f["y"]) - size))

        # Beans at the floor
        self._draw_beans(surface)

        # State overlays
        if self.state == self.INTRO:
            self._draw_intro(surface)
        elif self.state == self.ROUND_OK:
            self._draw_round_ok(surface)
        elif self.state == self.ROUND_FAIL:
            self._draw_round_fail(surface)
        elif self.state == self.LEVEL_CLEAR:
            self._draw_level_clear(surface)

    # ── Sub-draw helpers ──────────────────────────────────────────────────────

    def _draw_beans(self, surface):
        """Draw Beans running at the floor, flipped when going left."""
        beans_cy = self.floor_y - 55
        tmp_w, tmp_h = 220, 180
        tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
        happy = self.stolen > 0
        draw_border_collie(tmp, tmp_w // 2, tmp_h // 2 + 20,
                           scale=0.78, happy=happy, tongue=True, pose="sit")
        if self.beans_dir == -1:
            tmp = pygame.transform.flip(tmp, True, False)
        surface.blit(tmp, (int(self.beans_x) - tmp_w // 2, beans_cy - tmp_h // 2))

    def _draw_yarn_ball(self, surface, ball: YarnBall):
        x, y  = int(ball.x), int(ball.y)
        r     = ball.r
        col   = ball.color
        dark  = tuple(max(0, c - 45) for c in col)
        # Shadow
        shd = pygame.Surface((r * 2 + 6, r + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shd, (0, 0, 0, 35), (0, 0, r * 2 + 6, r + 6))
        surface.blit(shd, (x - r - 3, y + r - 4))
        # Body
        pygame.draw.circle(surface, col, (x, y), r)
        pygame.draw.circle(surface, dark, (x, y), r, 2)
        # Rotating swirl
        for i in range(3):
            angle = self.t * 2.2 + i * (2 * math.pi / 3)
            x1 = x + int(math.cos(angle) * r * 0.25)
            y1 = y + int(math.sin(angle) * r * 0.25)
            x2 = x + int(math.cos(angle + math.pi) * r * 0.75)
            y2 = y + int(math.sin(angle + math.pi) * r * 0.75)
            pygame.draw.line(surface, dark, (x1, y1), (x2, y2), 2)
        # Shine
        pygame.draw.circle(surface, WHITE, (x - r // 3, y - r // 3), max(2, r // 4))

    def _draw_intro(self, surface):
        alpha = min(255, int(self.intro_timer * 150))
        card  = pygame.Surface((540, 114), pygame.SRCALPHA)
        pygame.draw.rect(card, (*CARD_BG, min(220, alpha)), (0, 0, 540, 114), border_radius=22)
        surface.blit(card, (self.w // 2 - 270, self.h // 2 - 60))
        if alpha > 50:
            t1 = self.f_title.render("Yarn Crisis!", True, DARK_BROWN)
            t1.set_alpha(alpha)
            surface.blit(t1, (self.w // 2 - t1.get_width() // 2, self.h // 2 - 52))
            t2 = self.f_sub.render("Click the yarn balls before Beans steals them!", True, MID_BROWN)
            t2.set_alpha(alpha)
            surface.blit(t2, (self.w // 2 - t2.get_width() // 2, self.h // 2 + 4))

    def _draw_round_ok(self, surface):
        msgs = ["Wave 1 clear!", "Wave 2 clear!", "Wave 3 clear!"]
        msg  = msgs[min(self.wave_idx, 2)]
        m    = self.f_cmd.render(msg, True, DARK_BROWN)
        card = pygame.Surface((m.get_width() + 44, 56), pygame.SRCALPHA)
        pygame.draw.rect(card, (*SOFT_PINK, 210), (0, 0, card.get_width(), 56), border_radius=14)
        surface.blit(card, (self.w // 2 - card.get_width() // 2, self.h // 2 - 60))
        surface.blit(m,    (self.w // 2 - m.get_width() // 2,    self.h // 2 - 52))

    def _draw_round_fail(self, surface):
        m    = self.f_cmd.render(f"Beans got {self.stolen}! Try again...", True, NOPE_RED)
        card = pygame.Surface((m.get_width() + 44, 56), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 200, 200, 210), (0, 0, card.get_width(), 56), border_radius=14)
        surface.blit(card, (self.w // 2 - card.get_width() // 2, self.h // 2 - 60))
        surface.blit(m,    (self.w // 2 - m.get_width() // 2,    self.h // 2 - 52))

    def _draw_level_clear(self, surface):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((*SOFT_PINK, min(185, self.clear_alpha)))
        surface.blit(overlay, (0, 0))
        if self.clear_alpha > 80:
            big = self.f_big.render("Chapter 5 Complete!", True, DARK_BROWN)
            big.set_alpha(min(255, self.clear_alpha))
            surface.blit(big, (self.w // 2 - big.get_width() // 2, self.h // 2 - 65))
            sub = self.f_sub.render("Vandita saved the yarn. Beans was NOT impressed.", True, MID_BROWN)
            sub.set_alpha(min(255, self.clear_alpha))
            surface.blit(sub, (self.w // 2 - sub.get_width() // 2, self.h // 2 + 10))
            if int(self.clear_timer * 2) % 2 == 0:
                cont = self.f_hint.render("Press any key to continue ->", True, MID_BROWN)
                surface.blit(cont, (self.w // 2 - cont.get_width() // 2, self.h // 2 + 55))


def _bezier(p0, p1, p2, p3, t):
    """Cubic bezier point at parameter t."""
    u = 1 - t
    x = u**3 * p0[0] + 3*u**2*t * p1[0] + 3*u*t**2 * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3*u**2*t * p1[1] + 3*u*t**2 * p2[1] + t**3 * p3[1]
    return (int(x), int(y))
