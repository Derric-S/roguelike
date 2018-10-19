import colors


def render_all(con, entities, game_map, fov_recompute, root_console, screen_width, screen_height):
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

    # draw all entities in list
    for entity in entities:
        draw_entity(con, entity, game_map.fov)

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