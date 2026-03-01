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


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    return 1 - (1 - t) ** 3
