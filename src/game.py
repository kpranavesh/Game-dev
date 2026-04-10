import pygame
from src.utils.constants import (
    SCREEN_W,
    SCREEN_H,
    FPS,
    TITLE,
    SCENE_TITLE,
    SCENE_LEVEL1,
    SCENE_LEVEL2,
    SCENE_LEVEL3,
    SCENE_LEVEL5,
    SCENE_LEVEL6,
    SCENE_COMING,
    SCENE_LEVEL7,
    SCENE_FINALE,
)
from src.scenes.title_screen import TitleScreen
from src.scenes.level1_hinge import Level1Hinge
from src.scenes.level2_beans import Level2Beans
from src.scenes.level3_yarn import Level3Yarn
from src.scenes.level5_beans_park import Level5BeansPark
from src.scenes.level6_proposal_park import Level6ProposalPark
from src.scenes.level7_kayak import Level7Kayak
from src.scenes.coming_soon import ComingSoonScreen
from src.scenes.level_finale import LevelFinale


class Game:
    def __init__(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
        pygame.init()
        from src.utils.sounds import init_sounds
        init_sounds()
        pygame.display.set_caption(TITLE)
        # Render at native res, scale to fullscreen
        self._render_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        info = pygame.display.Info()
        self._display_w = info.current_w
        self._display_h = info.current_h
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = TitleScreen(SCREEN_W, SCREEN_H)

    def _get_scene(self, name):
        if name == SCENE_TITLE:
            return TitleScreen(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL1:
            return Level1Hinge(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL2:
            return Level2Beans(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL3:
            return Level3Yarn(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL5:
            return Level5BeansPark(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL6:
            return Level6ProposalPark(SCREEN_W, SCREEN_H)
        elif name == SCENE_LEVEL7:
            return Level7Kayak(SCREEN_W, SCREEN_H)
        elif name == SCENE_COMING:
            return ComingSoonScreen(SCREEN_W, SCREEN_H)
        elif name == SCENE_FINALE:
            return LevelFinale(SCREEN_W, SCREEN_H)
        return TitleScreen(SCREEN_W, SCREEN_H)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    sx, sy = event.pos
                    scale = getattr(self, '_scale', 1)
                    ox = getattr(self, '_offset_x', 0)
                    oy = getattr(self, '_offset_y', 0)
                    mx = int((sx - ox) / scale) if scale else sx
                    my = int((sy - oy) / scale) if scale else sy
                    event = pygame.event.Event(
                        event.type,
                        pos=(mx, my),
                        button=event.button,
                    )
                self.scene.handle_event(event)

            self.scene.update(dt)

            if self.scene.next_scene:
                self.scene = self._get_scene(self.scene.next_scene)

            self.scene.draw(self._render_surface)
            # Scale to fit screen, maintain aspect ratio, center with black bars
            scale = min(self._display_w / SCREEN_W, self._display_h / SCREEN_H)
            self._scale = scale
            sw = int(SCREEN_W * scale)
            sh = int(SCREEN_H * scale)
            self._offset_x = (self._display_w - sw) // 2
            self._offset_y = (self._display_h - sh) // 2
            self.screen.fill((0, 0, 0))
            scaled = pygame.transform.scale(self._render_surface, (sw, sh))
            self.screen.blit(scaled, (self._offset_x, self._offset_y))
            pygame.display.flip()

        pygame.quit()
