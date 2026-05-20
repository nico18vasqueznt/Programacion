import os
import json
import sys
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt5.QtGui import QPixmap, QBrush, QPen
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, 
    QLabel, QPushButton, QComboBox, QGraphicsScene, QGraphicsView, 
    QGraphicsEllipseItem, QInputDialog, QMessageBox, QGraphicsPixmapItem
)
from Game_Clientt import GameClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🎲 Diccionario de dados generado dinámicamente
dices_images = {i: os.path.join(BASE_DIR, f"dice-six-faces-{['one','two','three','four','five','six'][i-1]}.png") for i in range(1, 7)}

# 📍 COORDENADAS DEL TABLERO
COORDENADAS_TABLERO = {
    "carcel_red": [[55, 55], [95, 55], [55, 95], [95, 95]],
    "carcel_blue": [[385, 55], [425, 55], [385, 95], [425, 95]],
    0: [208, 185], 1: [208, 162], 2: [208, 140], 3: [208, 118], 4: [208, 95], 5: [208, 72],
    6: [185, 55], 7: [162, 55], 8: [140, 55], 9: [118, 55], 10: [95, 55], 11: [72, 55],
    12: [55, 72], 13: [55, 95], 14: [55, 118], 15: [55, 140], 16: [55, 162], 17: [265, 485],
    18: [290, 464], 19: [290, 442], 20: [290, 421], 21: [290, 400], 22: [290, 378], 23: [290, 358],
    24: [290, 335], 25: [310, 315], 26: [335, 315], 27: [358, 315], 28: [380, 315], 29: [402, 315],
    30: [425, 315], 31: [447, 315], 32: [447, 290], 33: [447, 265], 34: [447, 240], 35: [447, 215],
    36: [447, 190], 37: [447, 165], 38: [447, 140], 39: [447, 118], 40: [447, 95], 41: [447, 72],
    42: [425, 55], 43: [402, 55], 44: [380, 55], 45: [358, 55], 46: [335, 55], 47: [315, 55],
    48: [290, 55], 49: [265, 55], 50: [240, 55], 51: [215, 55], 52: [208, 72], 53: [208, 95],
    54: [208, 118], 55: [208, 140], 56: [208, 162], 57: [265, 464], 58: [265, 442], 59: [265, 421],
    60: [265, 400], 61: [265, 378], 62: [265, 358], 63: [265, 335], 64: [265, 315], 65: [240, 290],
    66: [215, 290], 67: [190, 290], 68: [165, 290], 69: [140, 290], 70: [118, 290], 71: [95, 290],
    72: [72, 290], 73: [55, 290]
}

