"""
Level 2: Good Girl, Beans
==========================
Simon Says mechanic — watch a sequence of commands, then repeat it.
3 rounds of increasing length. Beans is a border collie.
"""
import pygame
import math
import random
from src.utils.constants import *
from src.utils.draw_helpers import draw_border_collie, draw_rounded_rect, draw_vandita, draw_food_bowl

# ── Command definitions ────────────────────────────────────────────────────────
CMDS = ["SIT", "DOWN", "MIDDLE", "FREE"]

CMD_EMOJI = {
    "SIT":    "🐾",
    "DOWN":   "⬇️",
    "MIDDLE": "⭕",
    "FREE":   "🎉",
}

CMD_COLOR = {
    "SIT":    (130, 195, 130),
    "DOWN":   (130, 160, 210),
    "MIDDLE": (200, 130, 200),
    "FREE":   (210, 155, 80),
}

# Pose each command triggers on Beans
CMD_POSE = {
    "SIT":    "sit",
    "DOWN":   "down",
    "MIDDLE": "middle",
    "FREE":   "free",
}

ROUNDS = [
    ["SIT", "DOWN", "MIDDLE"],
    ["FREE", "SIT", "DOWN", "MIDDLE"],
    ["MIDDLE", "FREE", "SIT", "DOWN", "FREE", "MIDDLE"],
]

BTN_W, BTN_H, BTN_GAP = 138, 58, 14


def _draw_heart(surface, cx, cy, size, color):
    pts = []
    for i in range(360):
        a = math.radians(i)
        x = size * (16 * math.sin(a) ** 3) / 16
        y = -size * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16
        pts.append((cx + int(x), cy + int(y)))
    if len(pts) >= 3:
        try:
            pygame.draw.polygon(surface, color[:3], pts)
        except Exception:
            pass


