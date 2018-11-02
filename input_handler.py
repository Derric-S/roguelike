from game_states import GameStates


def handle_keys(user_input, game_state):
	if user_input:
		if game_state == GameStates.PLAYERS_TURN:
			if user_input.type == 'KEYDOWN':
				return handle_player_turn_keys(user_input)
			elif user_input.type == 'MOUSEMOTION' or user_input.type == 'MOUSEDOWN':
				return handle_player_mouse_movement(user_input)
		elif game_state == GameStates.PLAYER_DEAD:
			return handle_player_dead_keys(user_input)
		elif game_state == GameStates.TARGETING:
			return handle_targeting_keys(user_input)
		elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
			return handle_inventory_keys(user_input)

	return {}


def handle_player_turn_keys(user_input):
	# movement keys
	#
	# 7 8 9   y k u
	# 4 5 6   h   l
	# 1 2 3   b j n
	key_char = user_input.keychar

	if key_char == 'UP' or key_char == 'k' or key_char == 'KP8':
		return {'move': (0, -1)}
	elif key_char == 'DOWN' or key_char == 'j' or key_char == 'KP2':
		return {'move': (0, 1)}
	elif key_char == 'LEFT' or key_char == 'h' or key_char == 'KP4':
		return {'move': (-1, 0)}
	elif key_char == 'RIGHT' or key_char == 'l' or key_char == 'KP6':
		return {'move': (1, 0)}
	elif key_char == 'y' or key_char == 'KP7':
		return {'move': (-1, -1)}
	elif key_char == 'u' or key_char == 'KP9':
		return {'move': (1, -1)}
	elif key_char == 'b' or key_char == 'KP1':
		return {'move': (-1, 1)}
	elif key_char == 'n' or key_char == 'KP3':
		return {'move': (1, 1)}
	elif key_char == 'KP5':  # wait key
		return {'move': (0, 0)}

	if key_char == 'g':
		return {'pickup': True}
	elif key_char == 'i':
		return{'show inventory': True}
	elif key_char == 'd':
		return {'drop inventory': True}

	# other keys
	if key_char == 'ENTER' and user_input.alt:
		# alt+enter: toggle full screen
		return {'fullscreen': True}
	elif key_char == 'ESCAPE':
		# exit game
		return {'exit': True}

	# no key pressed
	return {}


def handle_mouse(mouse_event):
	if mouse_event:
		(x, y) = mouse_event.cell

		if mouse_event.button == 'LEFT':
			return {'left_click': (x, y)}
		elif mouse_event.button == 'RIGHT':
			return {'right_click': (x, y)}

	return {}


def handle_player_mouse_movement(user_input):
	dx, dy = user_input.cell
	return {'mouse move': (dx, dy)}


def handle_targeting_keys(user_input):
	if user_input.keychar == 'ESCAPE':
		return {'exit': True}

	return {}


def handle_player_dead_keys(user_input):
	key_char = user_input.keychar

	if key_char == 'i':
		return {'show inventory': True}

	if key_char == 'ENTER' and user_input.alt:
		# alt+enter: toggle full screen
		return {'fullscreen': True}
	elif key_char == 'ESCAPE':
		# exit game
		return {'exit': True}

	# no key pressed
	return {}


def handle_inventory_keys(user_input):
	key_char = user_input.keychar

	if not user_input.char:
		return {}

	index = ord(user_input.char) - ord('a')

	if index >= 0:
		return {'inventory index': index}

	if key_char == 'ENTER' and user_input.alt:
		# alt+enter: toggle full screen
		return {'fullscreen': True}
	elif key_char == 'ESCAPE':
		# exit game
		return {'exit': True}

	return {}
