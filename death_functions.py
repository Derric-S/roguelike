import colors
from game_states import GameStates
from render_functions import RenderOrder
from game_messages import Message


def kill_player(player):
	player.char = '%'
	player.color = colors.dark_red

	return Message('You died!', colors.red), GameStates.PLAYER_DEAD


def kill_monster(monster):
	death_message = Message('{0} is dead!'.format(monster.name.capitalize()), colors.orange)

	monster.char = '%'
	monster.color = colors.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	monster.render_order = RenderOrder.CORPSE

	return death_message
