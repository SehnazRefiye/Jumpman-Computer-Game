import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

"""
    Refiye Şehnaz YILDIRIM / 171805012
    Kani SUNGUR / 161805049
"""

pygame.mixer.pre_init(44100, -16, 2, 512)
# mixer'i başlat
mixer.init()
# pygame'i başlat
pygame.init()

clock = pygame.time.Clock()
fps = 60
# Ekranın boyutu tanımlandı
screen_width = 680
screen_height = 680

screen = pygame.display.set_mode((screen_width, screen_height))
# Oyuna adı verildi
pygame.display.set_caption('Jumpman')


# Font tanımlandı.
font = pygame.font.SysFont('Jumpman', 70)
font_score = pygame.font.SysFont('Jumpman', 30)

# Oyunun değişkenleri tanımlandı
tile_size = 34
game_over = 0
main_menu = True
level = 1
max_levels = 6
score = 0

# Renkler tanımlandı
white = (255, 255, 255)
blue = (0, 0, 255)

# Resimler yüklendi
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

# Ses efektleri ve oyun müziği yüklendi
# Sound diye bir klasör oluşturdum onun içinde bunlar
pygame.mixer.music.load('sound/BitQuest.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('sound/coin.mp3')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sound/jump.mp3')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('sound/game_over.mp3')
game_over_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Leveli sıfırlama fonksiyonu
def reset_level(level):
    player.reset(50, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    ladder_group.empty()
    exit_group.empty()

    # Levellerin dataları ve her bir level için oyun dünyasını oluşturma
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    # Skoru görüntülemek için sahte para oluşturma (Ekranın sol üstünde)
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world


""" 
•	This class defines all our buttons. 
•	A button has an image and a position associated with it.
"""


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Mouse'un konumu alındı
        pos = pygame.mouse.get_pos()

        # Fare ile üzerine gelinen ve tıklanan koşulları kontrol etme
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Butonlar çizildi
        screen.blit(self.image, self.rect)

        return action


"""
•	This class defines our player. 
•	We specialize the person by adding capabilities such as jump etc.
"""


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            # yön tuşları ve space tuşu işlemleri
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 2
                self.counter += 1
                self.direction = 1
            if key[pygame.K_UP]:
                dy += 2
                self.counter += 1
                self.direction = 1
            if key[pygame.K_DOWN]:
                dy -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            if key[pygame.K_DOWN] == False and key[pygame.K_UP] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_up[self.index]
                if self.direction == -1:
                    self.image = self.images_down[self.index]

            # Yürüme animasyonu
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                    self.image = self.images_up[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                    self.image = self.images_down[self.index]

            # Yer çekimi ekleme
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Çarpışma kontrolü
            self.in_air = True
            for tile in world.tile_list:
                # x yönünde çarpışma kontrolü
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y yönünde çarpışma kontrolü
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # yerin altında olup olmadığını kontrol etme, yani zıplama
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # yerden yüksekte olup olmadığını kontrol etme, yani düşme
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # düşmanlarla çarpışmayı kontrol etme
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()


            # çıkışa gelmeyi kontrol etme
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # bu kısım imncelenmeli platformun x ve y yönü hareketi var
            # check for collision with platforms
            for platform in platform_group:
                # collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # Oyuncunun konumunu güncelleme
            self.rect.x += dx
            self.rect.y += dy


        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # Oyuncuyu ekrana çizme
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.images_up = []
        self.images_down = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            # player yaptım guy ı dikkat et
            img_right = pygame.image.load(f'img/player{num}.png')
            # img_up = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (25, 50))
            img_up = pygame.transform.scale(img_right, (25, 50))
            img_left = pygame.transform.flip(img_right, True, False)
            img_down = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_up)
            self.images_up.append(img_right)
            self.images_down.append(img_down)

        self.dead_image = pygame.image.load('img/monster.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


"""
•	This class defines all inanimate objects that we need to display on our world.
•	Any object that is on the world and not a person, comes under this class (ex. Coins, Ladders etc.)
•	Sets up the image and its position for all its child classes.
"""


class World():
    def __init__(self, data):
        self.tile_list = []

        # görseller yüklendi
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')
        ladder_img = pygame.image.load('img/ladder.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 6:
                    img = pygame.transform.scale(ladder_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


"""
•	This class defines all our enemies.
•	Our enemies will move at the determined levels along the x and y axes.
"""


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 5
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


"""
•	Used for the positions of the platforms from which the player climbs.
"""


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


"""
•	This class defines all our coins. 
•	Each coin will increase our score by an amount of 'value'. 
•	We animate each coin with 1 image.
"""


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


"""
•	This class defines all our ladders in the game. 
•	We can add features such as ladder climb sounds etc. here.

"""


class Ladder(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/ladder.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        """
        def move(self, guy):
        keys = pygame.key.get_pressed()
        if keys[K_DOWN]:
            if guy.rect.y + 50 < self.rect.y + self.rect.height:
                guy.rect.y += 10
        if keys[K_UP]:
            guy.rect.y -= 10
        elif keys[K_LEFT]:
            guy.rect.x -= 10
        elif keys[K_RIGHT]:
            guy.rect.x += 10
        """


"""
•	It was created so that the player can pass to the next level and win the game in the last level.
"""


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(50, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# skoru göstermek için sahte para oluşturma
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# level verilerini yükleme ve oyun dünyasını oluşturma
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# Butonları oluşturma
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 60, screen_height // 2-80, start_img)
exit_button = Button(screen_width // 2 - 60, screen_height // 2, exit_img)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()
            # Skoru güncelle
            # Paranın toplanıp toplanmadığını kontrol etme
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        ladder_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # Eğer oyuncu ölürse
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # Eğer oyuncu leveli geçerse
        if game_over == 1:
            # Oyunu resetle ve bir sonraki levele geç
            level += 1
            if level <= max_levels:
                # Leveli resetle
                world_data = []
                world = reset_level(level)
                game_over = 0
            # Eğer son level de geçildiyse oyuncu oyunu kazandı
            else:
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    # Leveli resetle
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
