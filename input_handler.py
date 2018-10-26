def handle_keys(user_input):
	if user_input.type == 'KEYDOWN':
		# movement keys
		# 7 8 9  y k u
		# 4 5 6  h   l
		# 1 2 3  b j n
		key_char = user_input.key

		if user_input.key == 'UP' or key_char == 'k' or key_char == 'KP8':
			return {'move': (0, -1)}
		elif user_input.key == 'DOWN' or key_char == 'j' or key_char == 'KP2':
			return {'move': (0, 1)}
		elif user_input.key == 'LEFT' or key_char == 'h' or key_char == 'KP4':
			return {'move': (-1, 0)}
		elif user_input.key == 'RIGHT' or key_char == 'l' or key_char == 'KP6':
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

		# other keys
		if user_input.key == 'ENTER' and user_input.alt:
			# alt+enter: toggle full screen
			return {'fullscreen': True}
		elif user_input.key == 'ESCAPE':
			# exit game
			return {'exit': True}

	elif user_input.type == 'MOUSEDOWN':
		# mouse movement
		dx, dy = user_input.cell
		return {'mouse move': (dx, dy)}

	# no key pressed
	return {}
