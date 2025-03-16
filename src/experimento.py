CARD_WIDTH = 70
CARD_HEIGTH = 100
DROP_PROXIMITY = 20
CARD_OFFSET = 20

SLOT_WIDTH = 70
SLOT_HEIGHT = 100
 
import flet as ft
 
class Slot(ft.Container):
   def __init__(self, top, left):
       super().__init__()
       self.pile=[]
       self.width=SLOT_WIDTH
       self.height=SLOT_HEIGHT
       self.left=left
       self.top=top
       self.border=ft.border.all(1)
 


class Card(ft.GestureDetector):
   def __init__(self, solitaire, color):
       super().__init__()
       self.slot = None
       self.mouse_cursor=ft.MouseCursor.MOVE
       self.drag_interval=5
       self.on_pan_start=self.start_drag
       self.on_pan_update=self.drag
       self.on_pan_end=self.drop
       self.left=None
       self.top=None
       self.solitaire = solitaire
       self.color = color
       self.content=ft.Container(bgcolor=self.color, width=CARD_WIDTH, height=CARD_HEIGTH)
   
   def move_on_top(self):
       """Moves draggable card to the top of the stack"""
       self.solitaire.controls.remove(self)
       self.solitaire.controls.append(self)
       self.solitaire.update()
 
   def bounce_back(self):
       """Returns card to its original position"""
       self.top = self.slot.top
       self.left = self.slot.left
       self.update()
 
   def place(self, slot):
        # remove card from it's original slot, if exists
        if self.slot is not None:
            self.slot.pile.remove(self)

        # change card's slot to a new slot
        self.top = slot.top + len(slot.pile) * CARD_OFFSET
        self.left = slot.left

        # add card to the new slot's pile
        slot.pile.append(self)
 
   def start_drag(self, e: ft.DragStartEvent):
       self.move_on_top()
       self.update()
 
   def drag(self, e: ft.DragUpdateEvent):
       self.top = max(0, self.top + e.delta_y)
       self.left = max(0, self.left + e.delta_x)
       self.update()
 
   def drop(self, e: ft.DragEndEvent):
       for slot in self.solitaire.slots:
           if (
               abs(self.top - slot.top) < DROP_PROXIMITY
           and abs(self.left - slot.left) < DROP_PROXIMITY
         ):
               self.place(slot)
               self.update()
               return
         
       self.bounce_back()
       self.update()


SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

 
class Solitaire(ft.Stack):
   def __init__(self):
       super().__init__()
       self.controls = []
       self.slots = []
       self.cards = []
       self.width = SOLITAIRE_WIDTH
       self.height = SOLITAIRE_HEIGHT
 
   def did_mount(self):
       self.create_card_deck()
       self.create_slots()
       self.deal_cards()
 
   def create_card_deck(self):
       card1 = Card(self, color="GREEN")
       card2 = Card(self, color="YELLOW")
       self.cards = [card1, card2]
 
   def create_slots(self):
       self.slots.append(Slot(top=0, left=0))
       self.slots.append(Slot(top=0, left=200))
       self.slots.append(Slot(top=0, left=300))
       self.controls.extend(self.slots)
       self.update()
 
   def deal_cards(self):
       self.controls.extend(self.cards)
       for card in self.cards:
           card.place(self.slots[0])
       self.update()


def main(page: ft.Page):
  
   solitaire = Solitaire()
 
   page.add(solitaire)
 
ft.app(main)   