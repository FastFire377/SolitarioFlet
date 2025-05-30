import flet as ft

CARD_WIDTH = 70
CARD_HEIGTH = 100
DROP_PROXIMITY = 30
CARD_OFFSET = 20


class Card(ft.GestureDetector):
    def __init__(self, solitaire, suite, rank):
        super().__init__()
        self.mouse_cursor = ft.MouseCursor.MOVE
        self.drag_interval = 5
        self.on_pan_start = self.start_drag
        self.on_pan_update = self.drag
        self.on_pan_end = self.drop
        self.on_tap = self.click
        self.on_double_tap = self.doubleclick
        self.suite = suite
        self.rank = rank
        self.face_up = False
        self.top = None
        self.left = None
        self.solitaire = solitaire
        self.slot = None
        self.index = None
        self.content = ft.Container(
            width=CARD_WIDTH,
            height=CARD_HEIGTH,
            border_radius=ft.border_radius.all(6),
            content=ft.Image(src="/images/card_back.png"),
        )
        
        self.draggable_pile = [self]

    def turn_face_up(self):
        """Reveals card"""
        self.face_up = True
        self.content.content.src = f"/images/{self.rank.name}_{self.suite.name}.svg"
        self.solitaire.update()

    def turn_face_down(self):
        """Vira a carta para baixo com a imagem de fundo atual"""
        self.face_up = False
        self.content.content.src = self.solitaire.card_back_image  # Usa a imagem salva

        # Verifica se a carta está na interface antes de atualizar
        if self.page:
            self.page.update()  # Atualiza a interface toda, evitando erro

    def move_on_top(self):
        """Brings draggable card pile to the top of the stack"""

        for card in self.draggable_pile:
            self.solitaire.controls.remove(card)
            self.solitaire.controls.append(card)
        self.solitaire.update()

    def bounce_back(self):
        """Returns draggable pile to its original position"""
        for card in self.draggable_pile:
            if card.slot in self.solitaire.tableau:
                card.top = card.slot.top + card.slot.pile.index(card) * CARD_OFFSET
            else:
                card.top = card.slot.top
            card.left = card.slot.left
        self.solitaire.update()

    def place(self, slot):
        """Place draggable pile to the slot"""

        for card in self.draggable_pile:
            # Define a posição vertical da carta
            if slot in self.solitaire.tableau:
                # Para slots do tableau, empilha as cartas com um offset
                card.top = slot.top + len(slot.pile) * CARD_OFFSET
            else:
                # Para outros slots, coloca as cartas na mesma posição vertical
                card.top = slot.top
            card.left = slot.left

            # Remove a carta do slot original, se existir
            if card.slot is not None:
                if card in card.slot.pile:  # Verifica se a carta está na pilha do slot anterior
                    card.slot.pile.remove(card)
                else:
                    print(f"Warning: Card {card.rank.name} {card.suite.name} not found in previous slot's pile.")

            # Atualiza o slot da carta para o novo slot
            card.slot = slot

            # Adiciona a carta à pilha do novo slot
            slot.pile.append(card)
            card.index = len(slot.pile) - 1

        # Verifica se o jogo foi vencido
        if self.solitaire.check_win():
            self.solitaire.winning_sequence()

        # Atualiza a interface e salva o estado do jogo
        self.solitaire.update()
        self.solitaire.save_state()

    def get_draggable_pile(self):
        """
        Retorna a lista de cartas que serão arrastadas a partir da carta atual.
        Se a carta não for encontrada na pile do slot, assume que é sozinha.
        """
        if self.slot is not None and self.slot not in (self.solitaire.stock, self.solitaire.waste):
            try:
                idx = self.slot.pile.index(self)
            except ValueError:
                idx = 0
            self.draggable_pile = self.slot.pile[idx:]
        else:
            self.draggable_pile = [self]


    def start_drag(self, e: ft.DragStartEvent):
        if self.face_up:
            self.get_draggable_pile()
            self.move_on_top()

    def drag(self, e: ft.DragUpdateEvent):
        if self.face_up:
            for card in self.draggable_pile:
                card.top = (
                    max(0, self.top + e.delta_y)
                    + self.draggable_pile.index(card) * CARD_OFFSET
                )
                card.left = max(0, self.left + e.delta_x)
                self.solitaire.update()

    def drop(self, e: ft.DragEndEvent):
        if self.face_up:
            for slot in self.solitaire.tableau:
                if (
                    abs(self.top - (slot.top + len(slot.pile) * CARD_OFFSET))
                    < DROP_PROXIMITY
                    and abs(self.left - slot.left) < DROP_PROXIMITY
                ) and self.solitaire.check_tableau_rules(self, slot):
                    self.place(slot)
                    return

            if len(self.draggable_pile) == 1:
                for slot in self.solitaire.foundations:
                    if (
                        abs(self.top - slot.top) < DROP_PROXIMITY
                        and abs(self.left - slot.left) < DROP_PROXIMITY
                    ) and self.solitaire.check_foundations_rules(self, slot):
                        self.place(slot)
                        return

            self.bounce_back()

    def click(self, e):
        if self.slot in self.solitaire.tableau:
            if not self.face_up and self == self.slot.get_top_card():
                self.turn_face_up()
        elif self.slot == self.solitaire.stock:
            self.move_on_top()
            self.place(self.solitaire.waste)
            self.turn_face_up()

    def doubleclick(self, e):
        self.get_draggable_pile()
        if self.face_up and len(self.draggable_pile) == 1:
            self.move_on_top()
            for slot in self.solitaire.foundations:
                if self.solitaire.check_foundations_rules(self, slot):
                    self.place(slot)
                    return
                
    def get_snapshot(self):
        return  {
                "suite": self.suite.name,
                "rank": self.rank.name,
                "face_up": self.face_up,
                "top": self.top,
                "left": self.left,
                "index": self.index
            }

    def restore_snapshot(self, snapshot):
        self.suite = snapshot["suite"]
        self.rank = snapshot["rank"]
        self.face_up = snapshot["face_up"]
        self.top = snapshot["top"]
        self.left = snapshot["left"]
        self.slot = snapshot["slot"]