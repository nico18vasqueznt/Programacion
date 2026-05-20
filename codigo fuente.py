from random import randint

# game_engine.py
# -------------------------------------------------
# Lógica completa del juego Parchís para 2 jugadores.
# -------------------------------------------------

COLORS = ["red", "blue"]
GAME_STATES = ["waiting_for_players", "defining_turn_order", "in_progress", "finished"]

def random_dices():
    return randint(1, 6), randint(1, 6)

# Estado de la fase de definición de turno inicial
first_turn = {"draw": set(), "rolls": 0, "dice_value": 0, "turn": None}

# ✅ FIX: dices_value como lista (no tupla) para que JSON lo maneje igual siempre
board_state = {
    "players": [],
    "current_player": None,
    "dices_value": [0, 0],
    "dices_remaining": [],
    "extra_turn": False,
    "game_state": GAME_STATES[0]
}

# =================================================
# UTILIDAD INTERNA
# =================================================

def _broadcast_state():
    """Devuelve el board_state completo como broadcast. Usado en casi todas las respuestas."""
    return {"message_type": "broadcast", "board_state": board_state}

# =================================================
# PLAYER MANAGEMENT
# =================================================

def add_player(player_name, playerID):
    global board_state

    if len(board_state["players"]) == 2:
        return _broadcast_state()

    color = COLORS[len(board_state["players"])]
    board_state["players"].append({
        "id": playerID,
        "name": player_name,
        "color": color,
        "pieces": [-1, -1, -1, -1]
    })

    if len(board_state["players"]) == 2:
        board_state["game_state"] = GAME_STATES[1]
        board_state["current_player"] = board_state["players"][0]["id"]

    return _broadcast_state()


def get_my_id(player_id):
    return {"message_type": "unicast", "id": player_id}


def get_players():
    return {"message_type": "unicast", "players": board_state["players"]}


# =================================================
# TURN MANAGEMENT
# =================================================

def get_current_player():
    return {"message_type": "unicast", "current_player": board_state["current_player"]}


def next_turn():
    global board_state
    if not board_state["players"]:
        board_state["current_player"] = None
        return

    current = board_state["current_player"]
    player_ids = [p["id"] for p in board_state["players"]]
    if current not in player_ids:
        board_state["current_player"] = player_ids[0]
        return

    idx = player_ids.index(current)
    board_state["current_player"] = player_ids[(idx + 1) % len(player_ids)]


def is_player_turn(player_id):
    return board_state["current_player"] == player_id


# =================================================
# DICE LOGIC
# =================================================

def roll_dice(player_id):
    global board_state, first_turn

    # =========================================
    # FASE 1: DEFINIR QUIÉN EMPIEZA
    # =========================================
    if board_state["game_state"] == GAME_STATES[1]:
        if not is_player_turn(player_id):
            return {"message_type": "unicast", "error": "No es tu turno de lanzar."}

        dice0, dice1 = random_dices()
        # ✅ FIX: guardar como lista, no tupla
        board_state["dices_value"] = [dice0, dice1]
        first_turn["rolls"] += 1

        if dice0 > first_turn["dice_value"]:
            first_turn["dice_value"] = dice0
            first_turn["turn"] = player_id
            first_turn["draw"] = {player_id}
        elif dice0 == first_turn["dice_value"]:
            first_turn["draw"].add(player_id)

        # Pasar turno temporal al siguiente jugador
        player_ids = [p["id"] for p in board_state["players"]]
        idx = player_ids.index(player_id)
        board_state["current_player"] = player_ids[(idx + 1) % len(player_ids)]

        # Cuando todos lanzaron, decidir quién inicia
        if first_turn["rolls"] == len(board_state["players"]):
            if len(first_turn["draw"]) == 1:
                board_state["current_player"] = first_turn["turn"]
                board_state["game_state"] = GAME_STATES[2]
            else:
                # Empate: reiniciar fase 1
                first_turn["rolls"] = 0
                first_turn["dice_value"] = 0
                first_turn["turn"] = None
                first_turn["draw"] = set()
                board_state["current_player"] = board_state["players"][0]["id"]

        # ✅ FIX CRÍTICO: siempre retornar board_state completo para que el cliente pinte los dados
        return _broadcast_state()

    # =========================================
    # FASE 2: JUEGO NORMAL
    # =========================================
    elif board_state["game_state"] == GAME_STATES[2]:
        if not is_player_turn(player_id):
            return {"message_type": "unicast", "error": "No es tu turno."}

        if board_state.get("dices_remaining"):
            return {"message_type": "unicast", "error": "Debes mover una ficha antes de lanzar."}

        dice0, dice1 = random_dices()
        # ✅ FIX: guardar como lista
        board_state["dices_value"] = [dice0, dice1]

        if dice0 == dice1:
            board_state["dices_remaining"] = [dice0, dice1, dice0, dice1]
            board_state["extra_turn"] = True
        else:
            board_state["dices_remaining"] = [dice0, dice1]
            board_state["extra_turn"] = False

        if not player_has_moves(player_id):
            board_state["dices_remaining"] = []
            next_turn()

        # ✅ FIX CRÍTICO: siempre retornar board_state completo
        return _broadcast_state()

    return {"message_type": "unicast", "error": "Acción no permitida en este estado."}


