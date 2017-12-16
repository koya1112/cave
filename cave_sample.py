#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys #package sys contains vars and functions which interpreter manages
from random import randint
import pygame
from pygame.locals import QUIT, Rect, KEYDOWN, K_ESCAPE, K_SPACE, RLEACCEL

SCREEN_SIZE = (800, 600)

pygame.init()
pygame.key.set_repeat(5, 5)
SURFACE = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("image\scroll game")
FPSCLOCK = pygame.time.Clock()

# 透明色を指定したイメージを作成する関数
def load_image(filename, colorkey=None):
    '''
    第２引数colorkeyに-1を与えると自動的に左上隅の色を透明色に設定
    戻り値：イメージが描写されたSurface, イメージの矩形
    '''
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:{}".format(filename))
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            # 左上の色を透明色に
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def main():
    walls = 80
    ship_y = 250
    velocity = 0
    score = 0
    slope = randint(1, 6)
    sysfont = pygame.font.SysFont(None, 36)
    
    # 画像の設定
    ship_image, ship_rect = load_image("image\ship.png", colorkey=-1)
    bang_image, bang_rect = load_image("image\bang.png", colorkey=-1)

    # SEをロード
    hit_sound = pygame.mixer.Sound("music\se1.wav")

    holes = []
    for xpos in range(walls):
        holes.append(Rect(xpos * 10, 100, 10, 400))
    game_over = False

    # BGMを再生
    pygame.mixer.music.load("music\bgm1.mp3")
    pygame.mixer.music.play(-1) # 引数-1でループ再生

    # game_start
    start_key = True
    while start_key:
        start_image = sysfont.render("PRESS SPACE KEY", True, (225, 225, 0))
        SURFACE.blit(start_image, (400, 300))
        pygame.display.update()
        # space_keyでゲーム開始
        for event in pygame.event.get():
            if event.type == QUIT: sys.exit()
            if event.type == KEYDOWN:  # キーを押したとき
                if event.key == K_SPACE:
                    start_key = False

    while True:
        is_space_down = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:  # キーを押したとき
                # ESCキーならスクリプトを終了
                if event.key == K_ESCAPE:
                    sys.exit()
                # spaceキーなら画像を移動
                if event.key == K_SPACE:
                    is_space_down = True

        # move the ship
        if not game_over:
            score += 10
            velocity += -3 if is_space_down else 3
            ship_y += velocity

            # scroll the cave
            edge = holes[-1].copy()
            test = edge.move(0, slope)
            if test.top <= 0 or test.bottom >= 600:
                slope = randint(1, 6) * (-1 if slope > 0 else 1)
                edge.inflate_ip(0, -20)
            edge.move_ip(10, slope)
            holes.append(edge)
            del holes[0]
            holes = [x.move(-10, 0) for x in holes]

            # judge the collision
            if holes[0].top > ship_y or \
               holes[0].bottom < ship_y + 80:
               game_over = True
               pygame.mixer.music.stop() # BGMを停止
               hit_sound.play()  # SEを再生

            # render the surface
            SURFACE.fill((0, 255, 0))
            for hole in holes:
                pygame.draw.rect(SURFACE, (0, 0, 0), hole)
            SURFACE.blit(ship_image, (0, ship_y))
            score_image = sysfont.render("score is {}".format(score), True, (0, 0, 225))
            esc_image = sysfont.render("if you want to quit, push 'Esc' key.", True, (225, 0, 0))
            SURFACE.blit(score_image, (600, 20))
            SURFACE.blit(esc_image, (0, 0))

            if game_over:
                SURFACE.blit(bang_image, (0, ship_y))
                SURFACE.blit(ship_image, (0, ship_y)) # shipが前面に配置されるようにする
                # TODO ゲームオーバー表示、スコア表示、リトライボタン
                gameover_image = sysfont.render("gameover", True, (0, 0, 225))
                SURFACE.blit(gameover_image, (400, 300))
                retry_image = sysfont.render("RETRY?", True, (225, 0, 0))
                SURFACE.blit(retry_image, (400, 400))

            pygame.display.update()
            FPSCLOCK.tick(15) # 15fps

if __name__ == '__main__':
    main()
