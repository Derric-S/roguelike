import colors
from enum import Enum


class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3


def render_all(con, entities, player, game_map, fov_recompute, root_console, screen_width, screen_height):
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

	con.draw_str(1, screen_height - 2, 'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

	root_console.blit(con, 0, 0, screen_width, screen_height, 0, 0)


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
