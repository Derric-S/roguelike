import tdl
import colors

from tcod import image_load

from entity import get_blocking_entities_at_location
from game_states import GameStates
from input_handler import handle_keys, handle_mouse, handle_main_menu
from render_functions import clear_all, render_all
from death_functions import kill_monster, kill_player
from game_messages import Message
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box


def main():
	constants = get_constants()

	tdl.set_font('arial12x12.png', greyscale=True, altLayout=True)

	root_console = tdl.init(constants['screen_width'], constants['screen_height'], title=constants['window_title'])
	con = tdl.Console(constants['screen_width'], constants['screen_height'])
	panel = tdl.Console(constants['screen_width'], constants['panel_height'])
	mouse_console = tdl.Console(1, 1)

	player = None
	entities = []
	game_map = None
	message_log = None
	game_state = None

	show_main_menu = True
	show_load_error_message = False

	main_menu_background_image = image_load('menu_background.png')

	while not tdl.event.is_window_closed():
		for event in tdl.event.get():
			if event.type == 'KEYDOWN':
				user_input = event
				break
		else:
			user_input = None

		if show_main_menu:
			main_menu(con, root_console, main_menu_background_image, constants['screen_width'],
					  constants['screen_height'])

			if show_load_error_message:
				message_box(con, root_console, 'No save game', 50, constants['screen_width'],
							constants['screen_height'])

			tdl.flush()

			action = handle_main_menu(user_input)

			new_game = action.get('new_game')
			load_saved_game = action.get('load_game')
			exit_game = action.get('exit')

			if show_load_error_message and (new_game or load_saved_game or exit_game):
				show_load_error_message = False
			elif new_game:
				player, entities, game_map, message_log, game_state = get_game_variables(constants)
				game_state = GameStates.PLAYERS_TURN

				show_main_menu = False
			elif load_saved_game:
				try:
					player, entities, game_map, message_log, game_state = load_game()
					show_main_menu = False
				except FileNotFoundError:
					show_load_error_message = True
			elif exit_game:
				break

		else:
			root_console.clear()
			con.clear()
			panel.clear()
			play_game(player, entities, game_map, message_log, game_state, root_console, con, panel, mouse_console,
					  constants)

			show_main_menu = True


