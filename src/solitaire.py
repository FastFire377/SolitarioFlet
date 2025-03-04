SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random

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
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT

        self.restart_button = ft.ElevatedButton(text="Reiniciar Jogo", on_click=self.restart_game)
        self.controls.append(ft.Container(content=self.restart_button, top=10, right=100))
        
        self.history = []
        self.undo_button = ft.ElevatedButton(text="Desfazer Jogada", on_click=self.undo_move)
        self.controls.append(ft.Container(content=self.undo_button, top=10, right=150))
        


    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

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

        self.cards = []

        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(solitaire=self, suite=suite, rank=rank))

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

        # place remaining cards to stock pile
        for card in remaining_cards:
            card.place(self.stock)
            print(f"Card in stock: {card.rank.name} {card.suite.name}")

        self.update()

        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        self.update()


    def check_foundations_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.name == top_card.suite.name
                and card.rank.value - top_card.rank.value == 1
            )
        else:
            return card.rank.name == "Ace"

    def check_tableau_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.color != top_card.suite.color
                and top_card.rank.value - card.rank.value == 1
                and top_card.face_up
            )
        else:
            return card.rank.name == "King"

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

    def save_current_state(self):
        state = self.get_game_state()
        self.history.append(state)

    def get_game_state(self):
        state = {
            "stock": [self.card_to_dict(card) for card in self.stock.pile],
            "waste": [self.card_to_dict(card) for card in self.waste.pile],
            "foundations": [[self.card_to_dict(card) for card in slot.pile] for slot in self.foundations],
            "tableau": [[self.card_to_dict(card) for card in slot.pile] for slot in self.tableau]
        }
        return state

    def card_to_dict(self, card):
        return {
            "suite": card.suite.name,
            "rank": card.rank.name,
            "face_up": card.face_up,
            "top": card.top,
            "left": card.left
        }

    def load_game_state(self, state):
        self.controls = [self.restart_button, self.undo_button]  # Preserve buttons
        self.create_card_deck()  # Ensure we have a fresh set of cards

        def dict_to_card(card_dict):
            suite = next(s for s in self.cards if s.suite.name == card_dict["suite"])
            rank = next(r for r in self.cards if r.rank.name == card_dict["rank"])
            card = next(c for c in self.cards if c.suite == suite and c.rank == rank)
            card.face_up = card_dict["face_up"]
            card.top = card_dict["top"]
            card.left = card_dict["left"]
            return card

        self.stock.pile = [dict_to_card(card) for card in state["stock"]]
        self.waste.pile = [dict_to_card(card) for card in state["waste"]]
        self.foundations = [[dict_to_card(card) for card in slot] for slot in state["foundations"]]
        self.tableau = [[dict_to_card(card) for card in slot] for slot in state["tableau"]]

        all_cards = self.stock.pile + self.waste.pile + [card for slot in self.foundations for card in slot] + [card for slot in self.tableau for card in slot]
        self.controls.extend(all_cards)

        self.update()

    def undo_move(self, e):
        print("history:", self.history)
        if len(self.history) > 1:
            self.history.pop()  # Remove o estado atual
            previous_state = self.history[-1]  # Pega o estado anterior
            self.load_game_state(previous_state)

    def clear_game_board(self):
        # Remove todas as cartas da tela
        for card in self.controls[:]:  # Copia a lista para evitar problemas ao remover
            if isinstance(card, Card):
                self.controls.remove(card)

        # Limpa o histórico
        self.history.clear()

        self.update()

    def restart_game(self, e):
        self.clear_game_board()
        self.history = []
        self.controls = [
            ft.Container(content=self.restart_button, top=10, right=100),
            ft.Container(content=self.undo_button, top=10, right=150)
        ]
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()
        self.update()