# 🪟 VENTANA PRINCIPAL
class NewWindow(QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.player_name, self.my_id, self.my_color = name, None, None
        self.setWindowTitle(f"Parchís – {name}"); self.setFixedSize(700, 720)

        # UI Base
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene); self.view.setFixedSize(520, 520)
        layout.addWidget(self.view, alignment=Qt.AlignCenter)

        # Tablero
        pixmap = QPixmap(os.path.join(BASE_DIR, "Parchís.svg.png"))
        self.board_item = QGraphicsPixmapItem(pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.scene.addItem(self.board_item)

        # Fichas (Simplificado en un solo bucle de configuración)
        self.fichas = {"red": [], "blue": []}
        for color, qt_color in [("red", Qt.red), ("blue", Qt.blue)]:
            for i in range(4):
                ficha = QGraphicsEllipseItem(0, 0, 24, 24)
                ficha.setBrush(QBrush(qt_color))
                ficha.setPen(QPen(Qt.white, 2))
                ficha.setPos(*COORDENADAS_TABLERO[f"carcel_{color}"][i])
                self.scene.addItem(ficha)
                self.fichas[color].append(ficha)

        # Estado y Controles
        self.label_status = QLabel("Esperando jugadores...")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet("font-size:18px; font-weight:bold; color:#1a237e;")
        layout.addWidget(self.label_status)

        controls = QGridLayout()
        self.button_roll = QPushButton("🎲 Lanzar Dados", clicked=self.roll_dice)
        self.combo_pieces = QComboBox()
        self.combo_pieces.addItems([f"Ficha {i+1}" for i in range(4)])
        self.button_move = QPushButton("♟️ Mover", clicked=self.send_move)

        for i, widget in enumerate([self.button_roll, self.combo_pieces, self.button_move]):
            controls.addWidget(widget, 0, i)

        # Dados Visuales
        self.dice0, self.dice1 = QLabel(), QLabel()
        for i, d in enumerate([self.dice0, self.dice1]):
            d.setFixedSize(70, 70)
            d.setStyleSheet("background:white; border:2px solid black;")
            d.setAlignment(Qt.AlignCenter)
            controls.addWidget(d, 1, i)
            self.set_dice(d, 1)

        layout.addLayout(controls)
        self.client = GameClient("ws://127.0.0.1:8765", self._safe_handle_response)

    def set_dice(self, label, value):
        value = int(value)
        if 1 <= value <= 6:
            pix = QPixmap(dices_images.get(value))
            if not pix.isNull():
                label.setPixmap(pix.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        label.setText(str(value) if 1 <= value <= 6 else "?")

    def iniciar_conexion(self):
        self.client.connect()
        self.client.send_action("join", player_name=self.player_name)

    def roll_dice(self): self.client.send_action("roll_dice")
    def send_move(self): self.client.send_action("move_piece", piece_id=self.combo_pieces.currentIndex(), dice_used=None)

    def _safe_handle_response(self, response):
        QMetaObject.invokeMethod(self, "_handle_response_main_thread", Qt.QueuedConnection, Q_ARG(str, json.dumps(response)))

    @pyqtSlot(str)
    def _handle_response_main_thread(self, payload):
        try: self.handle_response(json.loads(payload))
        except Exception: pass

    def handle_response(self, data):
        print("\n========== RESPONSE ==========\n", data)
        if "error" in data:
            self.label_status.setText(f"⚠️  {data['error']}"); return

        board = data.get("board_state", {})
        players = board.get("players", [])
        
        if "winner" in data:
            w_name = next((p["name"] for p in players if p["id"] == data["winner"]), data["winner"])
            QMessageBox.information(self, "🏆 ¡Ganador!", f"¡{w_name} ganó el juego!")
            self.label_status.setText(f"🏆 ¡{w_name} ganó!"); return

        if not board: return

        # Identificar jugador actual
        for p in players:
            if p["name"] == self.player_name:
                self.my_id, self.my_color = p["id"], p["color"]

        # 🧠 Mapeo inteligente de los estados del juego (Reemplaza el árbol if/elif largo)
        dices_rem = board.get("dices_remaining", [])
        is_my_turn = board.get("current_player") == self.my_id
        
        status_map = {
            "waiting_for_players": "⏳ Esperando al segundo jugador...",
            "defining_turn_order": "🎲 Lanza el dado para definir quién empieza" if is_my_turn else "⏳ El oponente lanza para definir turno...",
            "in_progress": f"🟢 TU TURNO — Mueve una ficha (dados: {dices_rem})" if dices_rem else "🟢 TU TURNO — Lanza los dados" if is_my_turn else "🔴 Turno del oponente...",
            "finished": "🏁 Juego terminado"
        }
        self.label_status.setText(status_map.get(board.get("game_state", ""), self.label_status.text()))

        # Actualizar dados en pantalla
        dices = board.get("dices_value", [0, 0])
        if any(dices):
            self.set_dice(self.dice0, dices[0])
            self.set_dice(self.dice1, dices[1])

        # Actualizar la posición de las fichas en el tablero
        for p in players:
            color, pieces = p["color"], p["pieces"]
            for idx, pos in enumerate(pieces):
                key = f"carcel_{color}" if pos == -1 else pos
                x, y = COORDENADAS_TABLERO.get(key, [238, 238])
                self.fichas[color][idx].setPos(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    nombre, ok = QInputDialog.getText(None, "Jugador", "Tu nombre:")
    if ok and nombre.strip():
        w = NewWindow(nombre.strip())
        w.show(); w.iniciar_conexion()
        sys.exit(app.exec_())