def get_last_dice():
    return {"message_type": "unicast", "dices_value": board_state["dices_value"]}


# =================================================
# PIECE MANAGEMENT
# =================================================

def get_player_pieces(player_id):
    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if not player:
        return {"message_type": "unicast", "error": "Jugador no encontrado."}
    return {"message_type": "unicast", "pieces": player["pieces"]}


def get_piece_position(player_id, piece_id):
    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if not player:
        return {"message_type": "unicast", "error": "Jugador no encontrado."}
    if piece_id < 0 or piece_id >= len(player["pieces"]):
        return {"message_type": "unicast", "error": "Pieza inválida."}
    return {"message_type": "unicast", "position": player["pieces"][piece_id]}


def can_piece_move(player, piece_id, dice):
    pos = player["pieces"][piece_id]

    # En cárcel solo sale con 6
    if pos == -1:
        return dice == 6

    # No puede pasarse de la meta
    if pos + dice > get_home_position(player["color"]):
        return False

    # No puede caer en bloqueo
    if detect_blockade(pos + dice):
        return False

    return True


def player_has_moves(player_id):
    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if not player:
        return False
    for dice in board_state["dices_remaining"]:
        for i in range(4):
            if can_piece_move(player, i, dice):
                return True
    return False


def move_piece(player_id, piece_id, dice_used):
    global board_state

    try:
        piece_id = int(piece_id)
        if dice_used is not None:
            dice_used = int(dice_used)
    except (TypeError, ValueError):
        return {"message_type": "unicast", "error": "Datos inválidos."}

    if not is_player_turn(player_id):
        return {"message_type": "unicast", "error": "No es tu turno."}

    # Auto-selección del primer dado disponible si no se especificó
    if dice_used is None:
        if not board_state["dices_remaining"]:
            return {"message_type": "unicast", "error": "No hay dados disponibles. Lanza primero."}
        dice_used = board_state["dices_remaining"][0]

    if dice_used not in board_state["dices_remaining"]:
        return {"message_type": "unicast", "error": "Ese dado no está disponible."}

    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if not player:
        return {"message_type": "unicast", "error": "Jugador no encontrado."}

    if not can_piece_move(player, piece_id, dice_used):
        return {"message_type": "unicast", "error": "Movimiento no válido para esa ficha y dado."}

    pos = player["pieces"][piece_id]

    # Salir de cárcel
    if pos == -1:
        player["pieces"][piece_id] = get_start_position(player["color"])
    else:
        player["pieces"][piece_id] = pos + dice_used

    moved_to = player["pieces"][piece_id]
    board_state["dices_remaining"].remove(dice_used)

    # Captura
    captured = check_capture(player_id, moved_to)
    if captured:
        send_piece_home(captured["player_id"], captured["piece_id"])

    # Victoria
    if has_player_won(player_id):
        board_state["game_state"] = "finished"
        return {"message_type": "broadcast", "winner": player_id, "board_state": board_state}

    # Cambio de turno si se usaron todos los dados
    if not board_state["dices_remaining"]:
        if not board_state["extra_turn"]:
            next_turn()
        board_state["extra_turn"] = False
        board_state["dices_value"] = [0, 0]

    return _broadcast_state()


# =================================================
# BOARD LOGIC
# =================================================

START_POSITIONS = {"red": 0, "blue": 17}
HOME_POSITIONS  = {"red": 56, "blue": 73}

def get_start_position(color):
    return START_POSITIONS.get(color, 0)

def get_home_position(color):
    return HOME_POSITIONS.get(color, 56)

def get_board():
    return {"message_type": "unicast", "board_state": board_state}

def is_safe_square(position):
    safe_squares = [0, 8, 17, 25, 34, 42, 51, 56, 73]
    return position in safe_squares

def detect_blockade(position):
    count = 0
    for player in board_state["players"]:
        count += player["pieces"].count(position)
    return count >= 2


# =================================================
# CAPTURE & RULES
# =================================================

def check_capture(player_id, position):
    if is_safe_square(position):
        return None
    for player in board_state["players"]:
        if player["id"] != player_id:
            for idx, piece_pos in enumerate(player["pieces"]):
                if piece_pos == position:
                    return {"player_id": player["id"], "piece_id": idx}
    return None

def send_piece_home(player_id, piece_id):
    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if player:
        player["pieces"][piece_id] = -1

def can_exit_jail():
    return 6 in board_state["dices_remaining"]


# =================================================
# WIN CONDITION
# =================================================

def has_player_won(player_id):
    player = next((p for p in board_state["players"] if p["id"] == player_id), None)
    if not player:
        return False
    home = get_home_position(player["color"])
    return all(pos == home for pos in player["pieces"])

def check_game_finished():
    return any(has_player_won(p["id"]) for p in board_state["players"])


# =================================================
# GAME STATE
# =================================================

def get_game_status():
    return {"message_type": "unicast", "game_state": board_state["game_state"]}

def get_state():
    return {"message_type": "unicast", "state": board_state}

def reset_game():
    global board_state, first_turn
    board_state = {
        "players": [],
        "current_player": None,
        "dices_value": [0, 0],
        "dices_remaining": [],
        "extra_turn": False,
        "game_state": GAME_STATES[0]
    }
    first_turn = {"draw": set(), "rolls": 0, "dice_value": 0, "turn": None}
    return _broadcast_state()