class HeartParticle:
    def __init__(self, cx, cy):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.8, 4.5)
        self.x = cx + random.uniform(-30, 30)
        self.y = cy + random.uniform(-15, 15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2.0
        self.size = random.uniform(8, 18)
        self.life = 1.0
        self.decay = random.uniform(0.012, 0.022)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.10
        self.life  -= self.decay
        self.size  *= 0.985

    @property
    def alive(self):
        return self.life > 0 and self.size > 1


class Level2Beans:
    # States
    INTRO         = "intro"
    SHOW_SEQ      = "show_seq"
    PLAYER_TURN   = "player_turn"
    FEEDBACK_OK   = "feedback_ok"
    FEEDBACK_FAIL = "feedback_fail"
    LEVEL_CLEAR   = "level_clear"

    SEQ_SHOW  = 0.85   # seconds each command is displayed
    SEQ_PAUSE = 0.28   # gap after each command fades
    INTRO_DUR = 2.4

    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.next_scene = None

        self.t             = 0.0
        self.state         = self.INTRO
        self.intro_timer   = 0.0
        self.round_idx     = 0

        # Show-sequence state
        self.seq_step      = 0
        self.seq_timer     = 0.0

        # Player input
        self.player_input  = []
        self.last_clicked  = None   # highlighted briefly after click

        # Feedback
        self.fb_timer      = 0.0
        self.shake_x       = 0

        # Beans animation
        self.beans_cx      = screen_w // 2
        self.beans_cy      = int(screen_h * 0.40)
        self.beans_bob     = 0.0
        self.beans_happy   = False
        self.beans_tongue  = False
        self.beans_spin    = 0.0    # degrees, for FEEDBACK_OK spin
        self.beans_pose    = "middle"
        self.pose_timer    = 0.0    # how long to hold pose before returning to middle
        self.pose_start_ms = pygame.time.get_ticks()

        # Hearts
        self.hearts: list[HeartParticle] = []

        # Level-clear fade
        self.clear_timer   = 0.0
        self.clear_alpha   = 0

        # Fonts
        self.f_title  = pygame.font.SysFont("Georgia", 46, bold=True)
        self.f_sub    = pygame.font.SysFont("Georgia", 22, italic=True)
        self.f_cmd    = pygame.font.SysFont("Georgia", 28, bold=True)
        self.f_btn    = pygame.font.SysFont("Georgia", 17, bold=True)
        self.f_hint   = pygame.font.SysFont("Arial", 20)
        self.f_hdr    = pygame.font.SysFont("Georgia", 20)
        self.f_big    = pygame.font.SysFont("Georgia", 52, bold=True)

        # Build button rects (5 buttons centred at bottom)
        total_w = len(CMDS) * BTN_W + (len(CMDS) - 1) * BTN_GAP
        bx0     = (screen_w - total_w) // 2
        by0     = screen_h - BTN_H - 24
        self.btn_rects: dict[str, pygame.Rect] = {
            cmd: pygame.Rect(bx0 + i * (BTN_W + BTN_GAP), by0, BTN_W, BTN_H)
            for i, cmd in enumerate(CMDS)
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def current_round(self):
        return ROUNDS[self.round_idx]

    def _start_show(self):
        self.state     = self.SHOW_SEQ
        self.seq_step  = 0
        self.seq_timer = 0.0

    def _spawn_hearts(self):
        for _ in range(22):
            self.hearts.append(HeartParticle(self.beans_cx, self.beans_cy))

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if self.state == self.PLAYER_TURN:
            cmd = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for c, rect in self.btn_rects.items():
                    if rect.collidepoint(event.pos):
                        cmd = c
                        break
            elif event.type == pygame.KEYDOWN:
                key_map = {
                    pygame.K_1: "SIT",
                    pygame.K_2: "DOWN",
                    pygame.K_3: "MIDDLE",
                    pygame.K_4: "FREE",
                }
                cmd = key_map.get(event.key)
            if cmd:
                self._on_click(cmd)

        elif self.state == self.LEVEL_CLEAR:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.next_scene = SCENE_COMING

    def _on_click(self, cmd: str):
        self.last_clicked = cmd
        # Trigger Beans pose immediately on any button press
        self.beans_pose    = CMD_POSE[cmd]
        self.pose_start_ms = pygame.time.get_ticks()
        # MIDDLE and FREE have multi-phase animations — hold longer
        self.pose_timer = 2.5 if cmd in ("MIDDLE", "FREE") else 0.8
        expected = self.current_round[len(self.player_input)]
        if cmd == expected:
            self.player_input.append(cmd)
            if len(self.player_input) == len(self.current_round):
                # Round complete
                self.state        = self.FEEDBACK_OK
                self.fb_timer     = 0.0
                self.beans_happy  = True
                self.beans_tongue = True
                self.beans_spin   = 0.0
                self._spawn_hearts()
        else:
            self.state        = self.FEEDBACK_FAIL
            self.fb_timer     = 0.0
            self.beans_happy  = False
            self.beans_tongue = False

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self.t        += dt
        self.beans_bob = math.sin(self.t * 3.0) * 5

        # Pose timer — return to middle after holding
        if self.pose_timer > 0:
            self.pose_timer -= dt
            if self.pose_timer <= 0 and self.state not in (self.FEEDBACK_OK, self.LEVEL_CLEAR):
                self.beans_pose = "middle"

        # Hearts
        for h in self.hearts:
            h.update()
        self.hearts = [h for h in self.hearts if h.alive]

        if self.state == self.INTRO:
            self.intro_timer += dt
            if self.intro_timer >= self.INTRO_DUR:
                self._start_show()

        elif self.state == self.SHOW_SEQ:
            self.seq_timer += dt
            if self.seq_timer >= self.SEQ_SHOW + self.SEQ_PAUSE:
                self.seq_step  += 1
                self.seq_timer  = 0.0
                if self.seq_step >= len(self.current_round):
                    # Hand off to player
                    self.state        = self.PLAYER_TURN
                    self.player_input = []
                    self.last_clicked = None

        elif self.state == self.FEEDBACK_OK:
            self.fb_timer    += dt
            self.beans_spin  += dt * 300   # spin Beans
            if self.fb_timer >= 1.8:
                self.round_idx   += 1
                self.beans_happy  = False
                self.beans_tongue = False
                self.beans_spin   = 0.0
                if self.round_idx >= len(ROUNDS):
                    self.state       = self.LEVEL_CLEAR
                    self.clear_timer = 0.0
                else:
                    self._start_show()

        elif self.state == self.FEEDBACK_FAIL:
            self.fb_timer += dt
            if self.fb_timer < 0.55:
                self.shake_x = int(math.sin(self.fb_timer * 45) * 9)
            else:
                self.shake_x = 0
            if self.fb_timer >= 1.6:
                self.shake_x = 0
                self._start_show()   # replay same round

        elif self.state == self.LEVEL_CLEAR:
            self.clear_timer += dt
            self.clear_alpha  = min(255, int(self.clear_timer * 130))
            self.beans_happy  = True
            self.beans_tongue = True
            # After a short celebration, head to the yarn level
            if self.clear_timer >= 6.0:
                from src.utils.constants import SCENE_LEVEL3  # local import to avoid cycle
                self.next_scene = SCENE_LEVEL3

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface):
        sx = self.shake_x

        # Background gradient (warm cream → sky)
        for y in range(self.h):
            frac = y / self.h
            r = int(CREAM[0] * (1 - frac) + SKY_BLUE[0] * frac)
            g = int(CREAM[1] * (1 - frac) + SKY_BLUE[1] * frac)
            b = int(CREAM[2] * (1 - frac) + SKY_BLUE[2] * frac)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Header
        hdr = self.f_hdr.render("Level 2  ·  Good Girl, Beans", True, DARK_BROWN)
        surface.blit(hdr, (self.w // 2 - hdr.get_width() // 2 + sx, 14))

        # Round progress dots (3 rounds)
        for i in range(len(ROUNDS)):
            dx = self.w // 2 + (i - 1) * 30 + sx
            dy = 44
            filled = i < self.round_idx or self.state == self.LEVEL_CLEAR
            active = i == self.round_idx
            col    = AMBER if filled else (SOFT_GREEN if active else CREAM_DARK)
            pygame.draw.circle(surface, col, (dx, dy), 10)
            pygame.draw.circle(surface, AMBER_DARK, (dx, dy), 10, 2)
            if active and self.state not in (self.INTRO,):
                num = self.f_btn.render(str(i + 1), True, DARK_BROWN)
                surface.blit(num, (dx - num.get_width() // 2, dy - num.get_height() // 2))

        # ── Beans ─────────────────────────────────────────────────────────────
        bx = self.beans_cx + sx
        by = int(self.beans_cy + self.beans_bob)

        if self.state == self.FEEDBACK_OK and self.beans_spin > 0:
            # Draw Beans to temp surface and rotate for the happy spin
            tmp_size = 180
            tmp = pygame.Surface((tmp_size, tmp_size), pygame.SRCALPHA)
            draw_border_collie(tmp, tmp_size // 2, tmp_size // 2,
                               scale=1.0, happy=True, tongue=True)
            rotated = pygame.transform.rotate(tmp, self.beans_spin % 360)
            surface.blit(rotated, (bx - rotated.get_width() // 2,
                                   by - rotated.get_height() // 2))
        else:
            pose_elapsed = pygame.time.get_ticks() - self.pose_start_ms
            draw_border_collie(surface, bx, by, scale=1.0,
                               happy=self.beans_happy, tongue=self.beans_tongue,
                               pose=self.beans_pose, pose_elapsed_ms=pose_elapsed)

        # ── Heart particles ────────────────────────────────────────────────────
        for h in self.hearts:
            alpha = int(h.life * 230)
            _draw_heart(surface, int(h.x) + sx, int(h.y), int(h.size), (HEART_RED[0], HEART_RED[1], HEART_RED[2], alpha))

        # ── State overlays ─────────────────────────────────────────────────────
        if self.state == self.INTRO:
            self._draw_intro(surface, sx)

        elif self.state == self.SHOW_SEQ:
            self._draw_show_seq(surface, sx)

        elif self.state == self.PLAYER_TURN:
            self._draw_player_turn(surface, sx)

        elif self.state == self.FEEDBACK_OK:
            self._draw_feedback_ok(surface, sx)

        elif self.state == self.FEEDBACK_FAIL:
            self._draw_feedback_fail(surface, sx)

        elif self.state == self.LEVEL_CLEAR:
            self._draw_level_clear(surface)

        # ── Buttons (always visible) ───────────────────────────────────────────
        self._draw_buttons(surface, sx)

    # ── Sub-draw helpers ──────────────────────────────────────────────────────

    def _draw_intro(self, surface, sx):
        alpha = min(255, int(self.intro_timer * 160))
        card  = pygame.Surface((500, 108), pygame.SRCALPHA)
        pygame.draw.rect(card, (*CARD_BG, min(220, alpha)), (0, 0, 500, 108), border_radius=22)
        surface.blit(card, (self.w // 2 - 250 + sx, self.h // 2 - 160))
        if alpha > 60:
            t_surf = self.f_title.render("Good Girl, Beans!", True, DARK_BROWN)
            t_surf.set_alpha(alpha)
            surface.blit(t_surf, (self.w // 2 - t_surf.get_width() // 2 + sx, self.h // 2 - 152))
            s_surf = self.f_sub.render("Watch the sequence — then repeat it!", True, MID_BROWN)
            s_surf.set_alpha(alpha)
            surface.blit(s_surf, (self.w // 2 - s_surf.get_width() // 2 + sx, self.h // 2 - 100))

    def _draw_show_seq(self, surface, sx):
        if self.seq_step >= len(self.current_round):
            return
        cmd   = self.current_round[self.seq_step]
        # Fade in/out card
        prog  = self.seq_timer / (self.SEQ_SHOW + self.SEQ_PAUSE)
        if self.seq_timer < self.SEQ_SHOW:
            card_alpha = min(230, int(self.seq_timer / 0.18 * 230))
        else:
            card_alpha = max(0, int((1 - (self.seq_timer - self.SEQ_SHOW) / self.SEQ_PAUSE) * 230))

        card = pygame.Surface((280, 88), pygame.SRCALPHA)
        col  = CMD_COLOR[cmd]
        pygame.draw.rect(card, (*col, card_alpha), (0, 0, 280, 88), border_radius=20)
        surface.blit(card, (self.w // 2 - 140 + sx, self.beans_cy - 148))

        if card_alpha > 40:
            lbl = self.f_cmd.render(f"{CMD_EMOJI[cmd]}  {cmd}", True, DARK_BROWN)
            lbl.set_alpha(card_alpha)
            surface.blit(lbl, (self.w // 2 - lbl.get_width() // 2 + sx, self.beans_cy - 134))

        # Mini sequence dots above card
        self._draw_seq_dots(surface, sx, filled_up_to=self.seq_step, y=self.beans_cy - 168)

        # "Watch..." hint
        hint = self.f_hint.render("Watch carefully...", True, MID_BROWN)
        surface.blit(hint, (self.w // 2 - hint.get_width() // 2 + sx, self.beans_cy - 80))

    def _draw_player_turn(self, surface, sx):
        self._draw_seq_dots(surface, sx, filled_up_to=len(self.player_input) - 1,
                            y=self.beans_cy - 105, show_remaining=True)
        hint = self.f_hint.render("Your turn! Click the commands in order.", True, MID_BROWN)
        surface.blit(hint, (self.w // 2 - hint.get_width() // 2 + sx, self.beans_cy - 72))

    def _draw_feedback_ok(self, surface, sx):
        msgs = ["Round 1 done! 🎯", "Round 2 done! 🌟", "All 3 rounds! 💕"]
        msg  = msgs[min(self.round_idx, 2)]
        m    = self.f_cmd.render(msg, True, DARK_BROWN)
        card = pygame.Surface((m.get_width() + 44, 52), pygame.SRCALPHA)
        pygame.draw.rect(card, (*SOFT_PINK, 210), (0, 0, card.get_width(), 52), border_radius=14)
        surface.blit(card, (self.w // 2 - card.get_width() // 2 + sx, self.beans_cy - 108))
        surface.blit(m,    (self.w // 2 - m.get_width() // 2 + sx,    self.beans_cy - 100))

    def _draw_feedback_fail(self, surface, sx):
        m    = self.f_cmd.render("Oops! Watch again... 👀", True, NOPE_RED)
        card = pygame.Surface((m.get_width() + 44, 52), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 200, 200, 210), (0, 0, card.get_width(), 52), border_radius=14)
        surface.blit(card, (self.w // 2 - card.get_width() // 2 + sx, self.beans_cy - 108))
        surface.blit(m,    (self.w // 2 - m.get_width() // 2 + sx,    self.beans_cy - 100))

    def _draw_level_clear(self, surface):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((*SOFT_PINK, min(185, self.clear_alpha)))
        surface.blit(overlay, (0, 0))
        if self.clear_alpha > 80:
            big = self.f_big.render("Level 2 Complete! 🐾", True, DARK_BROWN)
            big.set_alpha(min(255, self.clear_alpha))
            surface.blit(big, (self.w // 2 - big.get_width() // 2, self.h // 2 - 65))
            sub = self.f_sub.render("Beans is a very good girl.", True, MID_BROWN)
            sub.set_alpha(min(255, self.clear_alpha))
            surface.blit(sub, (self.w // 2 - sub.get_width() // 2, self.h // 2 + 10))
            if int(self.clear_timer * 2) % 2 == 0:
                cont = self.f_hint.render("Press any key to continue →", True, MID_BROWN)
                surface.blit(cont, (self.w // 2 - cont.get_width() // 2, self.h // 2 + 55))

    def _draw_seq_dots(self, surface, sx, filled_up_to=-1, y=None, show_remaining=False):
        """Draw coloured dots for the current round's command sequence."""
        n    = len(self.current_round)
        y    = y or (self.beans_cy - 148)
        step = 28
        for i, cmd in enumerate(self.current_round):
            dx = self.w // 2 + (i - n // 2) * step + (step // 2 if n % 2 == 0 else 0) + sx
            if i <= filled_up_to:
                col = CMD_COLOR[cmd]
            elif show_remaining:
                col = CREAM_DARK
            else:
                col = CREAM_DARK
            pygame.draw.circle(surface, col, (dx, y), 9)
            pygame.draw.circle(surface, AMBER_DARK, (dx, y), 9, 1)

    def _draw_buttons(self, surface, sx=0):
        active = self.state == self.PLAYER_TURN
        for cmd, rect in self.btn_rects.items():
            r    = pygame.Rect(rect.x + sx, rect.y, rect.width, rect.height)
            col  = CMD_COLOR[cmd]
            a    = 240 if active else 90
            surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*col, a), (0, 0, rect.width, rect.height), border_radius=14)
            if active:
                pygame.draw.rect(surf, (*AMBER_DARK, 180), (0, 0, rect.width, rect.height),
                                 width=2, border_radius=14)
            # Flash highlight briefly after click
            if active and cmd == self.last_clicked:
                pygame.draw.rect(surf, (255, 255, 255, 110), (0, 0, rect.width, rect.height),
                                 border_radius=14)
            surface.blit(surf, r)
            lbl = self.f_btn.render(f"{CMD_EMOJI[cmd]}  {cmd}", True,
                                    DARK_BROWN if active else (180, 160, 140))
            surface.blit(lbl, (r.x + rect.width // 2 - lbl.get_width() // 2,
                                r.y + rect.height // 2 - lbl.get_height() // 2))
