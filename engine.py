import tdl
import colors

from components.fighter import Fighter
from entity import Entity, get_blocking_entities_at_location
from game_states import GameStates
from input_handler import handle_keys
from render_functions import clear_all, render_all, RenderOrder
from map_utils import GameMap, make_map
from death_functions import kill_monster, kill_player


def main():
	# initializations
	screen_width = 80
	screen_height = 50
	map_width = 80
	map_height = 45

	room_max_size = 10
	room_min_size = 6
	max_rooms = 30

	fov_algorithm = 'BASIC'
	fov_light_walls = True
	fov_radius = 10

	max_monster_per_room = 3

	fighter_component = Fighter(hp=30, defense=2, power=5)
	player = Entity(0, 0, '@', colors.white, 'Player', blocks=True,
					render_order=RenderOrder.ACTOR, fighter=fighter_component)
	entities = [player]  # list to store all entities on map

	tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

	root_console = tdl.init(screen_width, screen_height, title='Roguelike')
	con = tdl.Console(screen_width, screen_height)

	# create map
	game_map = GameMap(map_width, map_height)
	make_map(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player,
			 entities, max_monster_per_room)

	fov_recompute = True

	game_state = GameStates.PLAYERS_TURN

	# MAIN GAME LOOP

	while not tdl.event.is_window_closed():
		if fov_recompute:
			game_map.compute_fov(player.x, player.y, fov=fov_algorithm, radius=fov_radius, light_walls=fov_light_walls)
		# render all entities
		render_all(con, entities, player, game_map, fov_recompute, root_console, screen_width, screen_height)

		tdl.flush()

		# clear entities last positions
		clear_all(con, entities)

		fov_recompute = False

		# event handling
		for event in tdl.event.get():
			if event.type == 'KEYDOWN':
				user_input = event
				break
		else:
			user_input = None

		if not user_input:
			continue

		action = handle_keys(user_input)  # check what key was pressed

		move = action.get('move')
		exit_game = action.get('exit')
		fullscreen = action.get('fullscreen')

		player_turn_results = []

		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			destination_x = player.x + dx
			destination_y = player.y + dy

			if game_map.walkable[destination_x, destination_y]:
				target = get_blocking_entities_at_location(entities, destination_x, destination_y)

				if target:
					attack_results = player.fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					player.move(dx, dy)

					fov_recompute = True

				game_state = GameStates.ENEMY_TURN

		if exit_game:
			return True

		if fullscreen:
			tdl.set_fullscreen(not tdl.get_fullscreen())

		for player_turn_result in player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')

			if message:
				print(message)

			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)

				else:
					message = kill_monster(dead_entity)

				print(message)

		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(player, game_map, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							print(message)

						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)

							else:
								message = kill_monster(dead_entity)

							print(message)

							if game_state == GameStates.PLAYER_DEAD:
								break

					if game_state == GameStates.PLAYER_DEAD:
						break

			else:
				game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
	main()
