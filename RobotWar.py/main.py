import pygame
from pygame import mixer
from pygame.locals import *
import random
import button

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()


#define fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Robot war')


#define fonts
tuban = pygame.font.Font('fonts/pressstart2p.ttf', 80)
font40 = pygame.font.Font('fonts/pressstart2p.ttf', 40)
fontR = pygame.font.Font('fonts/pressstart2p.ttf', 60)
win = pygame.font.Font('fonts/pressstart2p.ttf', 60)
fontS = pygame.font.Font('fonts/pressstart2p.ttf', 25)
fontX = pygame.font.Font('fonts/pressstart2p.ttf', 45)



TEXT_COL = (255, 255, 255)


#load button images
start_img = pygame.image.load("images/button_start.png").convert_alpha()
exit_img = pygame.image.load("images/exit_btn.png").convert_alpha()
mg = pygame.image.load("img/menu_g.jpg").convert_alpha()

#create button instances
start_button = button.Button(165, 250, start_img, 1)
exit_button = button.Button(187, 450, exit_img, 1)



#load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(2)

theme_fx = pygame.mixer.Sound("img/theme.wav")
theme_fx.set_volume(0.25)

win_fx = pygame.mixer.Sound("img/ww.wav")
win_fx.set_volume(0.25)

lose_fx = pygame.mixer.Sound("img/lose.wav")
lose_fx.set_volume(0.25)

theme_fx = pygame.mixer.Sound("img/theme.wav")
theme_fx.set_volume(0.25)


#define game variables
rows = 5
cols = 5
robot_cooldown = 1000#bullet cooldown in milliseconds
last_robot_shot = pygame.time.get_ticks()
countdown = 4
last_count = pygame.time.get_ticks()
game_over = 0#0 is no game over, 1 means player has won, -1 means player has lost
game_paused = True
menu_state = "main"
score = 0 
sound_played = False

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
org = (255, 131, 45)
maucuatuban = (76, 119, 88)



#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
	screen.blit(bg, (0, 0))
def draw_score():
	draw_text(f'Score: {score}', fontS, white, 10, 10)


#define function for creating text
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#create spaceship class
class Spaceship(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/spaceship.png") #tao hinh anh
		self.rect = self.image.get_rect() #tao ra 1 cai o vuong chua hinh anh
		self.rect.center = [x, y] #vi tri cuar hinh anh
		self.health_start = health #ham thanh mau nguoi choi luc bat dau
		self.health_remaining = health #ham thanh mau nguoi choi luc sau
		self.last_shot = pygame.time.get_ticks() #ham get_ticks() dum de dem thoi gian trong game, ham nay giup ban dan theo nhu cooldown cho 1s thi ban 1 vien

	def update(self):
		#set movement speed
		speed = 8 # dich chuyen 8 pixels
		#set a cooldown variable
		cooldown = 500 #milliseconds
		game_over = 0


		#get key press
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] and self.rect.left > 0: #neu an sang trai se dich chuyen sang ben trai 8 pixels va de no khong bi mat khoi man hinh thi gioi han bang lenh and self.rect.left > 0
			self.rect.x -= speed
		if key[pygame.K_RIGHT] and self.rect.right < screen_width: #nhu tren nhung sang phai
			self.rect.x += speed

		#record current time
		time_now = pygame.time.get_ticks() #dem thoi gian 
		#shoot
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown: # an SPACE de ban dan va hoi lai sau 1s thi moi ban duoc tiep and time_now - self.last_shot > cooldown tranh ban lien tuc
			laser_fx.play()
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now


		#update maskx	
		self.mask = pygame.mask.from_surface(self.image) # hoat dong nhu hitbox cua game 


		#draw health bar
		pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15)) # ve thanh mau nguoi choi
		if self.health_remaining > 0:
			pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15)) #ve khi thanh mau bi tut
		elif self.health_remaining <= 0:
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
			explosion_group.add(explosion)
			self.kill() # duoc su dung nhieu trong code nay dung de lam cho vat the bien mat
			game_over = -1
		return game_over



#create Bullets class
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y] #vị trí của đạn xuất hiện ở ngay giữ theo spaceship

	def update(self):
		self.rect.y -= 5 #vì space ship ở phía dưới nên khi muốn đạn bắn lên trên thì -5 pixels
		if self.rect.bottom < 0: #đạn sẽ biến mất khi ra khỏi màn hình
			self.kill()
		if pygame.sprite.spritecollide(self, robot_group, True): # kiểm tra va trạm của đạn với robot
			self.kill() # biến mất khi có va trạm 
			global score
			score += 10
			explosion_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2) 
			explosion_group.add(explosion) 




