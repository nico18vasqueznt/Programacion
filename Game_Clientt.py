
import asyncio
import threading
import json
import websockets

class GameClient:
    def __init__(self, uri, callback):
        self.uri = uri
        self.callback = callback
        self.loop = asyncio.new_event_loop()
        self.websocket = None

    def connect(self):
        # Inicia la escucha en un hilo secundario para no congelar la ventana de PyQt5
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._listen())

    async def _listen(self):
        async for websocket in websockets.connect(self.uri):
            self.websocket = websocket
            try:
                async for message in websocket:
                    data = json.loads(message)
                    # Envía los cambios del servidor directo a la función handle_response de tu ventana
                    self.callback(data)
            except websockets.ConnectionClosed:
                continue

    def send_action(self, action, **kwargs):
        # Envía las acciones (join, roll_dice, move_piece) hacia el servidor
        payload = {"action": action, **kwargs}
        if self.websocket and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(payload)), 
                self.loop
            )