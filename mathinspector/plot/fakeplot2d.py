import pygame
from pygame.locals import *

OPTIONS = {}

class SDLWindow:
	def __init__(self):
		pass

	def plot(self, *args, **kwargs):
		w, h = (1280, 720)
		clock = pygame.time.Clock()
		pygame.init()
		self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)

		is_running = True
		while is_running:
			# print ("hi")
			# if kwargs["on_update"]:
			# 	kwargs["on_update"]()

			for event in pygame.event.get():
			# 	print (event)
				if event.type == pygame.QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					is_running = False
			# pygame.event.pump()
			clock.tick(60)

		pygame.display.quit()