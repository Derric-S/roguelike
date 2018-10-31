import colors
from enum import Enum
from game_states import GameStates
from menus import inventory_menu


class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3


def get_names_under_mouse(mouse_coordinates, entities, game_map):
	x, y = mouse_coordinates

	names = [entity.name for entity in entities
			 if entity.x == x and entity.y == y and game_map.fov[entity.x, entity.y]]
	names = ', '.join(names)

	return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color, string_color):
	# calculate width of bar
	bar_width = int(float(value) / maximum * total_width)

	# render background first
	panel.draw_rect(x, y, total_width, 1, None, bg=back_color)

	# render bar on top
	if bar_width > 0:
		panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)

	# centered text with values
	text = name + ': ' + str(value) + '/' + str(maximum)
	x_centered = x + int((total_width-len(text)) / 2)

	panel.draw_str(x_centered, y, text, fg=string_color, bg=None)


def render_all(con, panel, mouse_console, entities, player, game_map, fov_recompute, root_console, message_log,
			   screen_width, screen_height, bar_width, panel_height, panel_y, mouse_coordinates, path, game_state):

	if fov_recompute:
		# draw all tiles in map
		for x, y in game_map:
			wall = not game_map.transparent[x, y]

			if game_map.fov[x, y]:
				if wall:
					con.draw_char(x, y, None, fg=None, bg=colors.light_wall)
				else:
					con.draw_char(x, y, None, fg=None, bg=colors.light_ground)

				game_map.explored[x][y] = True

			elif game_map.explored[x][y]:
				if wall:
					con.draw_char(x, y, None, fg=None, bg=colors.dark_wall)
				else:
					con.draw_char(x, y, None, fg=None, bg=colors.dark_ground)

	entities_in_render_order = sorted(entities, key=lambda order: order.render_order.value)

	# draw all entities in list
	for entity in entities_in_render_order:
		draw_entity(con, entity, game_map.fov)

	root_console.blit(con, 0, 0, screen_width, screen_height, 0, 0)

	panel.clear(fg=colors.white, bg=colors.darker_grey)

	# print game messages one line at a time
	y = 1
	for message in message_log.messages:
		panel.draw_str(message_log.x, y, message.text, bg=None, fg=message.color)
		y += 1

	render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
			   colors.light_red, colors.darker_red, colors.white)

	panel.draw_str(1, 0, get_names_under_mouse(mouse_coordinates, entities, game_map), bg=colors.darker_grey)

	root_console.blit(panel, 0, panel_y, screen_width, panel_height, 0, 0)

	if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
		if game_state == GameStates.SHOW_INVENTORY:
			inventory_title = 'Press the key next to an item to use it, or Esc to cancel. \n'
		else:
			inventory_title = 'Press the key next to an item to drop it , or Esc to cancel. \n'

		inventory_menu(con, root_console, inventory_title, player.inventory, 50, screen_width, screen_height)

	# highlight path to mouse position
	mouse_x, mouse_y = mouse_coordinates
	try:
		if game_map.explored[mouse_x][mouse_y]:
			mouse_console.clear(bg=colors.lightest_green)
			for x, y in path:
				root_console.blit(mouse_console, x, y, width=None, height=None, bg_alpha=0.4)
	except IndexError:
		pass


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)


def draw_entity(con, entity, fov):
	# only draw entity if in fov
	if fov[entity.x, entity.y]:
		con.draw_char(entity.x, entity.y, entity.char, entity.color, bg=None)


def clear_entity(con, entity):
	# erase the character that represents this entity
	con.draw_char(entity.x, entity.y, ' ', entity.color, bg=None)
