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
)
from src.scenes.title_screen import TitleScreen
from src.scenes.level1_hinge import Level1Hinge
from src.scenes.level2_beans import Level2Beans
from src.scenes.level3_yarn import Level3Yarn
from src.scenes.level5_beans_park import Level5BeansPark
from src.scenes.level6_proposal_park import Level6ProposalPark
from src.scenes.coming_soon import ComingSoonScreen


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
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
        elif name == SCENE_COMING:
            return ComingSoonScreen(SCREEN_W, SCREEN_H)
        return TitleScreen(SCREEN_W, SCREEN_H)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                self.scene.handle_event(event)

            self.scene.update(dt)

            if self.scene.next_scene:
                self.scene = self._get_scene(self.scene.next_scene)

            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
