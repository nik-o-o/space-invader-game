#!/usr/bin/env python3

import pygame
import os
import time
import random

# initialize the font for levels and lives
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

# loading images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))  #Player player

# loading lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# background
# scale is re-sizing the image to the width and height that we want
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
	'''
	This is a class is for the lasers in the game.
	'''
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		'''
		Method to draw the lasers on the screen.
		'''
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		'''
		Method to move lasers on screen with velocity velo.
		'''
		self.y += vel

	def off_screen(self, height):
		'''
		returns true if laser goes off-screen.
		'''
		return not(self.y <= height and self.y >= 0)

	def collision(self, obj):
		'''
		returns true if the laser collides with the obj.
		'''
		return collide(self, obj)

# General ship class to inherit from
class Ship:
	'''
	Ship class (PARENT CLASS FOR PLAYER SHIP AND ENEMY SHIP)
	'''
	COOLDOWN = 30 # FPS/2

	def __init__(self, x, y, health = 100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1
	
	def draw(self, window):
		'''
		Method to draw the ship on the screen (window).
		'''
		# pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50), 0) # 0 -> filled in rectangle. If wanted hollow, put width = some_value
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		'''
		Method for ship to shoot lasers.
		'''
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def get_width(self):
		'''
		returns width of the ship on window
		'''
		return self.ship_img.get_width()

	def get_height(self):
		'''
		returns height of the ship on window
		'''
		return self.ship_img.get_height()

	def shoot(self):
		'''
		adds lasers in the ship.
		'''
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

class Player(Ship):
	'''
	class Player inherited from base class Ship.
	This is the player playing the game.
	'''
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health) # inherits from parent (Ship)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self, vel, objs):
		'''
		move_lasers method overriden from Ship class to move lasers on screen and check if they hit the enemy ship.
		'''
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)

	def draw(self, window):
		'''
		Method to draw the ship overriden from Ship class to add the health-bar in Player ship.
		'''
		super().draw(window)
		self.healthbar(window)

	def healthbar(self, window):
		'''
		Designing the healthbar on Player ship.
		'''
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
	'''
	class Enemy ship inherited from Ship class.
	'''
	COLOR_MAP = {
				"red": (RED_SPACE_SHIP, RED_LASER),
				"green": (GREEN_SPACE_SHIP, GREEN_LASER),
				"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
				}

	def __init__(self, x, y, color, health=100):
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		'''
		Method to move the ships.
		'''
		self.y += vel

	def shoot(self):
		'''
		Method to shoot laser from enemy ship.
		'''
		if self.cool_down_counter == 0:
			laser = Laser(self.x - 15, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

def collide(obj1, obj2):
	'''
	Returns true if obj1 collides with obj2.
	Checks if images overlap with each other. 
	'''
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
	'''
	Main function of game.
	'''
	run = True
	FPS = 60
	clock = pygame.time.Clock()
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 50) # 50 -> size
	lost_font = pygame.font.SysFont("comicsans", 60) # 50 -> size

	enemies = [] # list of enemies in particular level.
	wave_length = 5 # number of ships in 1 level.
	enemy_vel = 1 # velocity of enemy ships.

	player_vel = 5 # velocity of player
	player = Player(300, 630) # initializing object of Player class and spawning it on x = 300, y = 630

	laser_vel = 5 # velocity of laser

	lost = False # bool keeping track if player lost (lives = 0 or health = 0)
	lost_count = 0

	def redraw_window():
		'''
		Redrawing the window 60 times in a second (FPS).
		'''
		WIN.blit(BG, (0,0)) # 0,0 is top-left corner
		
		# draw text
		lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 0))
		level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

		# positioning lives and levels on screen
		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
		
		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # FLASHES "you lost" on the center of screen

		pygame.display.update() # refreshes the display

	while(run):
		clock.tick(FPS)
		redraw_window()

		# check if player lost.
		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		# updating run if player lost.
		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		# updating level if cleared previous level (defeating enemies of previous level) 
		if len(enemies) == 0:
			level += 1
			wave_length += 5
			for i in range(wave_length):
				# spawns Enemy ships randomly in y = -1500 to y = -100 so they stay hidden from the screen
				enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)

		# if 'cross' (X) is clicked (top-right), window will close
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				quit()

		# CONTROLS
		keys = pygame.key.get_pressed() # return dictionary with pressed keys. computes 60 times in 1 sec (fps)
		if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0: # a -> left
			player.x -= player_vel
		if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH: # d -> right
			player.x += player_vel
		if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0: # w -> up
			player.y -= player_vel
		if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 15 < HEIGHT: # s -> down
			player.y += player_vel

		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*60) == 1:
				enemy.shoot()

			elif collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)

			if enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(enemy)

		# -laser_vel because player shoots from bottom to up and we have to check if laser collide with any enemy so passed the list of enemies.
		player.move_lasers(-laser_vel, enemies)

def main_menu():
	'''
	Main MENU of the game (Press the mouse to begin pops in the middle of screen)
	'''
	title_font = pygame.font.SysFont("comicsans", 70)
	run = True
	while(run):
		WIN.blit(BG, (0,0))
		title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()

	pygame.quit()

main_menu()