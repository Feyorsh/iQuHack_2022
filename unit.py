# -*- coding: utf-8 -*-
#
#  Unit.py, Ice Emblem's unit class.
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


import pygame
import os.path
import random
import logging
import utils


class Unit(object):
	"""
	This class is a unit with stats
	"""
	def __init__(self, name, hp_max, hp, lv, exp, strength, skill, spd, luck, defence, res, move, con, aid, trv, affin, cond, wrank):
		self.name	=	str(name)   	# name of the character
		self.hp_max	=	int(hp_max) 	# maximum hp
		self.hp 	=	int(hp)     	# current hp
		self.prev_hp=	self.hp     	# HP before an attack
		self.lv 	=	int(lv)     	# level
		self.prev_lv = self.lv
		self.exp	=	int(exp)    	# experience
		self.prev_exp = self.exp
		self.strength = int(strength)	# strength determines the damage inflicted to the enemy
		self.skill	=	int(skill)  	# skill chance of hitting the enemy
		self.spd	=	int(spd)    	# speed chance to avoid enemy's attack
		self.luck	=	int(luck)   	# luck influences many things
		self.defence=	int(defence)	# defence reduces phisical damages
		self.res	=	int(res)    	# resistence reduces magical damages
		self.move	=	int(move)   	# movement determines how far the unit can move in a turn
		self.con	=	int(con)    	# constitution, or phisical size. affects rescues.
		self.aid	=	int(aid)    	# max rescuing constitution. units with lower con can be rescued.
		self.trv	=	trv         	# traveler. the unit with whom this unit is traveling.
		self.affin	=	affin       	# elemental affinity. determines compatibility with other units.
		self.cond	=	cond        	# health conditions.
		self.wrank	=	wrank       	# weapons' levels.
		self.items	=	[]          	# list of items
		self.played	=	False       	# wether unit was used or not in a turn
		self.color	=	None        	# team color
		self.coord	=	None
		path = os.path.relpath(os.path.join('sprites', self.name + '.png'))
		try:
			self.image = pygame.image.load(path).convert_alpha()
			new_size = utils.resize_keep_ratio(self.image.get_size(), (200, 200))
			self.image = pygame.transform.smoothscale(self.image, new_size)
		except pygame.error as e:
			logging.warning(_("Couldn't load %s! Loading default image") % path)
			no_image_path = os.path.relpath(os.path.join('sprites', 'no_image.png'))
			self.image = pygame.image.load(no_image_path).convert_alpha()

	def __str__(self):
		return """
Unit: "%s"
	HP: %d/%d
	LV: %d	EXP: %d
	Str: %d	Skill: %d
	Spd: %d	Luck: %d
	Def: %d	Res: %d
	Move: %d	Con: %d
	Aid: %d	Trv: %s
	Affin: %s	Cond: %s
	WRank: %s
	Items: %s
	Played: %s
""" % (self.name,
			self.hp, self.hp_max, self.lv, self.exp, self.strength,
			self.skill, self.spd, self.luck, self.defence,
			self.res, self.move, self.con, self.aid, self.trv,
			self.affin, self.cond, self.wrank, self.items, self.played)

	def render_info(self, font):
		"""
		Returns a Surface containing all informations about a unit.
		The specified font will be used to render the text and will
		determine the width and haight of the Surface
		"""

		font_linesize = font.get_linesize()

		# will "parse" this text and render each attribute individually
		info_text = self.__str__()

		info_list = []
		max_width = 0
		counter = 0

		# which attributes to show
		show = ['HP', 'LV', 'EXP', 'Str', 'Skill', 'Spd', 'Luck', 'Def']

		# split newlines and tabs except the "indentation" tabs
		for raw_line in iter(info_text.splitlines()):
			for line in iter(raw_line.strip().split('\t')):
				attr = line.split(':')
				if attr[0] in show:
					# it's in the list: render it
					info_list.append(font.render(line, 1, (255, 255, 255)))
					# max_width and counter to compute surface's size
					max_width = max(info_list[-1].get_size()[0], max_width)
					counter += 1

		dim = (max_width * 2 + 20, counter * font_linesize // 2)
		surface = pygame.Surface(dim).convert_alpha()
		surface.fill((0, 0, 0, 0))  # transparent surface

		for i, line in enumerate(info_list):
			# position each attribute in two colums
			pos = (i % 2 * (max_width + 20), i // 2 * font_linesize)
			surface.blit(line, pos)

		return surface

	def get_active_weapon(self):
		"""Returns the active weapon if it exists, None otherwise."""
		for item in self.items:
			if item.active:
				return item
		return None

	def give_weapon(self, weapon, active=True):
		"""Gives a weapon to the unit. The weapon becomes active by default."""
		weapon.active = active
		self.items.append(weapon)

	def inflict_damage(self, dmg):
		"""Inflicts damages to the unit."""
		self.hp -= dmg
		if self.hp <= 0:
			self.hp = 0
			print(_("%s died") % self.name)

	def get_weapon_range(self):
		active_weapon = self.get_active_weapon()
		return active_weapon.range if active_weapon is not None else 1

	def get_attack_distance(self):
		return self.get_weapon_range() + self.move

	def number_of_attacks(self, enemy, distance):
		"""
		Returns a tuple: how many times this unit can attack the enemy
		and how many times the enemy can attack this unit in a single battle
		"""
		self_attacks = enemy_attacks = 1

		if self.spd > enemy.spd:
			self_attacks += 1
		elif enemy.spd > self.spd:
			enemy_attacks += 1

		self_range = self.get_weapon_range()
		enemy_range = enemy.get_weapon_range()
		if self_range < distance:
			self_attacks = 0
		if enemy_range < distance:
			enemy_attacks = 0

		return (self_attacks, enemy_attacks)

	def life_percent(self):
		return int(float(self.hp) / float(self.hp_max) * 100.0)

	def attack(self, enemy):
		"""
		1 -> miss
		2 -> null damage
		3 -> triple hit
		4 -> hit
		"""

		active_weapon = self.get_active_weapon()

		if active_weapon is None or active_weapon.uses == 0:
			print(_("%s attacks %s with his bare hands") % (self.name, enemy.name))
			hit_probability = self.skill * 2 + self.luck / 2
			dmg = self.strength - enemy.defence
			critical_probability = self.skill // 2 - enemy.luck
		else:
			print(_("%s attacks %s with %s") % (self.name, enemy.name, active_weapon.name))
			hit_probability = (self.skill * 2) + active_weapon.hit + (self.luck / 2)
			dmg = (self.strength + active_weapon.might) - enemy.defence # TODO
			critical_probability = self.skill // 2 + active_weapon.crit - enemy.luck

		print("Dmg: %d  Hit: %d" % (dmg, hit_probability))
		hit = random.randrange(0, 100) < hit_probability
		critical = random.randrange(0, 100) < critical_probability

		if not hit:
			print("Misses")
			ret = 1
		elif dmg <= 0:
			print("Null attack")
			ret = 2
		elif critical:
			print("Triple attack")
			enemy.inflict_damage(dmg*3)
			if active_weapon is not None:
				active_weapon.use()
			ret = 3
		else:
			print(_("%s inflicts %s %d damages") % (self.name, enemy.name, dmg))
			enemy.inflict_damage(dmg)
			if active_weapon is not None:
				active_weapon.use()
			ret = 4
		return ret

	def value(self):
		"""
		the return value is used by ai to choose who enemy attack
		"""
		# TODO add type unit influence
		return self.hp + self.strength + self.skill + self.spd + self.luck + self.defence

	def prepare_battle(self):
		self.prev_hp = self.hp
		self.prev_lv = self.lv

	def get_damage(self):
		return self.prev_hp - self.hp

	def experience(self, enemy):
		self.prev_exp = self.exp
		exp = 1
		damages = enemy.get_damage()
		if damages > 0:
			lv_diff = abs(enemy.lv - self.lv)
			if enemy.lv < self.lv:
				exp += damages // lv_diff
			else:
				exp += damages * lv_diff
			exp += random.randrange(0, self.luck // 2 + 1)
		if enemy.hp == 0:
			exp += damages // 2
		if exp > 100:
			exp = 100
		self.exp += exp
		if self.exp >= 100:
			self.exp %= 100
			self.level_up()

		print(_("%s gained %d experience points! EXP: %d") % (self.name, exp, self.exp))

	def gained_exp(self):
		"""Return the gained experience with latest battle"""
		if self.exp > self.prev_exp:
			return self.exp - self.prev_exp
		return self.exp + 100 - self.prev_exp

	def level_up(self):
		self.prev_lv = self.lv
		self.lv += 1
		print(_("%s levelled up!") % self.name)

	def levelled_up(self):
		"""Returns True if the latest attack caused a level-up"""
		return self.lv > self.prev_lv

	def is_dead(self):
		return self.hp == 0


class Flying(Unit):
	def __init__(self, *args):
		super().__init__(*args)


class Water(Unit):
	def __init__(self, *args):
		super().__init__(name, *args)


class Team(object):
	"""Every unit is part of a Team."""

	number_of_teams = 0

	def __init__(self, name, color, relation, ai, units, boss):
		"""
		name [str]: name of the Team
		color [tuple of 3 ints]: color of the Team
		relation [number]: used to represent relationship between teams.
			Two Teams can be allied, neutral or enemy. If the difference
			between the two teams' value is 0 they are allied, if it is
			1 they are neutral otherwise they are enemy.
		ai [AI]: if ai is an AI object ai will be used for this team
		my_turn [bool]: if it is this team's turn
		units [list of units]: units part of the team
		"""
		self.number_of_teams += 1
		self.name = name
		self.color = color
		self.relation = relation
		self.ai = ai
		for unit in units:
			unit.color = color
		self.units = units
		self.boss = boss

	def __del__(self):
		self.number_of_teams -= 1

	def __str__(self):
		units = "["
		for unit in self.units:
			units += unit.name + ', '
		return '%s: %s]' % (self.name, units)

	def is_mine(self, unit):
		"""Tells wether a unit belongs to this player or not"""
		return unit in self.units

	def is_turn_over(self):
		for unit in self.units:
			if not unit.played:
				return False
		return True

	def end_turn(self):
		for unit in self.units:
			unit.played = False
		self.my_turn = False
		print(_("Team %s ends its turn") % self.name)

	def begin_turn(self):
		self.my_turn = True
		for unit in self.units:
			unit.played = False
		print(_("Team %s begins its turn") % self.name)

	def is_defeated(self):
		return len(self.units) == 0

	def remove_unit(self, unit):
		unit.color = None
		self.units.remove(unit)

	def is_enemy(self, team):
		return abs(team.relation - self.relation) > 1

	def is_neutral(self, team):
		return abs(team.relation - self.relation) == 1

	def is_allied(self, team):
		return team.relation == self.relation

	def is_boss(self, unit):
		return unit == self.boss


class UnitsManager(object):
	def __init__(self, teams):
		self.teams = teams
		self.active_team = self.teams[0]
		self.units = [u for t in teams for u in t.units]

	def get_team(self, color):
		for team in self.teams:
			if team.color == color:
				return team

	def switch_turn(self):
		self.active_team.end_turn()
		active_team_index = (self.teams.index(self.active_team) + 1) % len(self.teams)
		self.active_team = self.teams[active_team_index]
		self.active_team.begin_turn()
		return self.active_team

	def get_units(self, **kwargs):
		found = []
		for unit in self.units:
			for attr in kwargs:
				if getattr(unit, attr) == kwargs[attr]:
					if unit not in found:
						found.append(unit)
		return found

	def get_enemies(self, team):
		enemies = []
		for enemy in self.units:
			if enemy not in enemies:
				enemy_team = self.get_team(enemy.color)
				if enemy_team.is_enemy(team):
					enemies += enemy_team.units
		return enemies
				

	def are_enemies(self, unit1, unit2):
		team1 = self.get_team(unit1.color)
		team2 = self.get_team(unit2.color)
		return team1.is_enemy(team2)

	def are_neutrals(self, unit1, unit2):
		team1 = self.get_team(unit1.color)
		team2 = self.get_team(unit2.color)
		return team1.is_neutral(team2)

	def are_allied(self, unit1, unit2):
		team1 = self.get_team(unit1.color)
		team2 = self.get_team(unit2.color)
		return team1.is_allied(team2)

	def kill_unit(self, unit):
		self.units.remove(unit)
		self.get_team(unit.color).units.remove(unit)
