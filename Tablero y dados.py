# ========================================================
# 📦 LIBRERÍAS E IMPORTACIONES
# ========================================================
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Game_Clientt import GameClient 
from json import loads

# ========================================================
# 🎲 RECURSOS VISUALES (IMÁGENES DE DADOS)
# ========================================================
dices_images = {
    1: "dice-six-faces-one.png",
    2: "dice-six-faces-two.png",
    3: "dice-six-faces-three.png",
    4: "dice-six-faces-four.png",
    5: "dice-six-faces-five.png",
    6: "dice-six-faces-six.png"
}

# ========================================================
# 📏 MAPA DE PÍXELES DEL TABLERO
# ========================================================
COORDENADAS_TABLERO = {
    # 🔴 JUGADOR ROJO (Esquina superior izquierda)
    "carcel_red": [
        [60, 60],   # Ficha 1
        [100, 60],  # Ficha 2
        [60, 100],  # Ficha 3
        [100, 100]  # Ficha 4
    ],
    
    # 🔵 JUGADOR AZUL (Esquina superior derecha)
    "carcel_blue": [
        [390, 60],  # Ficha 1
        [430, 60],  # Ficha 2
        [390, 100], # Ficha 3
        [430, 100]  # Ficha 4
    ],
    
    # 🛣️ RECORRIDO DE CASILLAS COMUNES
    26: [232, 162], 27: [232, 140], 28: [232, 120], 29: [232, 98], 
    30: [232, 77],  31: [232, 56],  32: [232, 35],  33: [232, 13],
    34: [265, 13],  35: [265, 35],  36: [265, 56],  37: [265, 77], 
    38: [265, 98],  39: [265, 120], 40: [265, 140], 41: [265, 162], 
    42: [265, 185],

    43: [185, 208], 44: [162, 208], 45: [140, 208], 46: [120, 208], 
    47: [98, 208],  48: [77, 208],  49: [56, 208],  50: [35, 208],
    51: [13, 235],  52: [13, 265], 
    53: [35, 290],  54: [56, 290],  55: [77, 290],  56: [98, 290],  # Meta/Salida Roja
    57: [120, 290], 58: [140, 290], 59: [162, 290],

    60: [208, 312], 61: [208, 335], 62: [208, 358], 63: [208, 378], 
    64: [208, 400], 65: [208, 421], 66: [208, 442], 67: [208, 464],
    68: [235, 485], 
    1:  [265, 485],  
    2:  [290, 464],  3:  [290, 442],  4:  [290, 421],  5:  [290, 400], 
    6:  [290, 378],  7:  [290, 358],  8:  [290, 335],

    # --- Pasillo Horizontal Derecho ---
    9:  [312, 290],  10: [335, 290], 11: [358, 290], 12: [378, 290], 
    13: [400, 290],  14: [421, 290], 15: [442, 290], 16: [464, 290],
    17: [485, 265],  # Salida Azul
    18: [485, 235], 
    19: [464, 208],  20: [421, 208],  21: [400, 208], 22: [378, 208], 
    23: [358, 208],  24: [335, 208],  25: [312, 208],
    
    0:  [208, 185],  # Salida Roja
}

