import pygame
import resources
import utils
from pygame.locals import *
from colors import *


VERSION = utils.read('VERSION').strip('\n')

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)
pygame.init()
pygame.display.set_icon(resources.load_image('icon.png'))

resolution = (1280, 720)
min_resolution = (800, 600)
fps = 60
mode = pygame.RESIZABLE
window = pygame.display.set_mode(resolution, mode)
pygame.display.set_caption("Ice Emblem " + VERSION)
pygame.key.set_repeat(200, 50)
clock = pygame.time.Clock()

FPS_FONT = pygame.font.SysFont("Liberation Sans", 12)

def modeset():
	global window
	window = pygame.display.set_mode(resolution, mode)

def set_fullscreen(enable):
	global mode
	mode = pygame.FULLSCREEN if enable else pygame.RESIZABLE
	modeset()

def toggle_fullscreen():
	global mode
	mode = pygame.FULLSCREEN if mode != pygame.FULLSCREEN else pygame.RESIZABLE
	modeset()

def set_resolution(res):
	global resolution
	resolution = res
	modeset()

def handle_videoresize(event):
	global window
	screen_size = event.size
	if screen_size[0] < min_resolution[0]:
		screen_size = (min_resolution[0], screen_size[1])
	if screen_size[1] < min_resolution[1]:
		screen_size = (screen_size[0], min_resolution[1])
	window = pygame.display.set_mode(screen_size, mode)

def draw_fps(font=None):
	if font is None:
		font = FPS_FONT
	screen_w, screen_h = window.get_size()
	fps = clock.get_fps()
	fpslabel = font.render('%d FPS' % int(fps), True, WHITE)
	rec = fpslabel.get_rect(top=5, right=screen_w - 5)
	window.blit(fpslabel, rec)

def fadeout(fadeout_time, percent=0):
	import events
	start = pygame.time.get_ticks()
	fade = window.copy()
	state_time = 0
	percent = (100 - percent) / 100.0

	while state_time < fadeout_time:
		alpha = int(255.0 - 255.0 * state_time / fadeout_time * percent)
		fade.set_alpha(alpha)
		window.fill(BLACK)
		window.blit(fade, (0, 0))
		pygame.display.flip()
		clock.tick(60)
		state_time = pygame.time.get_ticks() - start
		events.pump()

def tick(_fps=None):
	if _fps is None:
		return clock.tick(fps)
	return clock.tick(_fps)

def flip():
	pygame.display.flip()