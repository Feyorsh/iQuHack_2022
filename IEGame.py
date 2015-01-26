# -*- coding: utf-8 -*-
#
#  IEGame.py, Ice Emblem's main game class.
#
#  Copyright 2015 Elia Argentieri <elia.argentieri@openmailbox.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import time
import pygame
import sys
import os.path

from IEItem import IEItem, IEWeapon
from IEMap import IEMap
from IEUnit import IEUnit, IEPlayer

from datetime import datetime
from Colors import *

def timestamp_millis_64():
	return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)

def center(rect1, rect2, xoffset=0, yoffset=0):
	"""Center rect2 in rect1 with offset."""
	return (rect1.centerx - rect2.centerx + xoffset, rect1.centery - rect2.centery + yoffset)

def distance(p0, p1):
    return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])

class IEGame(object):
	def __init__(self, players, _map, tileset_path, music, colors):
		pygame.init()
		# pygame.FULLSCREEN    create a fullscreen display
		# pygame.DOUBLEBUF     recommended for HWSURFACE or OPENGL
		# pygame.HWSURFACE     hardware accelerated, only in FULLSCREEN
		# pygame.OPENGL        create an OpenGL renderable display
		# pygame.RESIZABLE     display window should be sizeable
		# pygame.NOFRAME       display window will have no border or controls
		self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
		pygame.display.set_caption("Ice Emblem")

		self.clock = pygame.time.Clock()

		font_path = os.path.abspath('fonts/Medieval Sharp/MedievalSharp.ttf')
		self.MAIN_MENU_FONT = pygame.font.Font(font_path, 48)
		self.SMALL_FONT = pygame.font.Font(font_path, 24)
		self.FPS_FONT = pygame.font.SysFont("Liberation Sans", 12)

		self.players = players
		self._map = _map

		self.tileset = pygame.image.load(os.path.abspath(tileset_path))
		self.tileset.convert()

		#pygame.mixer.set_reserved(2)
		self.overworld_music_ch = pygame.mixer.Channel(0)
		self.battle_music_ch = pygame.mixer.Channel(1)
		
		self.main_menu_music = pygame.mixer.Sound(os.path.abspath(music['menu']))
		self.overworld_music = pygame.mixer.Sound(os.path.abspath(music['overworld']))
		self.battle_music = pygame.mixer.Sound(os.path.abspath(music['battle']))

		self.colors = colors
		self.backgrounds = {}
		for background, color in self.colors.iteritems():
			self.backgrounds[background] = pygame.Surface(self._map.square).convert_alpha()
			self.backgrounds[background].fill(color)

		#self.overworld_music_ch.play(overworld_music, -1)
		self.winner = None
		self.prev_dist = None

	def screen_resize(self, (screen_w, screen_h)):
		self._map.screen_resize((screen_w, screen_h))
		for background, color in self.colors.iteritems():
			self.backgrounds[background] = pygame.Surface(self._map.square).convert_alpha()
			self.backgrounds[background].fill(color)

	def play_overworld_music(self):
		"""Start playing overworld music in a loop."""
		self.overworld_music_ch.play(self.overworld_music, -1)

	def wait_for_user_input(self, timeout=-1):
		"""
		This function waits for the user to left-click somewhere and,
		if the timeout argument is positive, exits after the specified
		number of milliseconds.
		"""

		now = start = timestamp_millis_64()

		while now - start < timeout or timeout < 0:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:  # If user clicked close
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					return event
			self.clock.tick(10)
			now = timestamp_millis_64()
		return None

	def main_menu(self):
		self.main_menu_music.play()
		screen_rect = self.screen.get_rect()
		screen_w, screen_h = self.screen.get_size()

		self.screen.fill(BLACK)

		elinvention = self.MAIN_MENU_FONT.render("Elinvention", 1, WHITE)
		presents = self.MAIN_MENU_FONT.render("PRESENTS", 1, WHITE)

		self.screen.blit(elinvention, center(screen_rect, elinvention.get_rect()))

		self.screen.blit(presents, center(screen_rect, presents.get_rect(), yoffset=self.MAIN_MENU_FONT.get_linesize()))

		pygame.display.flip()

		self.wait_for_user_input(6000)


		path = os.path.abspath('images/Ice Emblem.png')
		main_menu_image = pygame.image.load(path).convert_alpha()
		main_menu_image = pygame.transform.smoothscale(main_menu_image, (screen_rect.w, screen_rect.h))

		click_to_start = self.MAIN_MENU_FONT.render("Click to Start", 1, ICE)
		click_license = self.SMALL_FONT.render("License", 1, WHITE)

		self.screen.blit(main_menu_image, (0, 0))
		self.screen.blit(click_to_start, center(screen_rect, click_to_start.get_rect(), yoffset=200))
		license_w, license_h = click_license.get_size()
		self.screen.blit(click_license, (screen_w - license_w, screen_h - license_h))

		pygame.display.flip()

		click_x, click_y = self.wait_for_user_input().pos

		if click_x > screen_w - license_w and click_y > screen_h - license_h:
			path = os.path.abspath('images/GNU GPL.jpg')
			gpl_image = pygame.image.load(path).convert()
			gpl_image = pygame.transform.smoothscale(gpl_image, (screen_rect.w, screen_rect.h))
			self.screen.blit(gpl_image, (0, 0))
			pygame.display.flip()
			self.wait_for_user_input()

		pygame.mixer.fadeout(2000)
		self.fade_out(2000)
		pygame.mixer.stop() # Make sure mixer is not busy

	def draw_fps(self):
		screen_w, screen_h = self.screen.get_size()
		fps = self.clock.get_fps()
		fpslabel = self.FPS_FONT.render(str(int(fps)) + ' FPS', True, WHITE)
		rec = fpslabel.get_rect(top=5, right=screen_w - 5)
		self.screen.blit(fpslabel, rec)

	def draw_map(self):
		"""Let's draw the map!"""
		screen_w, screen_h = self.screen.get_size()
		#screen_rect = self.screen.get_rect()

		square = (self._map.tile_size - 2, self._map.tile_size - 2)
		side = self._map.tile_size

		map_w = square * self._map.w
		map_h = square * self._map.h

		self.screen.fill(BLACK)

		for i in range(0, self._map.w):
			# pygame.draw.line(screen, WHITE, (i * side, 0), (i * side, map_h), 1)
			for j in range(0, self._map.h):
				# pygame.draw.line(screen, WHITE, (0, j * side), (map_w, j * side), 1)

				node = self._map.nodes[i][j]
				unit = node.unit
				tile = node.tile

				node_background = self.tileset.subsurface(pygame.Rect(tile, (64, 64)))
				node_background = pygame.transform.smoothscale(node_background, square)
				self.screen.blit(node_background, (i * side, j * side))

				if self._map.is_selected((i, j)):
					self.screen.blit(self.backgrounds['selected'], (i * side, j * side))
				elif self._map.is_in_move_range((i, j)):
					self.screen.blit(self.backgrounds['move_range'], (i * side, j * side))
				elif self._map.is_in_attack_range((i, j)):
					self.screen.blit(self.backgrounds['attack_range'], (i * side, j * side))
				elif self._map.is_played((i, j)):
					self.screen.blit(self.backgrounds['played'], (i * side, j * side))

				if unit is not None:
					rect = pygame.Rect((i * side, j * side), (side, side)) # color
					pygame.draw.rect(self.screen, self.whose_unit(unit).color, rect, 1)

					if unit.image is None:
						scritta = self.SMALL_FONT.render(unit.name, 1, BLACK)
						self.screen.blit(scritta, (i * side, j * side))
					else:
						image_w, image_h = unit.image.get_size()
						if (image_w, image_h) != (side, side - 5):
							if image_w > image_h:
								aspect_ratio = float(image_h) / float(image_w)
								resized_w = side
								resized_h = int(aspect_ratio * resized_w)
							else:
								aspect_ratio = float(image_w) / float(image_h)
								resized_h = side - 5
								resized_w = int(aspect_ratio * resized_h)
							image = pygame.transform.smoothscale(unit.image, (resized_w, resized_h))
						else:
							image = unit.image
						self.screen.blit(image, (i * side + side / 2 - image.get_size()[0] / 2, j * side))

					HP_bar_length = int((float(unit.HP) / float(unit.HP_max)) * float(side))
					HP_bar = pygame.Surface((HP_bar_length, 5))
					HP_bar.fill(GREEN)
					self.screen.blit(HP_bar, (i * side, j * side + side - 5)) # HP bar
		try:
			cell_x, cell_y = self._map.mouse2cell(pygame.mouse.get_pos())
		except ValueError:
			pass
		else:
			cell_label = self.SMALL_FONT.render('X: %d Y: %d' % (cell_x, cell_y), True, WHITE)
			rec = cell_label.get_rect(bottom=screen_h - 5, left=5)
			self.screen.blit(cell_label, rec)

		turn = self.whose_turn()
		turn_label = self.SMALL_FONT.render('phase', True, WHITE)
		rec = turn_label.get_rect(bottom=screen_h - 5, left=200)
		self.screen.blit(turn_label, rec)
		rect = pygame.Rect((195 - side, screen_h - 5 - side), (side, side))
		pygame.draw.rect(self.screen, turn.color, rect, 0)

	def whose_unit(self, unit):
		for player in self.players:
			for player_unit in player.units:
				if player_unit == unit:
					return player
		return None

	def whose_turn(self):
		for player in self.players:
			if player.my_turn:
				return player
		return None

	def fade_out(self, fade_out_time):
		start = timestamp_millis_64()
		fade = self.screen.copy()
		state_time = 0

		while state_time < fade_out_time:
			alpha = int(255.0 - 255.0 * state_time / fade_out_time)
			fade.set_alpha(alpha)
			self.screen.fill(BLACK)
			self.screen.blit(fade, (0, 0))
			pygame.display.flip()
			self.clock.tick(60)
			state_time = timestamp_millis_64() - start



	def battle_animation(attacking, defending):
		start = time.time()

		while time.time() - start < ANIMATION_DURATION:
			self.screen.fill(BLACK)

			pygame.display.flip()
			self.clock.tick(60)

	def battle(self, attacking, defending):
		attacking_player = self.whose_unit(attacking)
		defending_player = self.whose_unit(defending)

		attacking_weapon = attacking.get_active_weapon()
		attacking_range = attacking_weapon.Range if attacking_weapon is not None else 1

		attacking_pos = self._map.where_is(attacking)
		defending_pos = self._map.where_is(defending)

		if distance(attacking_pos, defending_pos) <= attacking_range:
			print("\r\n##### Fight!!! #####")
			#battle_animation(attacking, defending)
			attacking.attack(defending)

			if defending.HP == 0:
				self._map.remove_unit(defending)
				defending_player.units.remove(defending)
			elif attacking.HP == 0:
				self._map.remove_unit(attacking)
				attacking_player.units.remove(attacking)
			print("##### Battle ends #####\r\n")

			if defending_player.is_defeated():
				return attacking_player
			elif attacking_player.is_defeated():
				return defending_player
			else:
				return None

	def get_active_player(self):
		for player in self.players:
			if player.my_turn:
				return player
		return None

	def switch_turn(self):
		active_player = None
		for i, player in enumerate(self.players):
			if player.my_turn:
				player.end_turn()
				active_player_index = (i + 1) % len(self.players)
				active_player = self.players[active_player_index]
				active_player.begin_turn()
				break
		self.draw_map()
		phase = self.MAIN_MENU_FONT.render(active_player.name + ' phase', 1, active_player.color)
		self.screen.blit(phase, center(self.screen.get_rect(), phase.get_rect()))
		pygame.display.flip()
		self.wait_for_user_input(5000)

	def handle_click(self, event):
		active_player = self.get_active_player()
		try:
			map_coords = self._map.mouse2cell(event.pos)
		except ValueError, e:
			print(e)
		else:
			attacking, defending = self._map.select(map_coords, active_player)
			if type(attacking) is IEUnit and type(defending) is IEUnit:
				self.overworld_music_ch.pause()
				self.battle_music_ch.play(self.battle_music)
				self.winner = self.battle(attacking, defending)
				self.battle_music_ch.stop()
				self.overworld_music_ch.unpause()
				return self.winner is not None
			elif attacking is not None:
				self.action_menu()
		if active_player.is_turn_over():
			self.switch_turn()
		return False

	def victory_screen(self):
		print(self.winner.name + " wins")
		pygame.mixer.fadeout(1000)
		self.fade_out(1000)
		victory = self.MAIN_MENU_FONT.render(self.winner.name + ' wins!', 1, self.winner.color)
		thank_you = self.MAIN_MENU_FONT.render('Thank you for playing Ice Emblem!', 1, ICE)

		self.screen.fill(BLACK)
		self.screen.blit(victory, center(self.screen.get_rect(), victory.get_rect(), yoffset=-50))
		self.screen.blit(thank_you, center(self.screen.get_rect(), thank_you.get_rect(), yoffset=50))

		pygame.display.flip()

		self.wait_for_user_input()

	def handle_mouse_motion(self, event):
		if self._map.selection is not None and self._map.move_range:
			try:
				coord = self._map.mouse2cell(event.pos)
			except ValueError:
				pass
			else:
				dist = distance(coord, self._map.selection)
				if self.prev_dist != dist:
					print(dist)
				self.prev_dist = dist

	def action_menu(self):
		print("Action menu")
		menu_wait = self.SMALL_FONT.render('Wait', 1, WHITE)
		menu_attack = self.SMALL_FONT.render('Attack', 1, WHITE)
		
		menu_wait_w, menu_wait_h = menu_wait.get_size()
		menu_attack_w, menu_attack_h = menu_attack.get_size()

		# if self.is_enemy_naerby()
		menu_h = menu_wait_h + menu_attack_h
		
		menu_size = (max(menu_wait_w, menu_attack_w), menu_h)
		
		menu = pygame.Surface(menu_size)
		menu.fill(BLACK)
		menu.blit(menu_wait, (0, 0))
		menu.blit(menu_attack, (0, menu_wait_h))

		menu_pos = pygame.mouse.get_pos()

		self.screen.blit(menu, menu_pos)
		pygame.display.flip()

		wait_rect = pygame.Rect(menu_pos, (menu_size[0], menu_wait_h))
		attack_rect = pygame.Rect((menu_pos[0], menu_pos[1] + menu_wait_h), (menu_size[0], menu_attack_h))

		done = False
		while not done:
			event = self.wait_for_user_input()

			if wait_rect.collidepoint(event.pos):
				print("Wait")
				done = True
			elif attack_rect.collidepoint(event.pos):
				print("Attack")
				done = True
		
