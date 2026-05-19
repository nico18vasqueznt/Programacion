# websocket_server.py
# pip install websockets
# Do not modify this file. Implement all logic in game_engine.py and server_adapter.py.

import asyncio
import uuid
import websockets
import json
from server_adapter2 import handle_request

connected_players = {}  # websocket -> player_id


async def handler(websocket):



    async for message in websocket:
        try:
            request = json.loads(message)
           
            # Inject player_id automatically to request if websocket is already associated with a player
            if websocket in connected_players:
                request["player_id"] = connected_players[websocket]

            if request.get("action") == "join":
                id = str(uuid.uuid4())[:8]  # Generate short unique ID for new player
                request["player_id"] = id
                connected_players[websocket] = id



            # Route request to server adapter and get response
            response = handle_request(request)

                

            # Broadcast the response to all connected clients if it's a broadcast message, or unicast to the specific client if it's a unicast message
            if response.get("message_type") == "broadcast":
                await broadcast(response)
            elif response.get("message_type") == "unicast":
                await unicast(response, websocket)

        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e)
            }
            await broadcast(error_response)

async def broadcast(message):
    """
    Broadcast a message to all connected clients.
    """
    for ws in connected_players:
        await ws.send(json.dumps(message))

async def unicast(message, websocket):
    """
    Send a message to a specific connected client.
    """
    await websocket.send(json.dumps(message))


    

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    print("WebSocket server for Parchis started on ws://localhost:8765")
    asyncio.run(main())