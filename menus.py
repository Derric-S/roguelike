import tdl
import textwrap
import colors


def menu(con, root, header, options, width, screen_width, screen_height):
	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	# calc total height for header
	header_wrapped = textwrap.wrap(header, width)
	header_height = len(header_wrapped)
	height = len(options) + header_height

	# create console for menu's window
	window = tdl.Console(width, height)

	# print header
	window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
	for i, line in enumerate(header_wrapped):
		window.draw_str(0, 0 + i, header_wrapped[i])

	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		window.draw_str(0, y, text, bg=None)
		y += 1
		letter_index += 1

	# blit window to root console
	x = screen_width // 2 - width // 2
	y = screen_height // 2 - height // 2
	root.blit(window, x, y, width, height, 0, 0)


def inventory_menu(con, root, header, inventory, inventory_width, screen_width, screen_height):
	# show menu with each item in inventory
	if len(inventory.items) == 0:
		options = ['Inventory is empty.']
	else:
		options = [item.name for item in inventory.items]

	menu(con, root, header, options, inventory_width, screen_width, screen_height)


def main_menu(con, root_console, background_image, screen_width, screen_height):
	background_image.blit_2x(root_console, 0, 0)

	title = 'Roguelike'
	center = (screen_width - len(title)) // 2
	root_console.draw_str(center, screen_height - 2, title, bg=None, fg=colors.light_yellow)

	menu(con, root_console, '', ['New', 'Continue', 'Quit'], 24, screen_width, screen_height)


def message_box(con, root_console, header, width, screen_width, screen_height):
	menu(con, root_console, header, [], width, screen_width, screen_height)