# ========================================================
# 🪟 CLASE PRINCIPAL DE LA INTERFAZ (GUI)
# ========================================================
class NewWindow(QMainWindow):
    def __init__(self, name):
        super().__init__()       
        self.player_name = name
        self.my_color = None
        self.my_id = None
        self.setWindowTitle("Parchís - Jugador: " + name)
        self.display_width = 640
        self.display_height = 550

        # --------------------------------------------------------
        # 🎨 CONFIGURACIÓN DE COMPONENTES VISUALES (UI)
        # --------------------------------------------------------
        # Fondo del Tablero
        self.image_label = QLabel()
        pixmap = QPixmap(r"C:\Users\USUARIO\Downloads\Parchís.svg.png")
        self.image_label.setPixmap(pixmap.scaled(int(pixmap.width()/2), int(pixmap.height()/2)))
        self.image_label.resize(self.display_width, 480)

        # Botón para lanzar dados
        self.button_roll = QPushButton('Lanzar dados')
        self.button_roll.clicked.connect(self.roll_dice)
        
        # Etiqueta de estado del juego
        self.label_status = QLabel("Esperando jugadores...")
        self.label_status.setStyleSheet("font-weight: bold; color: darkblue;")
        
        # Selector de pieza (Fichas del 1 al 4)
        self.label_move = QLabel("Selecciona Ficha a Mover:")
        self.combo_pieces = QComboBox()
        self.combo_pieces.addItems(["Ficha 1", "Ficha 2", "Ficha 3", "Ficha 4"])
        
        # Botón para confirmar movimiento
        self.button_move = QPushButton("Mover Ficha")
        self.button_move.clicked.connect(self.send_move)

        # Etiquetas para mostrar los dados visualmente
        self.dice0_label = QLabel()
        self.dice1_label = QLabel()
        
        # --------------------------------------------------------
        # 📐 DISEÑO DE CAPAS Y MATRICES (LAYOUT)
        # --------------------------------------------------------
        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.image_label, 0, 0, 1, 4)
        
        layout.addWidget(self.label_status, 1, 0, 1, 4, Qt.AlignCenter)
        layout.addWidget(self.button_roll, 2, 0, 1, 2)
        
        layout.addWidget(self.label_move, 2, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(self.combo_pieces, 2, 3, 1, 1)
        layout.addWidget(self.button_move, 3, 2, 1, 2)
        
        layout.addWidget(self.dice0_label, 4, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self.dice1_label, 4, 1, 1, 1, Qt.AlignCenter)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # --------------------------------------------------------
        # 🔴🔵 CREACIÓN DE LAS FICHAS GRÁFICAS (SPRITES)
        # --------------------------------------------------------
        self.fichas_red = []
        self.fichas_blue = []
        
        for i in range(4):
            lbl = QLabel(self)
            lbl.setFixedSize(20, 20)
            lbl.setStyleSheet("background-color: red; border: 2px solid white; border-radius: 10px;")
            lbl.hide()
            self.fichas_red.append(lbl)
            
        for i in range(4):
            lbl = QLabel(self)
            lbl.setFixedSize(20, 20)
            lbl.setStyleSheet("background-color: blue; border: 2px solid white; border-radius: 10px;")
            lbl.hide()
            self.fichas_blue.append(lbl)

       # --------------------------------------------------------
        # 🔌 CONEXIÓN CON EL SERVIDOR DE PARCHÍS
        # --------------------------------------------------------
        self.client = GameClient("ws://127.0.0.1:8765", self.handle_response) 
        self.client.connect()
        self.client.send_action("join", player_name=name)

    # ========================================================
    # 🕹️ ACCIONES Y ENVIOS DE INFORMACIÓN (MÉTODOS OUTGOING)
    # ========================================================
    def roll_dice(self):
        """ Envía la orden al servidor para ejecutar roll_dice(player_id) """
        self.client.send_action("roll_dice")

    def send_move(self):
        """ Envía la orden al servidor para mover la pieza elegida """
        piece_id = self.combo_pieces.currentIndex()
        # Se envía dice_used=None para activar la auto-selección en el backend
        self.client.send_action("move_piece", piece_id=piece_id, dice_used=None)

    # ========================================================
    # 📩 RECEPCIÓN Y RENDERIZADO DEL JUEGO (MÉTODOS INCOMING)
    # ========================================================
    def handle_response(self, response):
        print("Received response:", response)
        data = response
        
        # --- Control de Mensajes y Errores ---
        if "error" in data:
            self.label_status.setText(f"Error: {data['error']}")
            return
        
        if "message" in data:
            self.label_status.setText(data["message"])

        if "winner" in data:
            self.label_status.setText(f"🎉 ¡El jugador {data['winner']} ha ganado la partida! 🎉")
            return

        if "board_state" not in data:
            return
            
        board_state = data["board_state"]
        
        # --- Actualización de Turnos y Estados ---
        current_player_id = board_state.get("current_player")
        game_state = board_state.get("game_state")
        dices_rem = board_state.get("dices_remaining", [])
        
        # Sincronizar ID y color local en la primera respuesta
        if not self.my_color and "players" in board_state:
            for p in board_state["players"]:
                if p["name"] == self.player_name:
                    self.my_color = p["color"]
                    self.my_id = p["id"]

        # Mostrar estado actual de la partida en el texto informativo
        if game_state == "waiting_for_players":
            self.label_status.setText("Esperando a que se conecte el segundo jugador...")
        elif game_state == "defining_turn_order":
            self.label_status.setText("Fase 1: Lanzando dados para definir el orden de turnos.")
        elif game_state == "in_progress":
            if current_player_id == self.my_id:
                if dices_rem:
                    self.label_status.setText(f"Tu turno. Dados pendientes por mover: {dices_rem}")
                else:
                    self.label_status.setText("Tu turno. ¡Lanza los dados!")
            else:
                self.label_status.setText("Esperando el movimiento del oponente...")
        elif game_state == "finished":
            self.label_status.setText("Fin de la partida.")

        # --- Renderizado Visual de Dados ---
        dices_value = board_state.get("dices_value", (0, 0))
        if dices_value[0] != 0:
            self.dice0_label.setPixmap(QPixmap(dices_images.get(dices_value[0], "")).scaled(60, 60))
        if dices_value[1] != 0:
            self.dice1_label.setPixmap(QPixmap(dices_images.get(dices_value[1], "")).scaled(60, 60))

        # --- Renderizado Dinámico de Fichas ---
        players = board_state.get("players", [])
        for player in players:
            color = player["color"]
            pieces = player["pieces"]
            
            widgets_fichas = self.fichas_red if color == "red" else self.fichas_blue
            
            for idx, pos in enumerate(pieces):
                widget_ficha = widgets_fichas[idx]
                
                # Si la posición en el servidor es -1 significa que está en la cárcel
                if pos == -1: 
                    coord_key = f"carcel_{color}"
                    x, y = COORDENADAS_TABLERO[coord_key][idx]
                else: 
                    # Buscar la casilla común en nuestro diccionario de píxeles
                    if pos in COORDENADAS_TABLERO:
                        x, y = COORDENADAS_TABLERO[pos]
                    else:
                        # Si llega a casillas especiales/metas aún no mapeadas
                        x, y = 100 + (idx * 25), 200 

                widget_ficha.move(x, y)
                widget_ficha.show()
                widget_ficha.raise_()

# ========================================================
# 🚀 EJECUCIÓN DEL PROGRAMA
# ========================================================
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Nombre del jugador (Instancia única)
    ventana = NewWindow("Jugador1") 
    ventana.show()
    sys.exit(app.exec_())