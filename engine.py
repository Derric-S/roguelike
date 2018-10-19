import tdl
import colors
from entity import Entity
from input_handler import handle_keys
from render_functions import clear_all, render_all
from map_utils import make_map


def main():
    # initializations
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    game_colors = {
        'dark_wall': (0, 0, 100),
        'dark_ground': (50, 50, 150)
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', colors.white)
    entities = [player]  # list to store all entities on map

    tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

    root_console = tdl.init(screen_width, screen_height, title='Roguelike')
    con = tdl.Console(screen_width, screen_height)

    # create map
    game_map = tdl.map.Map(map_width, map_height)
    make_map(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    # MAIN GAME LOOP

    while not tdl.event.is_window_closed():
        # render all entities
        render_all(con, entities, game_map, root_console, screen_width, screen_height, game_colors)

        tdl.flush()

        # clear entities last position
        clear_all(con, entities)

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
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:  # move key pressed
            dx, dy = move
            if game_map.walkable[player.x + dx, player.y + dy]:
                player.move(dx, dy)

        if exit:  # exit game
            return True

        if fullscreen:  # set fullscreen
            tdl.set_fullscreen(not tdl.get_fullscreen())


if __name__ == '__main__':
    main()
