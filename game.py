"""Game"""


from time import sleep
import sys
import pygame
from pygame import *
from pygame.locals import *
from enum import Enum

# Marcus was here


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    NONE = 4


friction = 0.2
gravity = 3/4


def sign(value):
    """Returns the sign of the number given"""
    return 1 if value == abs(value) else -1


class Object(sprite.Sprite):
    def __init__(self, groups, xpos, ypos, img):
        super().__init__(groups)
        self.xpos = xpos
        self.ypos = ypos
        self.image = img
        self.rect = self.image.get_rect()
        self.xvel = 0
        self.yvel = 0
        self.collisions = {
            Direction.LEFT: False,
            Direction.RIGHT: False,
            Direction.UP: False,
            Direction.DOWN: False
        }

    def update(self):
        """Ticks the object"""
        self.rect = self.rect.move([self.xvel, self.yvel])
        super().update()

    def is_colliding(self, crect, direction):
        """Detects external collisions with a rect"""
        if direction == Direction.UP:
            return self.rect.top < crect.bottom and \
                (self.rect.right < crect.left or self.rect.left > crect.right)
        elif direction == Direction.LEFT:
            return self.rect.left < crect.right and \
                (self.rect.bottom < crect.top or self.rect.top > crect.bottom)
        elif direction == Direction.RIGHT:
            return self.rect.right > crect.left and \
                (self.rect.bottom < crect.top or self.rect.top > crect.bottom)
        elif direction == Direction.DOWN:
            return self.rect.bottom > crect.top and \
                (self.rect.right < crect.left or self.rect.left > crect.right)

    def collide_internal(self, crect, direction):
        """Detects internal collisions with a rect"""
        if direction == Direction.UP:
            return self.rect.top < crect.top
        elif direction == Direction.LEFT:
            return self.rect.left < crect.left
        elif direction == Direction.RIGHT:
            return self.rect.right > crect.right
        elif direction == Direction.DOWN:
            return self.rect.bottom > crect.bottom

    def collision(self):
        self.collisions = {
            Direction.LEFT: False,
            Direction.RIGHT: False,
            Direction.UP: False,
            Direction.DOWN: False
        }


class Player(Object):
    def __init__(self, groups, img, accel, top_speed, jump_limit, jump_velocity):
        super().__init__(groups, 0, 0, img)
        self.accel = accel
        self.top_speed = top_speed
        self.jump_limit = jump_limit
        self.jump_velocity = jump_velocity
        self.jumps = 0
        self.movements = {
            "direction": None,
            "jumping": False
        }  # keep track of whether we are moving and where
        self.last_direction = Direction.RIGHT
        self.direction_before = Direction.RIGHT


    def update(self):
        # ...
        if self.movements['direction'] == None:
            self.xvel -= self.xvel * friction  # apply friction if the player is not moving
            self.direction_before = self.last_direction

        self.direction_before = self.last_direction

        if self.movements['direction'] == Direction.RIGHT:
            self.xvel += self.accel
            self.last_direction = Direction.RIGHT

        if self.movements['direction'] == Direction.LEFT:
            self.xvel -= self.accel
            self.last_direction = Direction.LEFT

        if self.direction_before != self.last_direction:
            self.image = pygame.transform.flip(self.image, True, False)

        if abs(self.xvel) > self.top_speed:
            self.xvel = sign(self.xvel) * self.top_speed

        if self.collide_internal(bounds, Direction.LEFT):
            self.rect = self.rect.move([-self.xvel + 1, 0])
        elif self.collide_internal(bounds, Direction.RIGHT):
            self.rect = self.rect.move([-self.xvel - 1, 0])

        if self.collide_internal(bounds, Direction.UP):
            self.yvel = gravity  # fix getting stuck on top of the window
            self.rect = self.rect.move([0, -self.rect.top])  # fix flying above the window

        if self.collide_internal(bounds, Direction.DOWN):
            self.yvel = abs(self.yvel) * -bounciness
            self.jumps = 0

        if self.movements["jumping"] and self.jumps < self.jump_limit:
            self.movements["jumping"] = False
            self.yvel = self.jump_velocity
            self.jumps += 1

        self.yvel += gravity
        super().update()


bounciness = 0  # bounciness of the level floor
friction = 0.2  # friction of the level floor

bounds = []
solids = []


def scaleup(surface, factor):
    return pygame.transform.scale(surface, (surface.get_rect().width * factor, surface.get_rect().height * factor))


def main():
    """Runs the game main loop"""

    global bounds
    global solids

    pygame.init()

    size = width, height = 900, 600   # window size
    fps = 75  # target fps which determines general game speed
    gravity = 3/4  # gravity constant
    white = 255, 255, 255  # background color

    screen = pygame.display.set_mode(size)

    drawgroup = sprite.RenderClear()
    collidegroup = sprite.RenderClear()

    bounds = screen.get_rect()
    solids = collidegroup

    charimg = scaleup(pygame.image.load("assets/Walking2.png"), 3)  # the character sprite

    char = Player(
        groups=drawgroup,
        accel=1,
        img=charimg,
        top_speed=8,
        jump_limit=2,
        jump_velocity=-12
    )

    background = scaleup(pygame.image.load("assets/Background.png"), 6)
    
    keys_pressed = {
        Direction.LEFT: False,
        Direction.RIGHT: False,
        Direction.UP: False
    }  # keep track of whether we are moving and where

    movements = {
        "direction": None,
        "jumping": False
    }

    while True:
        for game_event in pygame.event.get():  # event processing
            #print(game_event)
            if game_event.type == QUIT:
                sys.exit()  # handle window close
            if game_event.type == KEYDOWN:  # handle key press down
                k = game_event.key  # code of the key being pressed down
                if k == K_SPACE or k == K_UP:  # jump
                    keys_pressed[Direction.UP] = True
                if k == K_LEFT:  # move left
                    keys_pressed[Direction.LEFT] = True
                if k == K_RIGHT:  # move right
                    keys_pressed[Direction.RIGHT] = True
            if game_event.type == KEYUP:  # handle key release
                k = game_event.key  # code of the key being released
                if k == K_LEFT:  # stop moving left
                    keys_pressed[Direction.LEFT] = False
                if k == K_RIGHT:  # stop moving right
                    keys_pressed[Direction.RIGHT] = False

        if keys_pressed[Direction.UP]:
            movements["jumping"] = True
            keys_pressed[Direction.UP] = False

        if keys_pressed[Direction.LEFT] and keys_pressed[Direction.RIGHT]:
            movements["direction"] = None
        elif keys_pressed[Direction.LEFT]:
            movements["direction"] = Direction.LEFT
        elif keys_pressed[Direction.RIGHT]:
            movements["direction"] = Direction.RIGHT
        else:
            movements["direction"] = None

        char.movements = movements

        drawgroup.update()

        screen.blit(background, (0, 0))
        drawgroup.clear(screen, background)
        drawgroup.draw(screen)
        pygame.display.flip()

        pygame.time.Clock().tick(fps)


if __name__ == "__main__":
    main()
