from src.solitaire import Solitaire

SLOT_WIDTH = 70
SLOT_HEIGHT = 100

import flet as ft

class Slot(ft.Container):
    def __init__(self, solitaire, top, left, border):
        super().__init__()
        self.pile=[]
        self.width=SLOT_WIDTH
        self.height=SLOT_HEIGHT
        self.left=left
        self.top=top
        self.on_click=self.click
        self.solitaire=solitaire
        self.border=border
        self.border_radius = ft.border_radius.all(6)

    def get_top_card(self):
        if len(self.pile) > 0:
            return self.pile[-1]

    def click(self, e):
        if self == self.solitaire.stock:
            self.solitaire.restart_stock()
        else:
            # Aqui você pode adicionar a lógica de movimentação de cartas para o slot.
            top_card = self.get_top_card()
            if top_card:
                # Verifica se a carta foi colocada corretamente e, se sim, aumenta o score
                if isinstance(self.solitaire, Solitaire):
                    if self.solitaire.check_tableau_rules(top_card, self) or self.solitaire.check_foundations_rules(
                            top_card, self):
                        self.solitaire.update_score()  # Atualiza o score
