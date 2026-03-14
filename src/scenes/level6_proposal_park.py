import math

import pygame

from src.utils.constants import (
    CREAM,
    SKY_BLUE,
    SOFT_GREEN,
    LEAF_GREEN,
    AMBER,
    AMBER_DARK,
    CARD_BG,
    DARK_BROWN,
    MID_BROWN,
    GOLD,
    HEART_RED,
    SCENE_COMING,
)
from src.utils.draw_helpers import draw_cute_face, draw_rounded_rect


class Level6ProposalPark:
    """
    Combined Level 6 + 7 — “Will You Be Mine?” + “The Proposal”

    Twilight park scene lit with string lights, blankets, wine, fruit.
    You walk Krishna over to each “moment” and press space/enter to set it up.
    When everything’s ready, the proposal sequence plays.
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        # Player avatar (Krishna-like chibi)
        self.x = self.w * 0.22
        self.y = self.h * 0.70
        self.speed = 210.0

        # Interaction points (blanket, lights, picnic basket)
        self.targets = [
            {"name": "blanket", "x": self.w * 0.48, "y": self.h * 0.72, "on": False},
            {"name": "lights", "x": self.w * 0.65, "y": self.h * 0.40, "on": False},
            {"name": "picnic", "x": self.w * 0.34, "y": self.h * 0.58, "on": False},
        ]

        self.prompt_alpha = 0
        self.t = 0.0
        self.proposed = False
        self.propose_timer = 0.0

        self.font_hdr = pygame.font.SysFont("Georgia", 24, bold=True)
        self.font_sub = pygame.font.SysFont("Georgia", 18, italic=True)
        self.font_ui = pygame.font.SysFont("Arial", 18)
        self.font_big = pygame.font.SysFont("Georgia", 46, bold=True)
        self.font_mid = pygame.font.SysFont("Georgia", 26, bold=True)

    # ------------------------------------------------------------------ events
    def handle_event(self, event):
        if self.proposed:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.next_scene = SCENE_COMING
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                # Check if near a target and toggle it on
                px = self.x
                py = self.y
                for t in self.targets:
                    dx = px - t["x"]
                    dy = py - t["y"]
                    if dx * dx + dy * dy < (80 * 80):
                        t["on"] = True

    # ------------------------------------------------------------------- update
    def update(self, dt: float):
        self.t += dt

        if not self.proposed:
            keys = pygame.key.get_pressed()
            vx = vy = 0.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                vx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                vx += 1
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

            # Constrain to park
            margin = 60
            self.x = max(margin, min(self.w - margin, self.x))
            ground_min = int(self.h * 0.42)
            self.y = max(ground_min, min(self.h - margin, self.y))

            # Blink interaction prompt when near something still off
            near = any(
                (not t["on"]) and ((self.x - t["x"]) ** 2 + (self.y - t["y"]) ** 2 < (90 * 90))
                for t in self.targets
            )
            if near:
                self.prompt_alpha = min(255, self.prompt_alpha + dt * 420)
            else:
                self.prompt_alpha = max(0, self.prompt_alpha - dt * 420)

            # All set?
            if all(t["on"] for t in self.targets):
                self.proposed = True
                self.propose_timer = 0.0

        else:
            self.propose_timer += dt

    # --------------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface):
        # Night sky gradient
        for y in range(self.h):
            t = y / self.h
            r = int(20 * (1 - t) + SKY_BLUE[0] * t * 0.4)
            g = int(18 * (1 - t) + SKY_BLUE[1] * t * 0.4)
            b = int(40 * (1 - t) + SKY_BLUE[2] * t * 0.7)
            surface.fill((r, g, b), pygame.Rect(0, y, self.w, 1))

        # Soft grass
        base_y = int(self.h * 0.70)
        ground_pts = [(0, self.h)]
        for x in range(0, self.w + 30, 14):
            y_off = math.sin(x * 0.010 + self.t * 0.5) * 10
            ground_pts.append((x, base_y + y_off))
        ground_pts.append((self.w, self.h))
        pygame.draw.polygon(surface, SOFT_GREEN, ground_pts)

        # Distant tree silhouettes
        for x in range(80, self.w, 160):
            trunk_x = x
            trunk_y = base_y - 40
            pygame.draw.rect(surface, (34, 22, 12), (trunk_x - 6, trunk_y, 12, 40))
            pygame.draw.circle(surface, (30, 60, 30), (trunk_x, trunk_y), 30)

        # Hanging string lights between trees
        light_y = base_y - 110
        points = []
        for i in range(0, 9):
            px = 80 + i * ((self.w - 160) / 8)
            py = light_y + math.sin(self.t * 1.2 + i * 0.8) * 4
            points.append((px, py))
        pygame.draw.lines(surface, (140, 110, 80), False, points, 3)
        for i, (px, py) in enumerate(points):
            phase = self.t * 3 + i
            glow = 180 + int(math.sin(phase) * 60)
            pygame.draw.circle(surface, (glow, glow, 150), (int(px), int(py)), 6)

        # Header card
        card_rect = pygame.Rect(self.w // 2 - 260, 22, 520, 80)
        draw_rounded_rect(surface, (*CARD_BG, 230), card_rect, radius=20, shadow=True, shadow_offset=4)
        hdr = self.font_hdr.render("Level 6  ·  Will You Be Mine?", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2, 30))
        sub = self.font_sub.render("Set the scene together: lights, blanket, picnic. Then ask the question.", True, MID_BROWN)
        surface.blit(sub, (self.w // 2 - sub.get_width() // 2, 56))

        # Blanket
        blanket = next(t for t in self.targets if t["name"] == "blanket")
        bx = int(blanket["x"])
        by = int(blanket["y"])
        rect = pygame.Rect(bx - 90, by - 16, 180, 52)
        col = (235, 215, 185) if blanket["on"] else (205, 188, 165)
        pygame.draw.rect(surface, col, rect, border_radius=12)
        pygame.draw.rect(surface, (200, 170, 140), rect, 2, border_radius=12)

        # Picnic items on blanket
        if blanket["on"]:
            # Wine bottle
            pygame.draw.rect(surface, (40, 90, 50), (bx - 40, by - 36, 16, 32), border_radius=4)
            pygame.draw.rect(surface, (30, 60, 40), (bx - 36, by - 48, 8, 16), border_radius=3)
            # Glasses
            pygame.draw.rect(surface, (200, 230, 255), (bx - 8, by - 22, 10, 18), border_radius=3)
            pygame.draw.rect(surface, (200, 230, 255), (bx + 8, by - 24, 10, 20), border_radius=3)
            # Fruit bowl
            pygame.draw.ellipse(surface, (195, 120, 90), (bx + 28, by - 8, 32, 18))
            pygame.draw.circle(surface, (230, 80, 80), (bx + 34, by - 2), 5)
            pygame.draw.circle(surface, (240, 210, 90), (bx + 46, by - 4), 5)
            pygame.draw.circle(surface, (120, 180, 90), (bx + 54, by - 1), 5)

        # Picnic basket target (even before "on" it's visible)
        picnic = next(t for t in self.targets if t["name"] == "picnic")
        px = int(picnic["x"])
        py = int(picnic["y"])
        basket_rect = pygame.Rect(px - 32, py - 26, 64, 34)
        pygame.draw.rect(surface, (165, 110, 70), basket_rect, border_radius=8)
        pygame.draw.rect(surface, (140, 88, 50), basket_rect, 2, border_radius=8)
        if picnic["on"]:
            lid_rect = pygame.Rect(px - 34, py - 40, 68, 16)
            pygame.draw.rect(surface, (175, 120, 78), lid_rect, border_radius=8)

        # Lights control target
        lights = next(t for t in self.targets if t["name"] == "lights")
        lx = int(lights["x"])
        ly = int(lights["y"])
        switch_rect = pygame.Rect(lx - 20, ly - 18, 40, 36)
        pygame.draw.rect(surface, (60, 60, 80), switch_rect, border_radius=6)
        if lights["on"]:
            knob_y = ly - 4
            color = (250, 233, 150)
        else:
            knob_y = ly + 4
            color = (130, 130, 150)
        pygame.draw.circle(surface, color, (lx, knob_y), 8)

        # Player + Vandita sitting on blanket once proposed
        if not self.proposed:
            # Walking Krishna
            walk_bob = math.sin(self.t * 6.0) * 3
            draw_cute_face(
                surface,
                int(self.x),
                int(self.y + walk_bob),
                scale=0.9,
                skin=(200, 158, 115),
                hair=(40, 28, 15),
                hair_style=4,
                blush=True,
            )
        else:
            # Sitting together on blanket
            kx = bx - 26
            ky = by + 10
            vx = bx + 28
            vy = by + 10
            draw_cute_face(
                surface,
                int(kx),
                int(ky),
                scale=0.85,
                skin=(200, 158, 115),
                hair=(40, 28, 15),
                hair_style=4,
                blush=True,
            )
            draw_cute_face(
                surface,
                int(vx),
                int(vy),
                scale=0.85,
                skin=(235, 195, 160),
                hair=(100, 70, 40),
                hair_style=1,
                blush=True,
            )

        # Interaction prompt
        if not self.proposed and self.prompt_alpha > 0:
            prompt = self.font_ui.render("Press space / enter here", True, CREAM)
            surf = pygame.Surface((prompt.get_width() + 16, prompt.get_height() + 8), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 0, 0, 160), (0, 0, surf.get_width(), surf.get_height()), border_radius=10)
            surf.blit(prompt, (8, 4))
            surf.set_alpha(int(self.prompt_alpha))
            surface.blit(surf, (int(self.x - surf.get_width() / 2), int(self.y - 70)))

        # Proposal overlay
        if self.proposed:
            alpha = min(230, int(self.propose_timer * 120) + 80)
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(alpha * 0.55)))
            surface.blit(overlay, (0, 0))

            # Ring icon
            ring_r = 26
            ring_surf = pygame.Surface((ring_r * 4, ring_r * 4), pygame.SRCALPHA)
            cx = ring_r * 2
            cy = ring_r * 2
            pygame.draw.circle(ring_surf, GOLD, (cx, cy), ring_r, 5)
            pygame.draw.polygon(
                ring_surf,
                (240, 240, 255),
                [(cx, cy - ring_r - 8), (cx - 10, cy - ring_r + 6), (cx + 10, cy - ring_r + 6)],
            )
            surface.blit(ring_surf, (self.w // 2 - ring_surf.get_width() // 2, self.h // 2 - 140))

            msg = self.font_big.render("Will you marry me?", True, CREAM)
            surface.blit(msg, (self.w // 2 - msg.get_width() // 2, self.h // 2 - 40))

            sub = self.font_mid.render("She had a ring too.  ♡", True, CREAM)
            surface.blit(sub, (self.w // 2 - sub.get_width() // 2, self.h // 2 + 10))

            if int(self.propose_timer * 2) % 2 == 0:
                tap = self.font_ui.render("Press any key to continue", True, CREAM)
                surface.blit(tap, (self.w // 2 - tap.get_width() // 2, self.h // 2 + 60))

        # Bottom hint
        hint = self.font_ui.render("Move with WASD / arrows. Set up the scene, then press space/enter when you're close.", True, CREAM)
        surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 34))

