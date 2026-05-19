# server_adapter.py
# You can modify this file by adding more functions or changing the existing ones.


import game_engine



# Function to handle incoming requests from the WebSocket server and route them
# to the appropriate game engine functions.
def handle_request(request):
    action = request.get("action")
    player_id = request.get("player_id")

    # -----------------------------
    # GAME CONTROL
    # -----------------------------

    if action == "initialize":
        return game_engine.initialize_game()

    if action == "reset":
        return game_engine.reset_game()

    if action == "get_status":
        return game_engine.get_game_status()

    if action == "get_state":
        return game_engine.get_state()

    # -----------------------------
    # PLAYER MANAGEMENT
    # -----------------------------

    if action == "join":
        return game_engine.add_player(request.get("player_name"),request.get("player_id"))

    if action == "remove_player":
        return game_engine.remove_player(player_id)

    if action == "get_players":
        return game_engine.get_players()
    
    if action=="get_my_id":
        return game_engine.get_my_id(player_id)
    
    

    # -----------------------------
    # TURN MANAGEMENT
    # -----------------------------

    if action == "current_player":
        return {"status": "ok", "player_id": game_engine.get_current_player()}

    if action == "next_turn":
        return game_engine.next_turn()

    # -----------------------------
    # DICE
    # -----------------------------

    if action == "roll_dice":
        return game_engine.roll_dice(player_id)

    if action == "get_last_dice":
        return {"status": "ok", "value": game_engine.get_last_dice()}
    
    if action == "give_sixes":
        return game_engine.give_sixes(player_id)

    # -----------------------------
    # PIECES
    # -----------------------------

    if action == "get_pieces":
        return {
            "status": "ok",
            "pieces": game_engine.get_player_pieces(player_id)
        }

    if action == "move_piece":
        return game_engine.move_piece(player_id, request.get("piece_id"),request.get('dice_used'))

    if action == "set_piece":
        return game_engine.set_piece_position(player_id,request.get("piece_id"),request.get("position"))
            
    # -----------------------------
    # BOARD
    # -----------------------------

    if action == "get_board":
        return {"status": "ok", "board": game_engine.get_board()}

    return {
        "status": "error",
        "message": "Invalid action"
    }