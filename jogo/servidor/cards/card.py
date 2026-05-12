class Card:
    def __init__(self, name:str):
        """
        Superclass used as a base for the cards
        :param name: Name of the card
        """
        self.name = name
        self.used_turn = 0

    def use_card(self, current_turn:int):
        self.used_turn = current_turn

