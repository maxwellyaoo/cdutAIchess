# coding:utf-8
import sys
import pygame
import random
import os.path
from MyChess.Chess_Core import Chessboard
from MyChess.Chess_Core import Point
from MyChess.Chess_Core import Chessman
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]
SCREENRECT = Rect(0, 0, 720, 800)


def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'Img', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pygame.get_error()))
    return surface.convert()
def load_sound(file):
    file = os.path.join(main_dir, 'sounds', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        raise SystemExit('Could not load sound "%s" %s' %
                         (file, pygame.get_error()))
    return sound

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class Chessman_Sprite(pygame.sprite.Sprite):
    is_selected = False
    images = []
    is_transparent = False
    def __init__(self, images, Kill_sound, chessman):
        pygame.sprite.Sprite.__init__(self)
        self.chessman = chessman
        self.images = images
        self.image = self.images[0]
        self.rect = Rect(chessman.col_num * 80,
                         (9 - chessman.row_num) * 80,  80,  80)
        self.move_sound = load_sound("move.mp3")
        self.Kill_sound = Kill_sound

    def move(self, col_num, row_num):
        old_col_num = self.chessman.col_num
        old_row_num = self.chessman.row_num
        is_correct_position = self.chessman.move(col_num, row_num)
        if is_correct_position:
            self.rect.move_ip((col_num - old_col_num)
                              * 80, (old_row_num - row_num) * 80)
            self.rect = self.rect.clamp(SCREENRECT)
            self.chessman.chessboard.clear_chessmans_moving_list()
            self.chessman.chessboard.calc_chessmans_moving_list()
            return True
        load_sound("lowtime.mp3").play()
        return False

    def update(self):
        if self.is_selected:
            if self.is_transparent:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.is_transparent = not self.is_transparent
        else:
            self.image = self.images[0]


def creat_sprite_group(sprite_group, chessmans_hash):
    for chessman in chessmans_hash.values():
        if chessman.is_red:
            if isinstance(chessman, Chessman.Rook):
                images = load_images("red_rook.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Cannon):
                images = load_images("red_cannon.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Knight):
                images = load_images("red_knight.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.King):
                images = load_images("red_king.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Elephant):
                images = load_images("red_elephant.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Mandarin):
                images = load_images("red_mandarin.gif", "transparent.gif")
            else:
                images = load_images("red_pawn.gif", "transparent.gif")
        else:
            if isinstance(chessman, Chessman.Rook):
                images = load_images("black_rook.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Cannon):
                images = load_images("black_cannon.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Knight):
                images = load_images("black_knight.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.King):
                images = load_images("black_king.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Elephant):
                images = load_images("black_elephant.gif", "transparent.gif")
            elif isinstance(chessman, Chessman.Mandarin):
                images = load_images("black_mandarin.gif", "transparent.gif")
            else:
                images = load_images("black_pawn.gif", "transparent.gif")
        if isinstance(chessman,Chessman.Cannon):
            Kill_sound = load_sound("explosion.mp3")
        else:
            Kill_sound = load_sound("berserk.mp3")
        chessman_sprite = Chessman_Sprite(images, Kill_sound, chessman)
        sprite_group.add(chessman_sprite)


def select_sprite_from_group(sprite_group, col_num, row_num):
    for sprite in sprite_group:
        if sprite.chessman.col_num == col_num and sprite.chessman.row_num == row_num:
            return sprite


def translate_hit_area(screen_x, screen_y):
    return screen_x // 80, 9 - screen_y // 80


def main(winstyle=0):
    # set up mixer function for sounds
    pygame.mixer.init()
    pygame.init()
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pygame.display.set_caption("马后炮")

    # create the background, tile the bgd image
    bgdtile = load_image('boardchess.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    cbd = Chessboard.Chessboard('000')
    cbd.init_board()

    chessmans = pygame.sprite.Group()
    framerate = pygame.time.Clock()

    load_sound("dong.mp3").play()
    
    creat_sprite_group(chessmans, cbd.chessmans_hash)
    current_chessman = None
    cbd.calc_chessmans_moving_list()
    while not cbd.is_end():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                pressed_array = pygame.mouse.get_pressed()
                for index in range(len(pressed_array)):
                    if index == 0 and pressed_array[index]:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        col_num, row_num = translate_hit_area(mouse_x, mouse_y)
                        chessman_sprite = select_sprite_from_group(
                            chessmans, col_num, row_num)
                        if current_chessman is None and chessman_sprite != None:
                            if chessman_sprite.chessman.is_red == cbd.is_red_turn:
                                current_chessman = chessman_sprite
                                chessman_sprite.is_selected = True
                        elif current_chessman != None and chessman_sprite != None:
                            if chessman_sprite.chessman.is_red == cbd.is_red_turn:
                                current_chessman.is_selected = False
                                current_chessman = chessman_sprite
                                chessman_sprite.is_selected = True
                            else:
                                success = current_chessman.move(
                                    col_num, row_num)
                                if success:
                                    current_chessman.Kill_sound.play()
                                    chessmans.remove(chessman_sprite)
                                    chessman_sprite.kill()
                                    current_chessman.is_selected = False
                                    current_chessman = None
                        elif current_chessman != None and chessman_sprite is None:
                            success = current_chessman.move(col_num, row_num)
                            if success:
                                current_chessman.is_selected = False
                                current_chessman.move_sound.play()
                                current_chessman = None
                                
        framerate.tick(20)
        # clear/erase the last drawn sprites
        chessmans.clear(screen, background)

        # update all the sprites
        chessmans.update()
        chessmans.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