def play_game(player, entities, game_map, message_log, game_state, root_console, con, panel, mouse_console, constants):
	tdl.set_font('arial12x12.png', greyscale=True, altLayout=True)

	fov_recompute = True

	previous_game_state = game_state

	targeting_item = None

	mouse_coordinates = (0, 0)
	mouse_location_x, mouse_location_y = mouse_coordinates

	highlight_path = False

	# MAIN GAME LOOP

	while not tdl.event.is_window_closed():
		if fov_recompute:
			game_map.compute_fov(player.x, player.y, fov=constants['fov_algorithm'], radius=constants['fov_radius'],
								 light_walls=constants['fov_light_walls'])

		if highlight_path:
			path = game_map.compute_path(player.x, player.y, mouse_location_x, mouse_location_y)
		else:
			path = [(mouse_location_x, mouse_location_y)]

		# render all entities
		render_all(con, panel, mouse_console, entities, player, game_map, fov_recompute, root_console, message_log,
				   constants['screen_width'], constants['screen_height'], constants['bar_width'],
				   constants['panel_height'], constants['panel_y'], mouse_coordinates, path, game_state)

		tdl.flush()

		# clear entities last positions
		clear_all(con, entities)

		fov_recompute = False

		# event handling
		for event in tdl.event.get():
			if event.type == 'KEYDOWN':
				user_input = event
				break
			elif event.type == 'MOUSEMOTION':
				mouse_coordinates = event.cell
				mouse_location_x, mouse_location_y = mouse_coordinates
			elif event.type == 'MOUSEDOWN':
				user_mouse_input = event
				break

		else:
			user_input = None
			user_mouse_input = None

		if not (user_input or user_mouse_input):
			continue

		action = handle_keys(user_input, game_state)  # check what was pressed
		mouse_action = handle_mouse(user_mouse_input)

		move = action.get('move')
		pickup = action.get('pickup')
		show_inventory = action.get('show inventory')
		inventory_index = action.get('inventory index')
		drop_inventory = action.get('drop inventory')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')

		left_click = mouse_action.get('left_click')
		right_click = mouse_action.get('right_click')

		player_turn_results = []

		if (move or left_click) and game_state == GameStates.PLAYERS_TURN:
			# make variables based on type of move
			if move:
				dx, dy = move

				destination_x = player.x + dx
				destination_y = player.y + dy
			else:
				destination_x, destination_y = left_click

			# Do checks and move player / attack
			if destination_x == player.x and destination_y == player.y:
				# player is waiting
				fov_recompute = True
				game_state = GameStates.ENEMY_TURN

			elif game_map.walkable[destination_x, destination_y]:
				if left_click:
					path = game_map.compute_path(player.x, player.y, mouse_location_x, mouse_location_y)

					dx = path[0][0] - player.x
					dy = path[0][1] - player.y

					destination_x = path[0][0]
					destination_y = path[0][1]

				target = get_blocking_entities_at_location(entities, destination_x, destination_y)

				if target:
					attack_results = player.fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					player.move(dx, dy)

					fov_recompute = True

				game_state = GameStates.ENEMY_TURN

		elif pickup and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.item and entity.x == player.x and entity.y == player.y:
					pickup_results = player.inventory.add_item(entity)
					player_turn_results.extend(pickup_results)
					break
			else:
				message_log.add_message(Message('There is nothing here to pick up.', colors.yellow))

		if show_inventory:
			previous_game_state = game_state
			game_state = GameStates.SHOW_INVENTORY

		if drop_inventory:
			previous_game_state = game_state
			game_state = GameStates.DROP_INVENTORY

		if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
				player.inventory.items):
			item = player.inventory.items[inventory_index]

			if game_state == GameStates.SHOW_INVENTORY:
				player_turn_results.extend(player.inventory.use(item, entities=entities, game_map=game_map))
			elif game_state == GameStates.DROP_INVENTORY:
				player_turn_results.extend(player.inventory.drop_item(item))

		if game_state == GameStates.TARGETING:
			if left_click:
				target_x, target_y = left_click

				item_use_results = player.inventory.use(targeting_item, entities=entities, game_map=game_map,
														target_x=target_x, target_y=target_y)
				player_turn_results.extend(item_use_results)
			elif right_click:
				player_turn_results.append({'targeting_cancelled': True})

		if exit:
			if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
				game_state = previous_game_state
			elif game_state == GameStates.TARGETING:
				player_turn_results.append({'targeting_cancelled': True})
			else:
				save_game(player, entities, game_map, message_log, game_state)

				return True

		if fullscreen:
			tdl.set_fullscreen(not tdl.get_fullscreen())

		for player_turn_result in player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')
			item_added = player_turn_result.get('item added')
			item_consumed = player_turn_result.get('consumed')
			item_dropped = player_turn_result.get('item dropped')
			targeting = player_turn_result.get('targeting')
			targeting_cancelled = player_turn_result.get('targeting_cancelled')

			if message:
				message_log.add_message(message)

			if targeting_cancelled:
				game_state = previous_game_state

				message_log.add_message(Message('Targeting cancelled'))

			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)

				else:
					message = kill_monster(dead_entity)

				message_log.add_message(message)

			if item_added:
				entities.remove(item_added)

				game_state = GameStates.ENEMY_TURN

			if item_consumed:
				game_state = GameStates.ENEMY_TURN

			if item_dropped:
				entities.append(item_dropped)

				game_state = GameStates.ENEMY_TURN

			if targeting:
				previous_game_state = GameStates.PLAYERS_TURN
				game_state = GameStates.TARGETING

				targeting_item = targeting
				message_log.add_message(targeting_item.item.targeting_message)

		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(player, game_map, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							message_log.add_message(message)

						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)

							else:
								message = kill_monster(dead_entity)

							message_log.add_message(message)

							if game_state == GameStates.PLAYER_DEAD:
								break

					if game_state == GameStates.PLAYER_DEAD:
						break

			else:
				game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
	main()