#create Robots class
class Robots(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/robot" + str(random.randint(1, 6)) + ".png") #tao random robot co trong 6 file anh
		self.rect = self.image.get_rect() 
		self.rect.center = [x, y]
		self.move_counter = 0 # tốc độ di chuyển
		self.move_direction = 1 # robot bắt đầu di chuyển sang phải còn nếu giá trị là -1 thì sang trái

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75: # kiểm soát cho các robot không di chuyển tràn ra màn hình
			self.move_direction *= -1 #di chuyển về phía ngược lại khi thoả điều kiện trên
			self.move_counter *= self.move_direction #tốc độ không thay đổi



#create Box Bullets class
class Box_Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/box.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask): #kiểm tra va chạm giữa hộp với space ship giúp game phát hiện khi nào thì người chơi mất máu, False để cho space ship không bị phá huỷ ngay lập tức
			self.kill() #Hộp sẽ biến mất sau va chạm
			explosion2_fx.play()
			#reduce spaceship health
			spaceship.health_remaining -= 1 # máu sẽ mất đi 1 
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1) #nổ theo size 1
			explosion_group.add(explosion)




#create Explosion class
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = [] #tạo ảnh nổ
		for num in range(1, 6):
			img = pygame.image.load(f"img/exp{num}.png")
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			#add the image to the list
			self.images.append(img) #load hình ảnh theo thứ tứ
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0


	def update(self):
		explosion_speed = 3
		#update explosion animation
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, delete explosion
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()




#tạo ra các sprite group để dễ kiểm soát hoạt động của các nguyên tố game
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
robot_group = pygame.sprite.Group()
box_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_robots():
	#tạo các robot theo hàng thứ nhất rồi xuống từ từ đến hết 5 hàng 
	for row in range(rows):
		for item in range(cols):
			robot = Robots(110 + item * 100, 100 + row * 70)
			robot_group.add(robot)

create_robots()


#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

def toggle_pause(): #hàm này dùng để pause game lại khi ân nút SHIFT và đồng thời game cũng dừng lại theo
    global game_paused
    game_paused = not game_paused

def handle_main_menu(): #tạo ra giao diện menu đầu game
    global menu_state, game_paused
    draw_text('UEH', tuban , maucuatuban, 189, 30)
    draw_text('ROBOT WAR', fontR, org , 40, 140) 

    if start_button.draw(screen): 
        game_paused = False #khi ấn vào start thì game sẽ bắt đầu chạy
        menu_state = "game" #hiển thị game
    if exit_button.draw(screen):
        pygame.quit() #thoát game khi ấn vào
        exit()

# Main game loop
run = True
while run:
    clock.tick(fps)
    draw_bg()
    # If the game is paused
    if game_paused:
        screen.blit(mg,(0,0))  # load hình nền menu
        if menu_state == "main": #tạo màn hình menu
            handle_main_menu()

    else:  # Game is running
        if countdown == 0: #khi game đếm đến 0 thì bắt đầu chơi
            time_now = pygame.time.get_ticks()

            if time_now - last_robot_shot > robot_cooldown and len(box_bullet_group) < 5 and len(robot_group) > 0: #kiểm soát lượng hộp mà robot thả xuống là 5 mỗi 1s cho đến khi hết robot
                attacking_robot = random.choice(robot_group.sprites()) #chọn random robot sẽ thả hộp xuống
                box_bullet = Box_Bullets(attacking_robot.rect.centerx, attacking_robot.rect.bottom) #thả hộp từ robot cho tới đáy
                box_bullet_group.add(box_bullet) #thêm hộp thả xuống vào nhóm robot
                last__shot = time_now #1s thì thả xuống 5 hộp

            #Kiểm soát nếu game win
            if len(robot_group) == 0: 
                game_over = 1

            if game_over == 0: #nếu đang diễn ra
                draw_score()
                game_over = spaceship.update()
                bullet_group.update()
                robot_group.update()
                box_bullet_group.update()

            else: #trường hợp thắng và thua sẽ tạo ra chữ báo hiệu
                if game_over == -1:
                    draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 170), int(screen_height / 2 + 80))
                    if not sound_played: 
                       lose_fx.play()
                       sound_played = True
                    draw_text(f'Score: {score}', fontX, white , int(screen_width / 2 - 170), int(screen_height / 2 + 10))	
                if game_over == 1:
                    draw_text('YOU WIN!', win, white, int(screen_width / 2 - 200), int(screen_height / 2 + 30))
                    if not sound_played:
                       win_fx.play()
                       sound_played = True
                    draw_text(f'Score: {score}', fontX, white , int(screen_width / 2 - 200), int(screen_height / 2 - 50))					   
                    
        elif countdown > 0: #đồng hồ đếm ngược đầu game
            # Countdown screen logic
            draw_text('GET READY!', font40, white, int(screen_width / 2 - 170), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100)) 
            count_timer = pygame.time.get_ticks() #đếm theo thời gian từ lúc bắt đầu
            if count_timer - last_count > 1000: #đếm ngược 1s
                countdown -= 1
                last_count = count_timer

        # load các nguyên tố spaceship, robot,... lên màn hình
        explosion_group.update()
        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        robot_group.draw(screen)
        box_bullet_group.draw(screen)
        explosion_group.draw(screen)

    # Event handling for pausing or quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  # Exit the game loop
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                toggle_pause()
    pygame.display.update()  # Update the screen
pygame.quit()
