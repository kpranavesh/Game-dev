import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import draw_rounded_rect, draw_cute_face, lerp, ease_out
from src.entities.profile import PROFILES


def _draw_heart(surface, cx, cy, size, color):
    pts = []
    for i in range(360):
        angle = math.radians(i)
        x = size * (16 * math.sin(angle) ** 3) / 16
        y = -size * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)) / 16
        pts.append((cx + x, cy + y))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)


class HeartParticle:
    def __init__(self, cx, cy):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 5)
        self.x = cx + random.uniform(-30, 30)
        self.y = cy + random.uniform(-20, 20)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.size = random.uniform(10, 22)
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.03)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= self.decay
        self.size *= 0.98

    @property
    def alive(self):
        return self.life > 0


class Level1Hinge:
    ENTERING = "entering"
    IDLE = "idle"
    EXIT_LEFT = "exit_left"
    EXIT_RIGHT = "exit_right"
    MATCHED = "matched"
    MISSED = "missed"
    DONE = "done"

    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        self.profiles = list(PROFILES)
        self.idx = 0
        self.card_x = screen_w + CARD_W
        self.card_y = self.h // 2 - CARD_H // 2 - 20
        self.target_x = self.w // 2 - CARD_W // 2
        self.state = self.ENTERING

        self.heart_particles = []
        self.match_alpha = 0
        self.match_timer = 0
        self.shake_t = 0
        self.shake_x = 0
        self.t = 0
        self.swipe_hint_alpha = 255

        self.font_name  = pygame.font.SysFont("Georgia", 30, bold=True)
        self.font_info  = pygame.font.SysFont("Georgia", 18)
        self.font_bio   = pygame.font.SysFont("Georgia", 16, italic=True)
        self.font_big   = pygame.font.SysFont("Georgia", 52, bold=True)
        self.font_hint  = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_ui    = pygame.font.SysFont("Georgia", 20)

        self.nope_alpha = 0
        self.like_alpha = 0
        self.show_nope = False
        self.show_like = False

    def _current_profile(self):
        return self.profiles[self.idx]

    def handle_event(self, event):
        if self.state != self.IDLE:
            if self.state == self.MATCHED and event.type == pygame.KEYDOWN:
                self.next_scene = SCENE_COMING
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.show_nope = True
                self.nope_alpha = 255
                self.state = self.EXIT_LEFT
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.show_like = True
                self.like_alpha = 255
                if self._current_profile().is_krishna:
                    self.state = self.MATCHED
                    self._spawn_hearts()
                else:
                    self.state = self.EXIT_RIGHT

    def _spawn_hearts(self):
        cx = self.w // 2
        cy = self.h // 2
        for _ in range(35):
            self.heart_particles.append(HeartParticle(cx, cy))

    def update(self, dt):
        self.t += dt
        self.heart_particles = [p for p in self.heart_particles if p.alive]
        for p in self.heart_particles:
            p.update()

        cx = self.target_x

        if self.state == self.ENTERING:
            self.card_x = lerp(self.card_x, cx, 0.12)
            if abs(self.card_x - cx) < 2:
                self.card_x = cx
                self.state = self.IDLE

        elif self.state == self.EXIT_LEFT:
            self.card_x = lerp(self.card_x, -CARD_W - 50, 0.14)
            if self.card_x < -CARD_W:
                self._advance()

        elif self.state == self.EXIT_RIGHT:
            self.card_x = lerp(self.card_x, self.w + 50, 0.14)
            if self.card_x > self.w:
                self._advance()

        elif self.state == self.MATCHED:
            self.match_alpha = min(255, self.match_alpha + 6)
            self.match_timer += dt
            if self.match_timer > 3.5:
                self.next_scene = SCENE_COMING

        if self.nope_alpha > 0:
            self.nope_alpha = max(0, self.nope_alpha - 6)
        if self.like_alpha > 0:
            self.like_alpha = max(0, self.like_alpha - 6)
        if self.state == self.IDLE:
            self.show_nope = False
            self.show_like = False

    def _advance(self):
        self.idx += 1
        if self.idx >= len(self.profiles):
            self.idx = 0
        self.card_x = self.w + CARD_W
        self.state = self.ENTERING
        self.show_nope = False
        self.show_like = False

    def _draw_card(self, surface, profile, x, y):
        rect = pygame.Rect(int(x), y, CARD_W, CARD_H)

        shadow_surf = pygame.Surface((CARD_W + 10, CARD_H + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 45), (6, 6, CARD_W, CARD_H), border_radius=22)
        surface.blit(shadow_surf, (int(x) - 3, y - 3))

        pygame.draw.rect(surface, CARD_BG, rect, border_radius=22)
        pygame.draw.rect(surface, AMBER, rect, width=2, border_radius=22)

        portrait_rect = pygame.Rect(int(x) + 10, y + 10, CARD_W - 20, 230)
        port_surf = pygame.Surface((CARD_W - 20, 230), pygame.SRCALPHA)
        for py in range(230):
            t = py / 230
            r = int(SKY_BLUE[0] * (1 - t) + CREAM[0] * t)
            g = int(SKY_BLUE[1] * (1 - t) + CREAM[1] * t)
            b = int(SKY_BLUE[2] * (1 - t) + CREAM[2] * t)
            pygame.draw.line(port_surf, (r, g, b, 255), (0, py), (CARD_W - 20, py))
        surface.blit(port_surf, (portrait_rect.x, portrait_rect.y))
        pygame.draw.rect(surface, AMBER_DARK, portrait_rect, width=1, border_radius=14)

        face_cx = int(x) + CARD_W // 2
        face_cy = y + 130
        draw_cute_face(surface, face_cx, face_cy, scale=1.0,
                       skin=profile.skin_color, hair=profile.hair_color,
                       hair_style=profile.hair_style, blush=True)

        emoji_font = pygame.font.SysFont("Apple Color Emoji", 28)
        try:
            em = emoji_font.render(profile.emoji, True, BLACK)
            surface.blit(em, (int(x) + CARD_W - 50, y + 15))
        except Exception:
            pass

        pygame.draw.line(surface, CREAM_DARK,
                         (int(x) + 20, y + 245),
                         (int(x) + CARD_W - 20, y + 245), 1)

        name_surf = self.font_name.render(f"{profile.name}, {profile.age}", True, DARK_BROWN)
        surface.blit(name_surf, (int(x) + 20, y + 255))

        job_surf = self.font_info.render(profile.job, True, MID_BROWN)
        surface.blit(job_surf, (int(x) + 20, y + 292))

        bio_lines = _wrap_text(profile.bio, self.font_bio, CARD_W - 40)
        for i, line in enumerate(bio_lines):
            ls = self.font_bio.render(line, True, MID_BROWN)
            surface.blit(ls, (int(x) + 20, y + 320 + i * 22))

        if self.show_nope and self.nope_alpha > 0:
            stamp_surf2 = self.font_big.render("NOPE", True, NOPE_RED)
            rot = pygame.transform.rotate(stamp_surf2, 20)
            rot_surf = pygame.Surface(rot.get_size(), pygame.SRCALPHA)
            rot_surf.blit(rot, (0, 0))
            rot_surf.set_alpha(self.nope_alpha)
            surface.blit(rot_surf, (int(x) + 20, y + 80))

        if self.show_like and self.like_alpha > 0:
            stamp_surf2 = self.font_big.render("LIKE ♡", True, LIKE_GREEN)
            rot = pygame.transform.rotate(stamp_surf2, -20)
            rot_surf = pygame.Surface(rot.get_size(), pygame.SRCALPHA)
            rot_surf.blit(rot, (0, 0))
            rot_surf.set_alpha(self.like_alpha)
            surface.blit(rot_surf, (int(x) + CARD_W - rot.get_width() - 20, y + 80))

    def draw(self, surface):
        for y in range(self.h):
            t = y / self.h
            r = int(SKY_BLUE[0] * (1 - t) + CREAM[0] * t)
            g = int(SKY_BLUE[1] * (1 - t) + CREAM[1] * t)
            b = int(SKY_BLUE[2] * (1 - t) + CREAM[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        random.seed(42)
        for i in range(8):
            px = (int(self.t * 25 + i * 137) % (self.w + 40)) - 20
            py = (int(self.t * 18 + i * 211) % (self.h + 40)) - 20
            pygame.draw.circle(surface, (*SOFT_PINK, 160), (px, py), 5)
        random.seed()

        header = self.font_ui.render(f"Level 1  ·  Swipe Right  ✦  {self.idx + 1}/{len(self.profiles)}", True, DARK_BROWN)
        surface.blit(header, (self.w//2 - header.get_width()//2, 18))

        if self.state == self.IDLE:
            hint = self.font_small.render("← Nope     |     Like →", True, MID_BROWN)
            surface.blit(hint, (self.w//2 - hint.get_width()//2, self.h - 38))

        if self.state != self.MATCHED or self.match_alpha < 200:
            self._draw_card(surface, self._current_profile(), self.card_x, self.card_y)

        nope_rect = pygame.Rect(self.w//2 - CARD_W//2 - 70, self.h//2 + 80, 56, 56)
        like_rect = pygame.Rect(self.w//2 + CARD_W//2 + 14, self.h//2 + 80, 56, 56)
        pygame.draw.circle(surface, NOPE_RED, nope_rect.center, 28)
        pygame.draw.circle(surface, LIKE_GREEN, like_rect.center, 28)
        x_surf = self.font_name.render("✕", True, WHITE)
        heart_surf = self.font_name.render("♡", True, WHITE)
        surface.blit(x_surf, (nope_rect.centerx - x_surf.get_width()//2, nope_rect.centery - x_surf.get_height()//2))
        surface.blit(heart_surf, (like_rect.centerx - heart_surf.get_width()//2, like_rect.centery - heart_surf.get_height()//2))

        for p in self.heart_particles:
            alpha = int(p.life * 255)
            _draw_heart(surface, int(p.x), int(p.y), int(p.size), (*HEART_RED, alpha))

        if self.state == self.MATCHED and self.match_alpha > 0:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((*SOFT_PINK, min(200, self.match_alpha)))
            surface.blit(overlay, (0, 0))

            if self.match_alpha > 100:
                big = self.font_big.render("IT'S A MATCH! 💕", True, DARK_BROWN)
                surface.blit(big, (self.w//2 - big.get_width()//2, self.h//2 - 60))
                sub = self.font_info.render("She found her person.", True, MID_BROWN)
                surface.blit(sub, (self.w//2 - sub.get_width()//2, self.h//2 + 20))
                if int(self.t * 2) % 2 == 0:
                    cont = self.font_hint.render("Press any key to continue →", True, MID_BROWN)
                    surface.blit(cont, (self.w//2 - cont.get_width()//2, self.h//2 + 70))


def _wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
