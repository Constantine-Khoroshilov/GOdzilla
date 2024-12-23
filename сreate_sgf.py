from sgfmill import sgf

def create_sgf(filename, moves,size): # пример moves [('b', (4, 4)), ('w', (4, 6)), ('b', (2, 3))]
    game = sgf.Sgf_game.from_string(f"(;FF[4]GM[1]SZ[{size}];)")

    for i in range(len(moves)):
        new_node = game.extend_main_sequence()
        new_node.set_move(moves[i][0],moves[i][1])

    with open(f"{filename}", "wb") as f:
        f.write(game.serialise())