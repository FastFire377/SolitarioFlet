import self
import time

SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500
CARD_OFFSET = 20

import json
import random
import copy

import flet as ft
from card import Card
from slot import Slot


class Suite:
    def __init__(self, suite_name, suite_color):
        self.name = suite_name
        self.color = suite_color


class Rank:
    def __init__(self, card_name, card_value):
        self.name = card_name
        self.value = card_value

class Solitaire(ft.Stack):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []
        self.foundations = []
        self.is_dark_mode = False

        self.restart_button = ft.ElevatedButton(text="Reiniciar Jogo", on_click=self.restart_game, color="white")
        self.undo_button = ft.ElevatedButton(text="Desfazer Jogada", on_click=self.undo_move, color="white")
        self.save_button = ft.ElevatedButton(text="Salvar Jogo", on_click=self.save_game, color="white")
        self.load_button = ft.ElevatedButton(text="Carregar Jogo", on_click=self.load_game, color="white")
        self.mode_button = ft.ElevatedButton(text="Modo Claro", on_click=self.toggle_mode, color="white")

        self.back_card_button = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="Padrão", on_click=lambda e: self.set_card_back("card_back.png")),
                ft.PopupMenuItem(text="Pokemon", on_click=lambda e: self.set_card_back("pokemon_back.jpg")),
                ft.PopupMenuItem(text="YuGiOh", on_click=lambda e: self.set_card_back("yugioh_back.jpg")),
                ft.PopupMenuItem(text="Uno", on_click=lambda e: self.set_card_back("uno_back.png")),
            ],
            icon_color="black" if not self.is_dark_mode else "white"
        )

        self.score_text = ft.Text(f"Score: {self.score}", size=20)

        self.controls = self.initiate_controls()

    def initiate_controls(self):
        button_width = 140  # Largura fixa para todos os botões
        button_height = 30  # Altura fixa para todos os botões (opcional)

        # Criando um espaçamento vertical
        spacing = 10  # Espaçamento entre os botões

        controls = [
            # Contêiner para o botão de reiniciar o jogo
            ft.Container(
                content=self.restart_button,
                top=10,  # Posição vertical do primeiro botão
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o botão de desfazer jogada
            ft.Container(
                content=self.undo_button,
                top=10 + button_height + spacing,  # Calculando a posição vertical do próximo botão
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o botão de salvar jogo
            ft.Container(
                content=self.save_button,
                top=10 + 2 * (button_height + spacing),  # Continuando o espaçamento
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o botão de carregar jogo
            ft.Container(
                content=self.load_button,
                top=10 + 3 * (button_height + spacing),
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o botão de alternar modo claro/escuro
            ft.Container(
                content=self.mode_button,
                top=10 + 4 * (button_height + spacing),
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o botão de fundo da carta
            ft.Container(
                content=self.back_card_button,
                top=10 + 5 * (button_height + spacing),
                right=30,
                width=button_width,
                height=button_height
            ),

            # Contêiner para o texto do score
            ft.Container(
                content=self.score_text,
                top=10 + 6 * (button_height + spacing),  # Posicionando abaixo dos botões
                right=40
            ),
        ]

        return controls

    def toggle_mode(self, e):
        self.is_dark_mode = not self.is_dark_mode
        background_color = "black" if self.is_dark_mode else "white"
        button_color = "#333333" if self.is_dark_mode else "#d3d3d3"
        text_color = "white" if self.is_dark_mode else "black"
        mode_text = "Modo Escuro" if self.is_dark_mode else "Modo Claro"

        # Alterar o fundo da página
        self.page.bgcolor = background_color

        # Alterar a cor dos botões e do texto
        for control in self.controls:
            if isinstance(control.content, ft.ElevatedButton):
                control.content.bgcolor = button_color
                control.content.color = text_color

        # Atualizar a cor do botão de modo
        self.mode_button.text = mode_text
        self.mode_button.color = text_color
        self.mode_button.bgcolor = button_color
        self.mode_button.update()

        # Atualizar a cor do texto do score
        self.score_text.color = text_color
        self.score_text.update()

        # Atualizar a cor dos três pontos
        self.back_card_button.icon_color = text_color
        self.back_card_button.update()

        self.update()
        self.page.update()

    def did_mount(self):
        # Não inicializa o temporizador aqui, para que ele só comece quando o jogo for iniciado
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

    def update(self):
        super().update()  # Chama a função `update` da classe pai

    def restart_game(self, e):
        self.clear_game_board()
        self.controls = self.initiate_controls()
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()
        self.score = 0
        self.update_score()
        self.update()

    def update_score(self):
        self.score += 1
        self.score_text.value = f"Score: {self.score}"
        self.update()

    def check_foundations_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            if card.suite.name == top_card.suite.name and card.rank.value - top_card.rank.value == 1:
                self.update_score()
                return True
        else:
            if card.rank.name == "Ace":
                self.update_score()
                return True
        return False

    def check_tableau_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            if card.suite.color != top_card.suite.color and top_card.rank.value - card.rank.value == 1 and top_card.face_up:
                self.update_score()
                return True
        else:
            if card.rank.name == "King":
                self.update_score()
                return True
        return False

    def update_foundations_with_score(self, state):
        for i, foundation in enumerate(self.foundations):
            for card in state["foundations"][i]:
                foundation.pile.append(card)
                card.slot = foundation
                card.top = foundation.top
                card.left = foundation.left
                self.update_score()

    def set_card_back(self, image_name):
        self.card_back_image = f"/images/{image_name}"
        for card in self.all_cards:
            if not card.face_up:
                card.turn_face_down()
        self.update()
        dlg = ft.AlertDialog(
            title=ft.Text("Traseira alterada!"),
            content=ft.Text(f"Nova imagem: {image_name}"),
            actions=[ft.TextButton("OK", on_click=lambda e: self.close_dialog())]
        )
        dlg.open = True
        self.page.dialog = dlg
        self.update()

    def close_dialog(self):
        self.page.dialog = None
        self.page.update()

    def create_card_deck(self):
        suites = [
            Suite("hearts", "RED"),
            Suite("diamonds", "RED"),
            Suite("clubs", "BLACK"),
            Suite("spades", "BLACK"),
        ]
        ranks = [
            Rank("Ace", 1),
            Rank("2", 2),
            Rank("3", 3),
            Rank("4", 4),
            Rank("5", 5),
            Rank("6", 6),
            Rank("7", 7),
            Rank("8", 8),
            Rank("9", 9),
            Rank("10", 10),
            Rank("Jack", 11),
            Rank("Queen", 12),
            Rank("King", 13),
        ]

        # Cria uma lista com todas as 52 cartas
        self.all_cards = []
        for suite in suites:
            for rank in ranks:
                card = Card(solitaire=self, suite=suite, rank=rank)
                self.all_cards.append(card)
        self.cards = self.all_cards.copy()

    def create_slots(self):
        self.stock = Slot(solitaire=self, top=0, left=0, border=ft.border.all(1))

        self.waste = Slot(solitaire=self, top=0, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(
                Slot(solitaire=self, top=0, left=x, border=ft.border.all(1, "outline"))
            )
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(solitaire=self, top=150, left=x, border=None))
            x += 100

        self.controls.append(self.stock)
        self.controls.append(self.waste)
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)
        self.update()

    def deal_cards(self):
        random.shuffle(self.cards)
        self.controls.extend(self.cards)

        # deal to tableau
        first_slot = 0
        remaining_cards = self.cards

        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        for card in remaining_cards:
            card.place(self.stock)
            print(f"Card in stock: {card.rank.name} {card.suite.name}")

        self.update()

        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        self.update()

        self.save_state()

    def restart_stock(self):
        while len(self.waste.pile) > 0:
            card = self.waste.get_top_card()
            card.turn_face_down()
            card.move_on_top()
            card.place(self.stock)

    def check_win(self):
        cards_num = 0
        for slot in self.foundations:
            cards_num += len(slot.pile)
        if cards_num == 52:
            return True
        return False

    def winning_sequence(self):
        for slot in self.foundations:
            for card in slot.pile:
                card.animate_position = 2000
                card.move_on_top()
                card.top = random.randint(0, SOLITAIRE_HEIGHT)
                card.left = random.randint(0, SOLITAIRE_WIDTH)
                self.update()
        self.controls.append(
            ft.AlertDialog(title=ft.Text("Congratulations! You won!"), open=True)
        )

    def save_state(self):
        state = {
            "stock": list(self.stock.pile),
            "waste": list(self.waste.pile),
            "foundations": [list(slot.pile) for slot in self.foundations],
            "tableau": [list(slot.pile) for slot in self.tableau],
        }
        self.history.append(state)

    def restore_state(self, state):
        self.stock.pile.clear()
        self.waste.pile.clear()
        for slot in self.foundations:
            slot.pile.clear()
        for slot in self.tableau:
            slot.pile.clear()

        for card in state["stock"]:
            self.stock.pile.append(card)
            card.slot = self.stock
            card.top = self.stock.top
            card.left = self.stock.left

        for card in state["waste"]:
            self.waste.pile.append(card)
            card.slot = self.waste
            card.top = self.waste.top
            card.left = self.waste.left

        for i, foundation in enumerate(self.foundations):
            for card in state["foundations"][i]:
                foundation.pile.append(card)
                card.slot = foundation
                card.top = foundation.top
                card.left = foundation.left

        for i, tableau_slot in enumerate(self.tableau):
            for j, card in enumerate(state["tableau"][i]):
                tableau_slot.pile.append(card)
                card.slot = tableau_slot
                card.top = tableau_slot.top + j * CARD_OFFSET
                card.left = tableau_slot.left

            if tableau_slot.pile and not tableau_slot.pile[-1].face_up:
                tableau_slot.pile[-1].turn_face_up()

        self.update()

        for card in self.stock.pile:
            card.face_up = False
            card.turn_face_down()

        self.update()
        self.update_foundations_with_score(state)

    def undo_move(self, e):
        if len(self.history) < 2:
            return

        self.history.pop()
        last_state = self.history[-1]
        self.restore_state(last_state)

    def serialize_state(self):
        state = []
        for card in self.all_cards:
            slot_id = None
            if card.slot is self.stock:
                slot_id = "stock"
            elif card.slot is self.waste:
                slot_id = "waste"
            else:
                for i, foundation in enumerate(self.foundations):
                    if card.slot is foundation:
                        slot_id = f"foundation{i}"
                        break
                if slot_id is None:
                    for i, tableau in enumerate(self.tableau):
                        if card.slot is tableau:
                            slot_id = f"tableau{i}"
                            break
            card_state = card.get_snapshot()
            card_state["slot"] = slot_id
            state.append(card_state)
        return state

    def save_game(self, e):
        state = self.serialize_state()
        self.page.client_storage.set("solitaire_state", json.dumps(state))
        self.page.snack_bar = ft.PopupMenuItem(ft.Text("Jogo salvo!"))
        self.page.snack_bar.open = True
        self.page.update()

    def load_game(self, e):
        saved = self.page.client_storage.get("solitaire_state")
        if not saved:
            dlg = ft.AlertDialog(title=ft.Text("Nenhum jogo salvo encontrado."))
            dlg.open = True
            self.page.dialog = dlg
            self.page.update()
            return

        state = json.loads(saved)

        self.stock.pile.clear()
        self.waste.pile.clear()
        for slot in self.foundations:
            slot.pile.clear()
        for slot in self.tableau:
            slot.pile.clear()

        slot_map = {"stock": self.stock, "waste": self.waste}
        for i, foundation in enumerate(self.foundations):
            slot_map[f"foundation{i}"] = foundation
        for i, tableau in enumerate(self.tableau):
            slot_map[f"tableau{i}"] = tableau

        temp_slots = {slot_id: [] for slot_id in slot_map.keys()}

        for card_state in state:
            for card in self.all_cards:
                if card.suite.name == card_state["suite"] and card.rank.name == card_state["rank"]:
                    card.face_up = card_state["face_up"]
                    card.left = card_state["left"]
                    card.index = card_state["index"]
                    slot_id = card_state["slot"]
                    if slot_id in slot_map:
                        card.slot = slot_map[slot_id]
                        temp_slots[slot_id].append(card)

                    if card.face_up:
                        card.turn_face_up()
                    else:
                        card.turn_face_down()
                    break

        for slot_id, cards_list in temp_slots.items():
            sorted_cards = sorted(cards_list, key=lambda card: card.index)
            if slot_id.startswith("tableau"):
                slot_obj = slot_map[slot_id]
                for i, card in enumerate(sorted_cards):
                    card.index = i
                    card.top = slot_obj.top + i * CARD_OFFSET
                    card.left = slot_obj.left
            else:
                slot_obj = slot_map[slot_id]
                for card in sorted_cards:
                    card.top = slot_obj.top
                    card.left = slot_obj.left
            slot_map[slot_id].pile = sorted_cards

        ordered_cards = []
        ordered_cards.extend(self.stock.pile)
        ordered_cards.extend(self.waste.pile)
        for foundation in self.foundations:
            ordered_cards.extend(foundation.pile)
        for tableau in self.tableau:
            ordered_cards.extend(tableau.pile)

        non_card_controls = [c for c in self.controls if not isinstance(c, Card)]
        self.controls = non_card_controls + ordered_cards
        self.update()

        dlg = ft.AlertDialog(title=ft.Text("Jogo carregado!"))
        dlg.open = True
        self.page.dialog = dlg
        self.page.update()

    def clear_game_board(self):
        # Remove todas as cartas da tela
        for card in self.controls:
            if isinstance(card, Card):
                self.controls.remove(card)

        self.update()