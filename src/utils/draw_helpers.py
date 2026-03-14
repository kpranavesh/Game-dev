import pygame
import math
from src.utils.constants import SHADOW_COLOR


def draw_rounded_rect(surface, color, rect, radius=18, shadow=True, shadow_offset=4):
    """Draw a rounded rectangle with optional drop shadow."""
    if shadow:
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*SHADOW_COLOR, 50), (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_cute_face(surface, cx, cy, scale=1.0, skin=(220, 175, 130),
                   hair=(60, 40, 20), hair_style=0, blush=True):
    """Draw a chibi-style face at (cx, cy) with given scale."""
    r = int(45 * scale)

    # Head
    pygame.draw.circle(surface, skin, (cx, cy), r)
    pygame.draw.circle(surface, (max(0, skin[0]-30), max(0, skin[1]-25), max(0, skin[2]-20)), (cx, cy), r, 2)

    # Hair base (behind head - top arc)
    hair_rect = pygame.Rect(cx - r - 4, cy - r - 8, (r + 4) * 2, r + 10)
    pygame.draw.ellipse(surface, hair, hair_rect)

    # Hair style variations
    if hair_style == 0:  # Straight/short
        pygame.draw.rect(surface, hair, (cx - r - 4, cy - r - 8, (r + 4) * 2, 20))
    elif hair_style == 1:  # Wavy/longer sides
        for side in [-1, 1]:
            pts = [(cx + side * (r + 2), cy - r + 10),
                   (cx + side * (r + 12), cy - 5),
                   (cx + side * (r + 8), cy + 15)]
            pygame.draw.polygon(surface, hair, pts)
    elif hair_style == 2:  # Messy/spiky top
        for i in range(5):
            angle = -90 + (i - 2) * 25
            ex = cx + int(math.cos(math.radians(angle)) * (r + 12))
            ey = cy + int(math.sin(math.radians(angle)) * (r + 12))
            pygame.draw.line(surface, hair, (cx + int(math.cos(math.radians(angle)) * r),
                                             cy + int(math.sin(math.radians(angle)) * r)),
                             (ex, ey), 6)
    elif hair_style == 3:  # Curly
        pygame.draw.arc(surface, hair, pygame.Rect(cx - r - 8, cy - r - 14, 20, 20), 0, math.pi, 6)
        pygame.draw.arc(surface, hair, pygame.Rect(cx - 4, cy - r - 14, 20, 20), 0, math.pi, 6)
        pygame.draw.arc(surface, hair, pygame.Rect(cx + r - 10, cy - r - 14, 20, 20), 0, math.pi, 6)
    elif hair_style == 4:  # Long dark hair (Krishna)
        for side in [-1, 1]:
            pts = [(cx + side * r, cy - r + 5),
                   (cx + side * (r + 15), cy + 20),
                   (cx + side * (r + 10), cy + r + 10),
                   (cx + side * (r - 5), cy + r - 5)]
            pygame.draw.polygon(surface, hair, pts)
        pygame.draw.rect(surface, hair, (cx - r, cy - r - 5, r * 2, 22))

    # Eyes
    eye_y = cy - int(5 * scale)
    eye_r = max(4, int(7 * scale))
    for ex in [cx - int(14 * scale), cx + int(14 * scale)]:
        pygame.draw.circle(surface, (255, 255, 255), (ex, eye_y), eye_r)
        pygame.draw.circle(surface, (50, 35, 20), (ex, eye_y), eye_r - 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex + 2, eye_y - 2), 2)  # shine

    # Nose (tiny dot)
    pygame.draw.circle(surface, (max(0, skin[0]-45), max(0, skin[1]-40), max(0, skin[2]-35)), (cx, cy + int(6 * scale)), 2)

    # Mouth (small smile)
    mouth_w = int(16 * scale)
    pygame.draw.arc(surface, (180, 80, 80),
                    pygame.Rect(cx - mouth_w//2, cy + int(10 * scale), mouth_w, int(10 * scale)),
                    math.pi + 0.3, 2 * math.pi - 0.3, 2)

    # Blush
    if blush:
        blush_surf = pygame.Surface((20, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(blush_surf, (255, 150, 150, 80), (0, 0, 20, 12))
        for bx in [cx - int(22 * scale), cx + int(10 * scale)]:
            surface.blit(blush_surf, (bx, eye_y + 5))


def _beans_head(surface, cx, cy, scale, tongue=True, happy=False):
    """Draw Beans' tricolor head (black/white/tan) at (cx, cy). Tongue always out — it's Beans."""
    BC_BLACK = (28, 22, 16)
    BC_WHITE = (248, 245, 238)
    BC_TAN   = (162, 98, 38)
    BC_PINK  = (255, 155, 165)

    r = int(34 * scale)
    s = scale

    # --- Floppy ears (drawn first, behind head) ---
    for side in [-1, 1]:
        ear = [
            (cx + side * int(22*s), cy - int(20*s)),
            (cx + side * int(40*s), cy + int(5*s)),
            (cx + side * int(38*s), cy + int(30*s)),
            (cx + side * int(20*s), cy + int(28*s)),
            (cx + side * int(14*s), cy + int(8*s)),
        ]
        pygame.draw.polygon(surface, BC_BLACK, ear)
        # Tan inner ear
        inner = [
            (cx + side * int(24*s), cy - int(10*s)),
            (cx + side * int(36*s), cy + int(8*s)),
            (cx + side * int(33*s), cy + int(26*s)),
            (cx + side * int(20*s), cy + int(24*s)),
            (cx + side * int(16*s), cy + int(10*s)),
        ]
        pygame.draw.polygon(surface, BC_TAN, inner)

    # --- Skull (black) ---
    pygame.draw.circle(surface, BC_BLACK, (cx, cy), r)

    # --- Tan patches on sides of face / cheeks ---
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, BC_TAN,
                            pygame.Rect(cx + side*int(10*s) - int(12*s),
                                        cy - int(4*s), int(22*s), int(20*s)))

    # --- White blaze (wide, Beans has a lot of white on her face) ---
    pygame.draw.ellipse(surface, BC_WHITE,
                        pygame.Rect(cx - int(12*s), cy - r + int(4*s),
                                    int(24*s), int(r*2 - int(4*s))))

    # --- Tan eyebrow dots (very characteristic) ---
    for side in [-1, 1]:
        pygame.draw.circle(surface, BC_TAN,
                           (cx + side * int(14*s), cy - int(16*s)), int(5*s))

    # --- Eyes ---
    for side in [-1, 1]:
        ex = cx + side * int(13*s)
        ey = cy - int(8*s)
        pygame.draw.circle(surface, BC_WHITE, (ex, ey), int(7*s))
        pygame.draw.circle(surface, (38, 26, 14), (ex, ey), int(5*s))
        pygame.draw.circle(surface, BC_WHITE, (ex + int(2*s), ey - int(2*s)), max(1, int(2*s)))

    # --- Wide white muzzle ---
    muz_cy = cy + int(12*s)
    pygame.draw.ellipse(surface, BC_WHITE,
                        pygame.Rect(cx - int(16*s), muz_cy - int(12*s),
                                    int(32*s), int(24*s)))

    # --- Big dark nose ---
    pygame.draw.ellipse(surface, (14, 9, 6),
                        pygame.Rect(cx - int(9*s), muz_cy - int(10*s),
                                    int(18*s), int(11*s)))
    # Nose shine
    pygame.draw.circle(surface, (80, 60, 55),
                       (cx - int(3*s), muz_cy - int(8*s)), max(1, int(2*s)))

    # --- Big tongue (Beans' signature — always out) ---
    tw, th = int(16*s), int(22*s)
    t_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.ellipse(t_surf, (*BC_PINK, 235), (0, 0, tw, th))
    pygame.draw.line(t_surf, (210, 105, 125), (tw//2, 0), (tw//2, th), max(1, int(2*s)))
    surface.blit(t_surf, (cx - tw//2, muz_cy + int(4*s)))

    # --- Happy blush ---
    if happy:
        for side in [-1, 1]:
            b = pygame.Surface((int(20*s), int(10*s)), pygame.SRCALPHA)
            pygame.draw.ellipse(b, (255, 130, 130, 90), (0, 0, int(20*s), int(10*s)))
            surface.blit(b, (cx + side*int(14*s) - int(10*s), muz_cy - int(14*s)))


def draw_vandita(surface, cx, cy, scale=1.0, looking_down=False, legs_apart=False):
    """Chibi Vandita — dark long hair, sunglasses on head, burgundy dress."""
    SKIN     = (195, 150, 108)
    HAIR     = (32, 20, 12)
    DRESS    = (158, 55, 45)
    SUNGLASS = (40, 30, 20)
    SG_LENS  = (80, 60, 45)
    s = scale

    head_r = int(22 * s)
    hcx, hcy = cx, cy - int(60 * s)

    # ── Long hair behind head ──
    for side in [-1, 1]:
        hair_pts = [
            (hcx + side * head_r, hcy - int(8*s)),
            (hcx + side * int((head_r+10)*s), hcy + int(20*s)),
            (hcx + side * int((head_r+8)*s),  hcy + int(70*s)),
            (hcx + side * int((head_r-4)*s),  hcy + int(72*s)),
        ]
        pygame.draw.polygon(surface, HAIR, hair_pts)
    pygame.draw.rect(surface, HAIR,
                     pygame.Rect(hcx - head_r, hcy - head_r - int(4*s), head_r*2, int(head_r + 6*s)))

    # ── Head ──
    pygame.draw.circle(surface, SKIN, (hcx, hcy), head_r)

    # ── Sunglasses on top of head (signature) ──
    sg_y = hcy - head_r + int(2*s)
    for side in [-1, 1]:
        pygame.draw.ellipse(surface, SG_LENS,
                            pygame.Rect(hcx + side*int(6*s) - int(8*s), sg_y - int(5*s), int(14*s), int(8*s)))
        pygame.draw.ellipse(surface, SUNGLASS,
                            pygame.Rect(hcx + side*int(6*s) - int(8*s), sg_y - int(5*s), int(14*s), int(8*s)), 1)
    pygame.draw.line(surface, SUNGLASS,
                     (hcx - int(2*s), sg_y - int(2*s)), (hcx + int(2*s), sg_y - int(2*s)), max(1, int(2*s)))

    # ── Eyes ──
    eye_y = hcy + int(2*s) if not looking_down else hcy + int(6*s)
    for side in [-1, 1]:
        ex = hcx + side * int(9*s)
        if looking_down:
            # Curved happy eyes when looking down at Beans
            pygame.draw.arc(surface, (38, 26, 14),
                            pygame.Rect(ex - int(5*s), eye_y - int(4*s), int(10*s), int(8*s)),
                            0, math.pi, max(1, int(2*s)))
        else:
            pygame.draw.circle(surface, (255, 255, 255), (ex, eye_y), int(5*s))
            pygame.draw.circle(surface, (38, 26, 14), (ex, eye_y), int(3*s))
            pygame.draw.circle(surface, (255, 255, 255), (ex+1, eye_y-1), 1)

    # ── Blush ──
    for side in [-1, 1]:
        b = pygame.Surface((int(12*s), int(7*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(b, (240, 140, 130, 100), (0, 0, int(12*s), int(7*s)))
        surface.blit(b, (hcx + side*int(8*s) - int(6*s), eye_y + int(4*s)))

    # ── Smile ──
    pygame.draw.arc(surface, (180, 70, 70),
                    pygame.Rect(hcx - int(8*s), hcy + int(8*s), int(16*s), int(10*s)),
                    math.pi + 0.4, 2*math.pi - 0.4, max(1, int(2*s)))

    # ── Neck ──
    pygame.draw.rect(surface, SKIN,
                     pygame.Rect(hcx - int(6*s), hcy + head_r - int(2*s), int(12*s), int(12*s)))

    # ── Strapless burgundy dress (body) ──
    body_top = hcy + head_r + int(10*s)
    body_h   = int(70 * s)
    pygame.draw.rect(surface, DRESS,
                     pygame.Rect(cx - int(20*s), body_top, int(40*s), body_h), border_radius=int(6*s))
    # Dress neckline (straight across)
    pygame.draw.line(surface, (130, 40, 30),
                     (cx - int(20*s), body_top + int(3*s)), (cx + int(20*s), body_top + int(3*s)),
                     max(1, int(2*s)))

    # ── Arms ──
    arm_y = body_top + int(14*s)
    for side in [-1, 1]:
        ax_end = cx + side * int(30*s)
        ay_end = arm_y + int(16*s)
        pygame.draw.line(surface, SKIN, (cx + side*int(18*s), arm_y),
                         (ax_end, ay_end), max(2, int(4*s)))
        pygame.draw.circle(surface, SKIN, (ax_end, ay_end), int(4*s))

    # ── Legs (apart if legs_apart, else together) ──
    leg_top = body_top + body_h
    if legs_apart:
        leg_offsets = [-int(18*s), int(18*s)]
    else:
        leg_offsets = [-int(8*s), int(8*s)]
    for lx in leg_offsets:
        leg_bot = leg_top + int(38*s)
        pygame.draw.line(surface, DRESS, (cx + lx, leg_top), (cx + lx, leg_top + int(20*s)),
                         max(2, int(8*s)))
        pygame.draw.line(surface, SKIN, (cx + lx, leg_top + int(20*s)), (cx + lx, leg_bot),
                         max(2, int(6*s)))
        # Sandal
        pygame.draw.ellipse(surface, (180, 130, 80),
                            pygame.Rect(cx + lx - int(8*s), leg_bot - int(3*s), int(16*s), int(7*s)))


def draw_krishna(surface, cx, cy, scale=1.0, looking_down=False, legs_apart=False):
    """Chibi Krishna — white shirt, black pants, short dark hair, taller than Vandita."""
    SKIN   = (195, 150, 108)
    HAIR   = (32, 20, 12)
    SHIRT  = (245, 245, 242)
    PANTS  = (28, 24, 20)
    s = scale

    head_r = int(22 * s)
    hcx, hcy = cx, cy - int(70 * s)   # taller than Vandita (who uses -60)

    # ── Short dark hair ──
    pygame.draw.ellipse(surface, HAIR,
                        pygame.Rect(hcx - head_r - int(2*s), hcy - head_r - int(6*s),
                                    (head_r + int(2*s)) * 2, int(head_r + 4*s)))
    pygame.draw.rect(surface, HAIR,
                     pygame.Rect(hcx - head_r - int(2*s), hcy - head_r - int(6*s),
                                 (head_r + int(2*s)) * 2, int(14*s)))

    # ── Head ──
    pygame.draw.circle(surface, SKIN, (hcx, hcy), head_r)

    # ── Eyes ──
    eye_y = hcy + int(2*s) if not looking_down else hcy + int(6*s)
    for side in [-1, 1]:
        ex = hcx + side * int(9*s)
        if looking_down:
            pygame.draw.arc(surface, (38, 26, 14),
                            pygame.Rect(ex - int(5*s), eye_y - int(4*s), int(10*s), int(8*s)),
                            0, math.pi, max(1, int(2*s)))
        else:
            pygame.draw.circle(surface, (255, 255, 255), (ex, eye_y), int(5*s))
            pygame.draw.circle(surface, (38, 26, 14), (ex, eye_y), int(3*s))
            pygame.draw.circle(surface, (255, 255, 255), (ex+1, eye_y-1), 1)

    # ── Blush ──
    for side in [-1, 1]:
        b = pygame.Surface((int(12*s), int(7*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(b, (240, 140, 130, 100), (0, 0, int(12*s), int(7*s)))
        surface.blit(b, (hcx + side*int(8*s) - int(6*s), eye_y + int(4*s)))

    # ── Smile ──
    pygame.draw.arc(surface, (180, 70, 70),
                    pygame.Rect(hcx - int(8*s), hcy + int(8*s), int(16*s), int(10*s)),
                    math.pi + 0.4, 2*math.pi - 0.4, max(1, int(2*s)))

    # ── Neck ──
    pygame.draw.rect(surface, SKIN,
                     pygame.Rect(hcx - int(6*s), hcy + head_r - int(2*s), int(12*s), int(12*s)))

    # ── White shirt body ──
    body_top = hcy + head_r + int(10*s)
    body_h   = int(65 * s)
    pygame.draw.rect(surface, SHIRT,
                     pygame.Rect(cx - int(20*s), body_top, int(40*s), body_h), border_radius=int(4*s))
    # Collar line
    pygame.draw.line(surface, (210, 210, 208),
                     (cx - int(8*s), body_top + int(2*s)), (cx + int(8*s), body_top + int(2*s)),
                     max(1, int(1*s)))

    # ── Arms ──
    arm_y = body_top + int(12*s)
    for side in [-1, 1]:
        ax_end = cx + side * int(30*s)
        ay_end = arm_y + int(18*s)
        pygame.draw.line(surface, SHIRT, (cx + side*int(18*s), arm_y),
                         (ax_end, ay_end), max(2, int(5*s)))
        pygame.draw.circle(surface, SKIN, (ax_end, ay_end), int(4*s))

    # ── Black pants + legs ──
    leg_top = body_top + body_h
    if legs_apart:
        leg_offsets = [-int(18*s), int(18*s)]
    else:
        leg_offsets = [-int(8*s), int(8*s)]
    for lx in leg_offsets:
        leg_bot = leg_top + int(42*s)   # slightly longer legs than Vandita
        pygame.draw.line(surface, PANTS, (cx + lx, leg_top), (cx + lx, leg_bot),
                         max(2, int(8*s)))
        # Shoe
        pygame.draw.ellipse(surface, (22, 18, 14),
                            pygame.Rect(cx + lx - int(9*s), leg_bot - int(4*s), int(18*s), int(8*s)))


def draw_food_bowl(surface, cx, cy, scale=1.0, fill_ratio=1.0):
    """Draw a cute dog food bowl with BEANS written on it and kibble."""
    s = scale
    BOWL_GRAY  = (140, 135, 130)
    BOWL_DARK  = (100, 95, 90)
    KIBBLE_1   = (180, 130, 70)
    KIBBLE_2   = (200, 155, 90)

    bw, bh = int(52*s), int(20*s)
    # Bowl shadow
    shd = pygame.Surface((bw + int(6*s), int(10*s)), pygame.SRCALPHA)
    pygame.draw.ellipse(shd, (0, 0, 0, 40), (0, 0, bw + int(6*s), int(10*s)))
    surface.blit(shd, (cx - bw//2 - int(3*s), cy + bh - int(4*s)))
    # Bowl body
    pygame.draw.ellipse(surface, BOWL_GRAY, pygame.Rect(cx - bw//2, cy, bw, bh))
    pygame.draw.ellipse(surface, BOWL_DARK, pygame.Rect(cx - bw//2, cy, bw, bh), max(1, int(2*s)))
    # Rim highlight
    pygame.draw.ellipse(surface, (200, 195, 190),
                        pygame.Rect(cx - bw//2 + int(4*s), cy + int(2*s), bw - int(8*s), int(8*s)))
    # Kibble (shown if fill_ratio > 0)
    if fill_ratio > 0:
        for i in range(int(8 * fill_ratio)):
            kx = cx + int(math.cos(i * 0.8) * 14 * s)
            ky = cy + int(6*s) + int(math.sin(i * 1.1) * 3 * s)
            col = KIBBLE_1 if i % 2 == 0 else KIBBLE_2
            pygame.draw.ellipse(surface, col,
                                pygame.Rect(kx - int(5*s), ky - int(3*s), int(10*s), int(6*s)))
    # "BEANS" label on bowl
    try:
        font = pygame.font.SysFont("Arial", max(8, int(9*s)), bold=True)
        lbl = font.render("BEANS", True, BOWL_DARK)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy + int(8*s)))
    except Exception:
        pass


def draw_border_collie(surface, cx, cy, scale=1.0, happy=False, tongue=False, pose="middle",
                       pose_elapsed_ms=9999):
    """
    Draw Beans — tricolor border collie mix (black/white/tan).
    Poses: 'sit', 'down', 'free' (food bowl + eating), 'middle' (between Vandita's legs)
    pose_elapsed_ms: milliseconds since this pose was triggered (drives sequenced animations)
    """
    BC_BLACK = (28, 22, 16)
    BC_WHITE = (248, 245, 238)
    BC_TAN   = (162, 98, 38)
    s = scale
    t = pygame.time.get_ticks()

    if pose == "sit":
        # ── SIT: haunches on ground, front paws forward, body compact ──────────
        # Body: wide low ellipse (haunches spread)
        bx, by = cx, cy + int(55*s)
        pygame.draw.ellipse(surface, BC_BLACK,
                            pygame.Rect(bx - int(38*s), by - int(16*s), int(76*s), int(32*s)))
        # White chest
        pygame.draw.ellipse(surface, BC_WHITE,
                            pygame.Rect(bx - int(18*s), by - int(18*s), int(36*s), int(28*s)))
        # Tail curled behind (short, to the right, low wag)
        wag = math.sin(t * 0.006) * 6
        tail = [(bx+int(36*s), by-int(6*s)),
                (bx+int(48*s), by+int(4*s)+int(wag*s)),
                (bx+int(42*s), by+int(16*s))]
        pygame.draw.lines(surface, BC_BLACK, False, tail, max(2, int(6*s)))
        pygame.draw.circle(surface, BC_WHITE, tail[-1], int(4*s))
        # Two front paws side by side, pointing forward
        for px in [bx - int(14*s), bx + int(14*s)]:
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(px - int(10*s), by + int(14*s), int(20*s), int(14*s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(px - int(7*s), by + int(22*s), int(14*s), int(6*s)))
        # Tan neck/saddle
        pygame.draw.ellipse(surface, BC_TAN,
                            pygame.Rect(bx - int(10*s), by - int(22*s), int(20*s), int(16*s)))
        # Head — upright, ears perked
        _beans_head(surface, cx, cy + int(4*s), scale * 0.92, tongue=True, happy=happy)

    elif pose == "down":
        # ── DOWN: completely flat, body horizontal, head resting low ────────────
        # Long flat body stretched left-right
        bx, by = cx, cy + int(68*s)
        pygame.draw.ellipse(surface, BC_BLACK,
                            pygame.Rect(bx - int(52*s), by - int(13*s), int(104*s), int(26*s)))
        # White underbelly stripe
        pygame.draw.ellipse(surface, BC_WHITE,
                            pygame.Rect(bx - int(32*s), by - int(8*s), int(64*s), int(16*s)))
        # Tan saddle patch
        pygame.draw.ellipse(surface, BC_TAN,
                            pygame.Rect(bx - int(20*s), by - int(12*s), int(40*s), int(14*s)))
        # Tail flat to the right, barely wagging
        wag = math.sin(t * 0.003) * 4
        tail = [(bx+int(50*s), by),
                (bx+int(62*s), by - int(5*s) + int(wag*s)),
                (bx+int(70*s), by - int(10*s))]
        pygame.draw.lines(surface, BC_BLACK, False, tail, max(2, int(6*s)))
        pygame.draw.circle(surface, BC_WHITE, tail[-1], int(4*s))
        # Front paws stretched forward
        for px in [bx - int(38*s), bx - int(18*s)]:
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(px - int(10*s), by + int(10*s), int(20*s), int(10*s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(px - int(6*s), by + int(15*s), int(12*s), int(5*s)))
        # Head resting low, facing forward
        _beans_head(surface, cx - int(20*s), cy + int(42*s), scale * 0.85, tongue=True, happy=happy)

    elif pose == "free":
        # ── FREE: food bowl appears, Beans dashes and eats ─────────────────────
        # Phase 0–400ms: Beans trembles in place, staring at bowl (holding)
        # Phase 400–900ms: Beans dashes toward bowl with speed lines
        # Phase 900ms+:    Beans eats, head bobs, tail goes wild
        phase = pose_elapsed_ms
        bowl_x = cx + int(90 * s)
        bowl_y = cy + int(72 * s)

        # Bowl is always visible
        draw_food_bowl(surface, bowl_x, bowl_y, scale=s * 0.9,
                       fill_ratio=1.0 if phase < 900 else max(0.0, 1.0 - (phase - 900) / 3000))

        if phase < 400:
            # Trembling wait — body vibrates slightly, eyes locked on bowl
            shake = int(math.sin(t * 0.04) * 3 * s)
            bx, by = cx + shake, cy + int(52*s)
            # Body
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(bx - int(30*s), by - int(24*s), int(60*s), int(44*s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(bx - int(16*s), by - int(20*s), int(32*s), int(34*s)))
            pygame.draw.ellipse(surface, BC_TAN,
                                pygame.Rect(bx - int(18*s), by - int(22*s), int(36*s), int(18*s)))
            # Legs (tense, stiff)
            for px in [bx - int(14*s), bx + int(14*s), bx - int(20*s), bx + int(20*s)]:
                pygame.draw.line(surface, BC_BLACK,
                                 (px, by + int(10*s)), (px, by + int(38*s)), max(2, int(5*s)))
                pygame.draw.ellipse(surface, BC_BLACK,
                                    pygame.Rect(px - int(8*s), by + int(34*s), int(16*s), int(10*s)))
                pygame.draw.ellipse(surface, BC_WHITE,
                                    pygame.Rect(px - int(5*s), by + int(39*s), int(10*s), int(4*s)))
            # Tail barely moving (tense hold)
            wag = math.sin(t * 0.005) * 3
            tail = [(bx + int(28*s), by - int(14*s)),
                    (bx + int(38*s), by - int(20*s) + int(wag*s)),
                    (bx + int(42*s), by - int(28*s))]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(2, int(6*s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], int(4*s))
            # Head looking right at bowl — eyes eager
            _beans_head(surface, bx, cy, scale * 0.95, tongue=True, happy=False)
            # Drool drop (anticipation)
            drool_x = bx + int(14*s)
            drool_y = cy + int(32*s) + int(math.sin(t * 0.003) * 4 * s)
            pygame.draw.ellipse(surface, (180, 210, 240),
                                pygame.Rect(drool_x - int(3*s), drool_y, int(6*s), int(10*s)))
            # "Holding..." floating text
            try:
                f = pygame.font.SysFont("Georgia", max(12, int(14*s)), italic=True)
                lbl = f.render("holding...", True, (160, 120, 80))
                alpha = int(128 + 100 * math.sin(t * 0.005))
                lbl.set_alpha(alpha)
                surface.blit(lbl, (cx - lbl.get_width()//2, cy - int(45*s)))
            except Exception:
                pass

        elif phase < 900:
            # DASH — Beans mid-sprint toward bowl, speed lines
            prog = min(1.0, (phase - 400) / 500)
            ease = 1 - (1 - prog) ** 3
            run_x = cx + int(ease * 55 * s)
            run_y = cy + int(52*s)
            bounce = int(math.sin(t * 0.025) * 6 * s)
            # Speed lines (blur streaks behind)
            for i in range(4):
                lx = run_x - int((30 + i*14) * s)
                ly = run_y - int((i * 5) * s) + bounce
                alpha = 200 - i * 45
                spd = pygame.Surface((int((20 + i*8)*s), max(1, int(3*s))), pygame.SRCALPHA)
                pygame.draw.rect(spd, (*BC_TAN, alpha), (0, 0, spd.get_width(), spd.get_height()))
                surface.blit(spd, (lx, ly))
            # Body tilted forward mid-gallop
            body_surf = pygame.Surface((int(72*s), int(44*s)), pygame.SRCALPHA)
            pygame.draw.ellipse(body_surf, (*BC_BLACK, 255), (0, 0, int(72*s), int(44*s)))
            pygame.draw.ellipse(body_surf, (*BC_WHITE, 255), (int(10*s), int(10*s), int(38*s), int(26*s)))
            pygame.draw.ellipse(body_surf, (*BC_TAN,  255), (int(16*s), int(6*s),  int(30*s), int(16*s)))
            rot = pygame.transform.rotate(body_surf, -18)
            surface.blit(rot, (run_x - rot.get_width()//2, run_y - rot.get_height()//2 + bounce))
            # Legs splayed
            for lx, ly in [(-int(24*s), int(22*s)), (-int(6*s), int(30*s)),
                           (int(10*s), int(28*s)), (int(26*s), int(16*s))]:
                pygame.draw.line(surface, BC_BLACK,
                                 (run_x + lx, run_y + int(8*s) + bounce),
                                 (run_x + lx + int(4*s), run_y + ly + bounce),
                                 max(2, int(5*s)))
                pygame.draw.ellipse(surface, BC_BLACK,
                                    pygame.Rect(run_x + lx - int(6*s), run_y + ly - int(4*s) + bounce,
                                                int(12*s), int(9*s)))
            # Tail streaming behind
            wag = math.sin(t * 0.02) * 20
            tail = [(run_x + int(24*s), run_y - int(10*s) + bounce),
                    (run_x + int(38*s), run_y - int(24*s) + int(wag*s)),
                    (run_x + int(44*s), run_y - int(36*s) + int(wag*1.3*s))]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(2, int(6*s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], int(4*s))
            _beans_head(surface, run_x - int(12*s), cy + int(4*s) + bounce,
                        scale * 0.9, tongue=True, happy=True)

        else:
            # EATING — head bobs into bowl, tail goes crazy
            bob = int(abs(math.sin(t * 0.015)) * 14 * s)
            eat_x = bowl_x - int(10*s)
            eat_y = cy + int(52*s)
            # Body near bowl
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(eat_x - int(30*s), eat_y - int(24*s), int(60*s), int(44*s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(eat_x - int(16*s), eat_y - int(20*s), int(32*s), int(34*s)))
            pygame.draw.ellipse(surface, BC_TAN,
                                pygame.Rect(eat_x - int(18*s), eat_y - int(22*s), int(36*s), int(18*s)))
            # Paws
            for px in [eat_x - int(14*s), eat_x + int(14*s)]:
                pygame.draw.line(surface, BC_BLACK,
                                 (px, eat_y + int(10*s)), (px, eat_y + int(38*s)), max(2, int(5*s)))
                pygame.draw.ellipse(surface, BC_BLACK,
                                    pygame.Rect(px - int(9*s), eat_y + int(34*s), int(18*s), int(11*s)))
                pygame.draw.ellipse(surface, BC_WHITE,
                                    pygame.Rect(px - int(6*s), eat_y + int(39*s), int(12*s), int(5*s)))
            # Tail waggling furiously
            wag = math.sin(t * 0.022) * 22
            tail = [(eat_x + int(28*s), eat_y - int(14*s)),
                    (eat_x + int(42*s), eat_y - int(20*s) + int(wag*s)),
                    (eat_x + int(50*s), eat_y - int(30*s) + int(wag*1.5*s))]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(2, int(7*s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], int(5*s))
            # Head bobbing into bowl
            _beans_head(surface, eat_x - int(4*s), cy - int(8*s) + bob,
                        scale * 0.88, tongue=True, happy=True)
            # NOM sparkles
            for i in range(3):
                ang = t * 0.004 + i * 2.1
                sx2 = eat_x + int(math.cos(ang) * 28 * s)
                sy2 = bowl_y - int(20*s) + int(math.sin(ang) * 12 * s)
                try:
                    f2 = pygame.font.SysFont("Arial", max(9, int(11*s)), bold=True)
                    nom = f2.render("nom", True, (210, 140, 60))
                    nom.set_alpha(180)
                    surface.blit(nom, (sx2, sy2))
                except Exception:
                    pass

    else:
        # ── MIDDLE: Beans comes from behind Vandita and pushes through her legs ──
        # Phase 0–500ms:   Vandita walks in from right, plants with legs wide open
        # Phase 500–900ms: Beans trots in from behind-right, approaches the leg gap
        # Phase 900–1300ms: Beans ducks low and pushes THROUGH the leg gap (left to right)
        # Phase 1300ms+:   Beans sits between legs facing forward, Vandita looks down, hearts

        human_s = s * 0.90
        beans_s = s * 0.42          # noticeably small dog vs adult

        # Vandita stands slightly left of center so there's space to see the action
        v_cx    = cx - int(10 * s)
        v_cy    = cy + int(20 * s)
        # Leg gap positions (matches draw_vandita legs_apart offsets at human_s)
        leg_gap_left  = v_cx - int(18 * human_s)
        leg_gap_right = v_cx + int(18 * human_s)
        leg_gap_mid   = (leg_gap_left + leg_gap_right) // 2
        # Floor level where Beans sits (between Vandita's ankles)
        floor_y = v_cy + int(20 * s)   # approximate ankle height for human_s figure

        if pose_elapsed_ms < 500:
            # Vandita slides in from right, Beans waits off to the right (behind)
            prog = min(1.0, pose_elapsed_ms / 500)
            ease = 1 - (1 - prog) ** 3
            v_draw_x = int(v_cx + (150 * s) * (1 - ease))
            draw_vandita(surface, v_draw_x, v_cy, scale=human_s,
                         looking_down=False, legs_apart=True)
            # Beans visible off to the right (behind Vandita's entry side)
            bx = int(cx + 130 * s)
            by = floor_y - int(24 * beans_s)
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(bx - int(28*beans_s), by, int(56*beans_s), int(40*beans_s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(bx - int(14*beans_s), by + int(4*beans_s),
                                            int(28*beans_s), int(30*beans_s)))
            _beans_head(surface, bx - int(10*beans_s), by - int(24*beans_s),
                        beans_s * 0.9, tongue=True, happy=False)

        elif pose_elapsed_ms < 900:
            # Vandita fully planted. Beans trots toward the leg gap from the right/behind.
            prog = min(1.0, (pose_elapsed_ms - 500) / 400)
            ease = 1 - (1 - prog) ** 2
            # Beans moves from right side toward the right leg
            start_x = int(cx + 130 * s)
            beans_x = int(start_x + (leg_gap_right - start_x) * ease)
            trot = int(math.sin(t * 0.025) * 5 * beans_s)
            draw_vandita(surface, v_cx, v_cy, scale=human_s,
                         looking_down=False, legs_apart=True)
            by = floor_y - int(24 * beans_s)
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(beans_x - int(28*beans_s), by + trot,
                                            int(56*beans_s), int(40*beans_s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(beans_x - int(14*beans_s), by + int(4*beans_s) + trot,
                                            int(28*beans_s), int(30*beans_s)))
            # Tail trotting
            wag = math.sin(t * 0.018) * 12
            tail = [(beans_x + int(26*beans_s), by + trot),
                    (beans_x + int(38*beans_s), by - int(12*beans_s) + int(wag*beans_s) + trot),
                    (beans_x + int(42*beans_s), by - int(24*beans_s) + int(wag*1.4*beans_s) + trot)]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(1, int(5*beans_s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], max(1, int(3*beans_s)))
            _beans_head(surface, beans_x - int(8*beans_s), by - int(24*beans_s) + trot,
                        beans_s * 0.9, tongue=True, happy=True)
            # "Here she comes!" hint
            try:
                fh = pygame.font.SysFont("Georgia", max(11, int(13*s)), italic=True)
                hint = fh.render("here she comes...", True, (140, 100, 60))
                hint.set_alpha(int(180 * ease))
                surface.blit(hint, (surface.get_width()//2 - hint.get_width()//2,
                                    v_cy - int(80*s)))
            except Exception:
                pass

        elif pose_elapsed_ms < 1300:
            # DUCK THROUGH — Beans crouches low and pushes through the gap
            prog = min(1.0, (pose_elapsed_ms - 900) / 400)
            ease = prog * prog  # ease-in: slow start, accelerates through
            # Beans moves from right leg position to center of gap
            beans_x = int(leg_gap_right + (leg_gap_mid - leg_gap_right) * ease)
            # Beans crouches — body gets lower and flatter as she squeezes through
            crouch = int(ease * 12 * beans_s)   # how much she compresses vertically
            by = floor_y - int(18 * beans_s) + crouch
            draw_vandita(surface, v_cx, v_cy, scale=human_s,
                         looking_down=False, legs_apart=True)
            # Flat crouching body (wider, lower)
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(beans_x - int(34*beans_s), by,
                                            int(68*beans_s), int(28*beans_s) - crouch))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(beans_x - int(18*beans_s), by + int(4*beans_s),
                                            int(36*beans_s), int(18*beans_s) - crouch//2))
            # Head lower, pushing through
            head_bob = int(math.sin(t * 0.02) * 3 * beans_s)
            _beans_head(surface, beans_x - int(14*beans_s), by - int(18*beans_s) + head_bob,
                        beans_s * 0.88, tongue=True, happy=True)
            # Tail still visible on entry side
            wag = math.sin(t * 0.02) * 10
            tail = [(beans_x + int(32*beans_s), by + int(4*beans_s)),
                    (beans_x + int(46*beans_s), by - int(4*beans_s) + int(wag*beans_s)),
                    (beans_x + int(50*beans_s), by - int(14*beans_s))]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(1, int(5*beans_s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], max(1, int(3*beans_s)))
            # "squeeze" sparkle dots on the leg columns
            for lx in [leg_gap_left, leg_gap_right]:
                for i in range(3):
                    sp_y = floor_y - int((i * 14) * s)
                    sp_alpha = max(0, 200 - i * 60)
                    sp_surf = pygame.Surface((int(8*s), int(8*s)), pygame.SRCALPHA)
                    pygame.draw.circle(sp_surf, (255, 200, 120, sp_alpha),
                                       (int(4*s), int(4*s)), int(3*s))
                    surface.blit(sp_surf, (lx - int(4*s), sp_y - int(4*s)))

        else:
            # SETTLED — Beans sits between legs, Vandita looks down, hearts float
            draw_vandita(surface, v_cx, v_cy, scale=human_s,
                         looking_down=True, legs_apart=True)
            # Beans sitting between the legs, facing forward
            bx = leg_gap_mid
            by_base = floor_y - int(6 * beans_s)
            # Haunches (sit pose)
            pygame.draw.ellipse(surface, BC_BLACK,
                                pygame.Rect(bx - int(32*beans_s), by_base - int(12*beans_s),
                                            int(64*beans_s), int(24*beans_s)))
            pygame.draw.ellipse(surface, BC_WHITE,
                                pygame.Rect(bx - int(16*beans_s), by_base - int(14*beans_s),
                                            int(32*beans_s), int(22*beans_s)))
            pygame.draw.ellipse(surface, BC_TAN,
                                pygame.Rect(bx - int(10*beans_s), by_base - int(16*beans_s),
                                            int(20*beans_s), int(12*beans_s)))
            # Front paws
            for px in [bx - int(10*beans_s), bx + int(10*beans_s)]:
                pygame.draw.ellipse(surface, BC_BLACK,
                                    pygame.Rect(px - int(8*beans_s), by_base + int(10*beans_s),
                                                int(16*beans_s), int(10*beans_s)))
                pygame.draw.ellipse(surface, BC_WHITE,
                                    pygame.Rect(px - int(5*beans_s), by_base + int(16*beans_s),
                                                int(10*beans_s), int(4*beans_s)))
            # Happy fast tail wag
            wag = math.sin(t * 0.01) * 10
            tail = [(bx + int(30*beans_s), by_base - int(6*beans_s)),
                    (bx + int(42*beans_s), by_base + int(2*beans_s) + int(wag*beans_s)),
                    (bx + int(38*beans_s), by_base + int(12*beans_s))]
            pygame.draw.lines(surface, BC_BLACK, False, tail, max(1, int(5*beans_s)))
            pygame.draw.circle(surface, BC_WHITE, tail[-1], max(1, int(3*beans_s)))
            _beans_head(surface, bx, by_base - int(28*beans_s), beans_s * 0.88,
                        tongue=True, happy=True)
            # Floating hearts
            age = pose_elapsed_ms - 1300
            for i in range(5):
                phase_i = (age * 0.001 + i * 0.6) % 2.8
                hx = bx + int(math.sin(i * 1.5) * 32 * s)
                hy = v_cy - int(60*s) - int(phase_i * 26 * s)
                h_alpha = max(0, int(220 - phase_i * 70))
                h_size  = max(4, int((8 - phase_i * 1.5) * s))
                if h_alpha > 0 and h_size > 2:
                    h_surf = pygame.Surface((h_size*4, h_size*4), pygame.SRCALPHA)
                    for a in range(0, 360, 4):
                        ang = math.radians(a)
                        hpx = h_size*2 + int(h_size * 1.2 * 16 * math.sin(ang)**3 / 16)
                        hpy = h_size*2 - int(h_size * 1.0 * (13*math.cos(ang) - 5*math.cos(2*ang)
                                             - 2*math.cos(3*ang) - math.cos(4*ang)) / 16)
                        if 0 <= hpx < h_size*4 and 0 <= hpy < h_size*4:
                            h_surf.set_at((hpx, hpy), (255, 100, 120, h_alpha))
                    surface.blit(h_surf, (hx - h_size*2, int(hy) - h_size*2))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    return 1 - (1 - t) ** 3
