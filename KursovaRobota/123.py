import tkinter as tk
from tkinter import messagebox, Button, Label, Frame, ttk, Canvas
import random
import os
import math
from PIL import Image, ImageTk
from typing import List, Tuple, Optional, Dict, Union, Callable
from abc import ABC, abstractmethod


# Шаблон проєктування Singleton для колоди карт
class Deck:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Deck, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        self.values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                       'jack': 10, 'queen': 10, 'king': 10, 'ace': 11}
        self.cards = []
        self.reset()

    def reset(self):
        """Метод для скидання колоди і створення нових карт."""
        self.cards = [(rank, suit) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.cards)

    def deal_card(self) -> Optional[Tuple[str, str]]:
        """Роздати одну карту з колоди."""
        if not self.cards:
            return None
        return self.cards.pop()

    def get_card_value(self, card: Tuple[str, str]) -> int:
        """Отримати числове значення карти."""
        rank, _ = card
        return self.values[rank]


class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        self.value = Deck().get_card_value((rank, suit))
        self.image = None

    def get_image(self, card_width: int, card_height: int) -> ImageTk.PhotoImage:
        """Завантажити зображення карти."""
        image_path = f"cards/{self.rank}_of_{self.suit}.png"


        if not os.path.exists(image_path):
            image_path = "cards/back.png"

        image = Image.open(image_path)
        image = image.resize((card_width, card_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image = photo
        return photo


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.value = 0
        self.aces = 0

    def add_card(self, card: Card) -> None:
        """Додати карту в руку і обчислити значення руки."""
        self.cards.append(card)
        self.value += card.value


        if card.rank == 'ace':
            self.aces += 1


        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def clear(self) -> None:
        """Очистити руку."""
        self.cards = []
        self.value = 0
        self.aces = 0


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
        self.chips = 1000

    def bet(self, amount: int) -> None:
        """Зробити ставку."""
        if amount <= self.chips:
            self.chips -= amount
        else:
            raise ValueError("Недостатньо фішок")

    def win_bet(self, amount: int) -> None:
        """Виграти ставку."""
        self.chips += amount * 2

    def push(self, amount: int) -> None:
        """Нічия (поверненя ставки)."""
        self.chips += amount


class BlackjackGame:
    def __init__(self, parent_frame, player):
        self.parent_frame = parent_frame
        self.player = player


        self.deck = Deck()
        self.dealer = Player("Дилер")
        self.bet_amount = 0
        self.game_over = True


        self.card_width = 80
        self.card_height = 120


        self.setup_ui()


        self.load_card_images()

    def setup_ui(self):
        """Налаштування інтерфейсу користувача."""

        self.info_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X)

        self.dealer_frame = Frame(self.parent_frame, bg="#34495e", padx=10, pady=10)
        self.dealer_frame.pack(fill=tk.BOTH, expand=True)

        self.player_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.player_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)


        self.chips_label = Label(self.info_frame, text=f"Фішки: {self.player.chips}",
                                 bg="#2c3e50", fg="white", font=("Arial", 14))
        self.chips_label.pack(side=tk.LEFT, padx=5)

        self.bet_label = Label(self.info_frame, text=f"Ставка: {self.bet_amount}",
                               bg="#2c3e50", fg="white", font=("Arial", 14))
        self.bet_label.pack(side=tk.LEFT, padx=5)

        self.result_label = Label(self.info_frame, text="",
                                  bg="#2c3e50", fg="white", font=("Arial", 14))
        self.result_label.pack(side=tk.RIGHT, padx=5)


        self.dealer_title = Label(self.dealer_frame, text="Дилер",
                                  bg="#34495e", fg="white", font=("Arial", 14))
        self.dealer_title.pack(anchor=tk.W)

        self.dealer_cards_frame = Frame(self.dealer_frame, bg="#34495e")
        self.dealer_cards_frame.pack(pady=10)

        self.dealer_value = Label(self.dealer_frame, text="",
                                  bg="#34495e", fg="white", font=("Arial", 12))
        self.dealer_value.pack(anchor=tk.W)

        self.player_title = Label(self.player_frame, text="Гравець",
                                  bg="#2c3e50", fg="white", font=("Arial", 14))
        self.player_title.pack(anchor=tk.W)

        self.player_cards_frame = Frame(self.player_frame, bg="#2c3e50")
        self.player_cards_frame.pack(pady=10)

        self.player_value = Label(self.player_frame, text="",
                                  bg="#2c3e50", fg="white", font=("Arial", 12))
        self.player_value.pack(anchor=tk.W)


        self.hit_button = Button(self.control_frame, text="Взяти карту",
                                 command=self.hit, font=("Arial", 12), bg="#3498db", fg="white")
        self.hit_button.pack(side=tk.LEFT, padx=5)

        self.stand_button = Button(self.control_frame, text="Достатньо",
                                   command=self.stand, font=("Arial", 12), bg="#2ecc71", fg="white")
        self.stand_button.pack(side=tk.LEFT, padx=5)

        self.new_game_button = Button(self.control_frame, text="Нова гра",
                                      command=self.new_game, font=("Arial", 12), bg="#e74c3c", fg="white")
        self.new_game_button.pack(side=tk.RIGHT, padx=5)


        self.bet_frame = Frame(self.control_frame, bg="#2c3e50")
        self.bet_frame.pack(side=tk.RIGHT, padx=20)

        self.bet_buttons = []
        for bet in [10, 25, 50, 100]:
            bet_btn = Button(self.bet_frame, text=f"{bet}",
                             command=lambda b=bet: self.place_bet(b),
                             font=("Arial", 12), bg="#f39c12", fg="white", width=3)
            bet_btn.pack(side=tk.LEFT, padx=2)
            self.bet_buttons.append(bet_btn)


        self.toggle_game_buttons(False)
        self.toggle_bet_buttons(True)

    def load_card_images(self):
        """Завантаження зображень карт."""

        if not os.path.exists('cards'):
            os.makedirs('cards')
            messagebox.showinfo("Інформація",
                                "Будь ласка, додайте зображення карт у папку 'cards'.\n"
                                "Назви файлів мають бути у форматі: 'rank_of_suit.png'\n"
                                "Наприклад: 'ace_of_hearts.png'")

    def update_chips_display(self):
        """Оновити відображення фішок."""
        self.chips_label.config(text=f"Фішки: {self.player.chips}")

    def place_bet(self, amount: int) -> None:
        """Зробити ставку."""
        if not self.game_over:
            return

        if amount <= self.player.chips:
            self.bet_amount = amount
            self.bet_label.config(text=f"Ставка: {self.bet_amount}")
            self.deal_cards()
            self.game_over = False


            self.toggle_bet_buttons(False)
            self.toggle_game_buttons(True)
        else:
            messagebox.showerror("Помилка", "Недостатньо фішок!")

    def toggle_bet_buttons(self, state: bool) -> None:
        """Увімкнути/вимкнути кнопки ставок."""
        for btn in self.bet_buttons:
            btn.config(state=tk.NORMAL if state else tk.DISABLED)

    def toggle_game_buttons(self, state: bool) -> None:
        """Увімкнути/вимкнути ігрові кнопки."""
        self.hit_button.config(state=tk.NORMAL if state else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if state else tk.DISABLED)

    def new_game(self) -> None:
        """Почати нову гру."""

        self.deck.reset()


        self.player.hand.clear()
        self.dealer.hand.clear()


        self.bet_amount = 0
        self.bet_label.config(text=f"Ставка: {self.bet_amount}")


        self.clear_cards()
        self.result_label.config(text="")
        self.player_value.config(text="")
        self.dealer_value.config(text="")


        self.toggle_bet_buttons(True)
        self.toggle_game_buttons(False)


        self.chips_label.config(text=f"Фішки: {self.player.chips}")

        self.game_over = True

    def clear_cards(self) -> None:
        """Очистити відображення карт."""
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()

        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

    def deal_cards(self) -> None:
        """Роздати початкові карти."""

        try:
            self.player.bet(self.bet_amount)
            self.chips_label.config(text=f"Фішки: {self.player.chips}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return


        for _ in range(2):

            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.player.hand.add_card(card)
                self.display_card(card, self.player_cards_frame)


            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.dealer.hand.add_card(card)


                if _ == 0:
                    self.dealer_hidden_card = card
                    back_image = self.get_card_back_image()
                    label = Label(self.dealer_cards_frame, image=back_image)
                    label.image = back_image
                    label.pack(side=tk.LEFT, padx=2)
                else:
                    self.display_card(card, self.dealer_cards_frame)


        self.player_value.config(text=f"Сума: {self.player.hand.value}")

        # Перевірка на Blackjack
        if self.player.hand.value == 21:
            self.stand()

    def display_card(self, card: Card, frame: Frame) -> None:
        """Відобразити карту на екрані."""
        try:
            photo = card.get_image(self.card_width, self.card_height)
            label = Label(frame, image=photo)
            label.image = photo
            label.pack(side=tk.LEFT, padx=2)
        except Exception as e:

            label = Label(frame, text=f"{card.rank} of {card.suit}",
                          bg="white", width=8, height=5)
            label.pack(side=tk.LEFT, padx=2)

    def get_card_back_image(self) -> ImageTk.PhotoImage:
        """Отримати зображення звороту карти."""
        try:
            image_path = "cards/back.png"
            if not os.path.exists(image_path):

                image = Image.new('RGB', (self.card_width, self.card_height), color='blue')
            else:
                image = Image.open(image_path)

            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception:

            return None

    def hit(self) -> None:
        """Взяти ще карту."""
        if self.game_over:
            return

        card_data = self.deck.deal_card()
        if card_data:
            card = Card(card_data[0], card_data[1])
            self.player.hand.add_card(card)
            self.display_card(card, self.player_cards_frame)
            self.player_value.config(text=f"Сума: {self.player.hand.value}")

            # Перевірка на перебір
            if self.player.hand.value > 21:
                self.end_game("Перебір! Ви програли.")

    def stand(self) -> None:
        """Зупинитись і передати хід дилеру."""
        if self.game_over:
            return


        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

        self.display_card(self.dealer_hidden_card, self.dealer_cards_frame)
        for card in self.dealer.hand.cards[1:]:
            self.display_card(card, self.dealer_cards_frame)

        self.dealer_value.config(text=f"Сума: {self.dealer.hand.value}")


        while self.dealer.hand.value < 17:
            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.dealer.hand.add_card(card)
                self.display_card(card, self.dealer_cards_frame)
                self.dealer_value.config(text=f"Сума: {self.dealer.hand.value}")


        self.determine_winner()

    def determine_winner(self) -> None:
        """Визначення переможця гри."""
        player_value = self.player.hand.value
        dealer_value = self.dealer.hand.value


        if dealer_value > 21:
            self.player.win_bet(self.bet_amount)
            self.end_game("Дилер перебрав! Ви виграли!")

        elif player_value > 21:
            self.end_game("Перебір! Ви програли.")

        elif player_value == 21 and len(self.player.hand.cards) == 2:

            self.player.chips += int(self.bet_amount * 2.5)
            self.end_game("Блекджек! Ви виграли!")

        elif player_value > dealer_value:
            self.player.win_bet(self.bet_amount)
            self.end_game("Ви виграли!")

        elif dealer_value > player_value:
            self.end_game("Ви програли.")

        else:
            self.player.push(self.bet_amount)
            self.end_game("Нічия!")

    def end_game(self, result_message: str) -> None:
        """Завершення гри і відображення результату."""
        self.result_label.config(text=result_message)
        self.toggle_game_buttons(False)
        self.chips_label.config(text=f"Фішки: {self.player.chips}")
        self.game_over = True


        if self.player.chips <= 0:
            messagebox.showinfo("Кінець гри", "У вас закінчились фішки. Гра завершена.")
            self.player.chips = 1000  # Починаємо нову гру з початковою кількістю фішок


class RouletteState(ABC):
    @abstractmethod
    def place_bet(self, game, bet_type: str):
        pass

    @abstractmethod
    def spin_wheel(self, game):
        pass

    @abstractmethod
    def clear_bets(self, game):
        pass


class IdleState(RouletteState):
    def place_bet(self, game, bet_type: str):
        if game.bet_amount == 0:
            messagebox.showerror("Помилка", "Виберіть суму ставки!")
            return
        if game.bet_amount <= game.player.chips:
            game.player.bet(game.bet_amount)
            game.active_bets[bet_type] = game.active_bets.get(bet_type, 0) + game.bet_amount
            game.update_chips_display()
            game.result_label.config(text=f"Ставка на {bet_type} прийнята")
        else:
            messagebox.showerror("Помилка", "Недостатньо фішок!")

    def spin_wheel(self, game):
        if not game.active_bets:
            messagebox.showerror("Помилка", "Зробіть хоча б одну ставку!")
            return
        game.set_state(SpinningState())
        game.spin_speed = random.uniform(0.1, 0.2)
        game.ball_speed = random.uniform(0.15, 0.25)
        game.spinning_time = 0
        game.result_label.config(text="Колесо крутиться...")
        game.animate_wheel()

    def clear_bets(self, game):
        for bet_amount in game.active_bets.values():
            game.player.chips += bet_amount
        game.active_bets.clear()
        game.bet_amount = 0
        game.bet_label.config(text=f"Ставка: {game.bet_amount}")
        game.update_chips_display()
        game.result_label.config(text="Ставки очищено")


class SpinningState(RouletteState):
    def place_bet(self, game, bet_type: str):
        messagebox.showinfo("Зачекайте", "Колесо крутиться, зачекайте результату!")

    def spin_wheel(self, game):
        messagebox.showinfo("Зачекайте", "Колесо вже крутиться!")

    def clear_bets(self, game):
        messagebox.showinfo("Зачекайте", "Не можна очистити ставки під час обертання!")


class ResultState(RouletteState):
    def place_bet(self, game, bet_type: str):
        game.set_state(IdleState())
        game.place_bet(bet_type)

    def spin_wheel(self, game):
        game.set_state(IdleState())
        game.spin_wheel()

    def clear_bets(self, game):
        game.set_state(IdleState())
        game.clear_bets()


class RouletteGame:
    def __init__(self, parent_frame, player):
        self.parent_frame = parent_frame
        self.player = player
        self.bet_amount = 0
        self.active_bets = {}
        self.wheel_radius = 150
        self.center_x = 250
        self.center_y = 200
        self.ball_radius = 8
        self.angle = 0
        self.ball_angle = 0
        self.ball_distance = self.wheel_radius - 20
        self.spin_speed = 0
        self.ball_speed = 0
        self.spinning_time = 0
        self.winner_number = None
        self.numbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
            5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        self.number_colors = {
            0: "green",
            1: "red", 2: "black", 3: "red", 4: "black", 5: "red", 6: "black",
            7: "red", 8: "black", 9: "red", 10: "black", 11: "black", 12: "red",
            13: "black", 14: "red", 15: "black", 16: "red", 17: "black", 18: "red",
            19: "red", 20: "black", 21: "red", 22: "black", 23: "red", 24: "black",
            25: "red", 26: "black", 27: "red", 28: "black", 29: "black", 30: "red",
            31: "black", 32: "red", 33: "black", 34: "red", 35: "black", 36: "red"
        }
        self.state = IdleState()  # Початковий стан
        self.setup_ui()

    def set_state(self, state: RouletteState):
        self.state = state

    def setup_ui(self):
        self.info_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X)
        self.wheel_frame = Frame(self.parent_frame, bg="#34495e", padx=10, pady=10)
        self.wheel_frame.pack(fill=tk.BOTH, expand=True)
        self.bet_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.bet_frame.pack(fill=tk.X)
        self.control_frame = Frame(self.parent_frame, bg="#2c3e50", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)
        self.chips_label = Label(self.info_frame, text=f"Фішки: {self.player.chips}", bg="#2c3e50", fg="white",
                                 font=("Arial", 14))
        self.chips_label.pack(side=tk.LEFT, padx=5)
        self.bet_label = Label(self.info_frame, text=f"Ставка: {self.bet_amount}", bg="#2c3e50", fg="white",
                               font=("Arial", 14))
        self.bet_label.pack(side=tk.LEFT, padx=5)
        self.result_label = Label(self.info_frame, text="", bg="#2c3e50", fg="white", font=("Arial", 14))
        self.result_label.pack(side=tk.RIGHT, padx=5)
        self.wheel_canvas = Canvas(self.wheel_frame, width=500, height=400, bg="#34495e", highlightthickness=0)
        self.wheel_canvas.pack(pady=10)
        self.draw_wheel()

        bet_types = [("red", "Червоне", "#e74c3c"), ("black", "Чорне", "#2c3e50"), ("green", "Зеро", "#2ecc71"),
                     ("even", "Парне", "#3498db"), ("odd", "Непарне", "#9b59b6"), ("1-18", "1-18", "#f39c12"),
                     ("19-36", "19-36", "#e67e22")]
        for bet_type, text, color in bet_types:
            bet_button = Button(self.bet_frame, text=text, bg=color, fg="white",
                                command=lambda b=bet_type: self.place_bet(b), font=("Arial", 12), width=8)
            bet_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.spin_button = Button(self.control_frame, text="Запустити колесо", command=self.spin_wheel,
                                  font=("Arial", 12), bg="#3498db", fg="white", width=15)
        self.spin_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_bets_button = Button(self.control_frame, text="Очистити ставки", command=self.clear_bets,
                                        font=("Arial", 12), bg="#e74c3c", fg="white", width=15)
        self.clear_bets_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.bet_amount_frame = Frame(self.control_frame, bg="#2c3e50")
        self.bet_amount_frame.pack(side=tk.RIGHT, padx=20)
        self.bet_amount_buttons = []
        for amount in [10, 25, 50, 100]:
            bet_amount_btn = Button(self.bet_amount_frame, text=f"{amount}",
                                    command=lambda a=amount: self.set_bet_amount(a), font=("Arial", 12), bg="#f39c12",
                                    fg="white", width=3)
            bet_amount_btn.pack(side=tk.LEFT, padx=2)
            self.bet_amount_buttons.append(bet_amount_btn)
        self.direct_bet_frame = Frame(self.control_frame, bg="#2c3e50")
        self.direct_bet_frame.pack(side=tk.RIGHT, padx=20)
        Label(self.direct_bet_frame, text="Число:", bg="#2c3e50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT,
                                                                                                       padx=5)
        self.number_var = tk.StringVar()
        self.number_entry = ttk.Combobox(self.direct_bet_frame, textvariable=self.number_var, width=5,
                                         font=("Arial", 12), state="readonly")
        self.number_entry['values'] = tuple(str(i) for i in range(37))
        self.number_entry.current(0)
        self.number_entry.pack(side=tk.LEFT, padx=5)
        self.direct_bet_button = Button(self.direct_bet_frame, text="Ставка на число", command=self.place_direct_bet,
                                        font=("Arial", 12), bg="#9b59b6", fg="white")
        self.direct_bet_button.pack(side=tk.LEFT, padx=5)

    def set_bet_amount(self, amount):
        if amount <= self.player.chips:
            self.bet_amount = amount
            self.bet_label.config(text=f"Ставка: {self.bet_amount}")
        else:
            messagebox.showerror("Помилка", "Недостатньо фішок!")

    def update_chips_display(self):
        self.chips_label.config(text=f"Фішки: {self.player.chips}")

    def place_bet(self, bet_type: str):
        self.state.place_bet(self, bet_type)

    def place_direct_bet(self):
        number = int(self.number_var.get())
        bet_key = f"number_{number}"
        self.state.place_bet(self, bet_key)

    def spin_wheel(self):
        self.state.spin_wheel(self)

    def clear_bets(self):
        self.state.clear_bets(self)

    def draw_wheel(self):
        self.wheel_canvas.delete("all")
        self.wheel_canvas.create_oval(self.center_x - self.wheel_radius, self.center_y - self.wheel_radius,
                                      self.center_x + self.wheel_radius, self.center_y + self.wheel_radius,
                                      fill="#333333")
        num_sectors = len(self.numbers)
        angle_step = 360 / num_sectors
        for i, num in enumerate(self.numbers):
            start_angle = i * angle_step + self.angle
            color = self.number_colors[num]
            self.wheel_canvas.create_arc(self.center_x - self.wheel_radius, self.center_y - self.wheel_radius,
                                         self.center_x + self.wheel_radius, self.center_y + self.wheel_radius,
                                         start=start_angle, extent=angle_step, fill=color, outline="#ffffff")
            text_angle = math.radians(start_angle + angle_step / 2)
            text_x = self.center_x + (self.wheel_radius - 30) * math.cos(text_angle)
            text_y = self.center_y - (self.wheel_radius - 30) * math.sin(text_angle)
            self.wheel_canvas.create_text(text_x, text_y, text=str(num), fill="white" if color != "green" else "black",
                                          font=("Arial", 8, "bold"))

        if isinstance(self.state, SpinningState) or isinstance(self.state, ResultState):
            ball_x = self.center_x + self.ball_distance * math.cos(self.ball_angle)
            ball_y = self.center_y - self.ball_distance * math.sin(self.ball_angle)
            self.wheel_canvas.create_oval(ball_x - self.ball_radius, ball_y - self.ball_radius,
                                          ball_x + self.ball_radius, ball_y + self.ball_radius, fill="white")

    def animate_wheel(self):
        self.spinning_time += 1
        self.angle += self.spin_speed
        self.ball_angle += self.ball_speed
        self.spin_speed *= 0.99
        self.ball_speed *= 0.98

        self.draw_wheel()
        if self.spinning_time < 100 or self.spin_speed > 0.01:
            self.wheel_canvas.after(20, self.animate_wheel)
        else:
            self.stop_wheel()

    def stop_wheel(self):
        num_sectors = len(self.numbers)
        sector_angle = 360 / num_sectors
        normalized_angle = math.degrees(self.ball_angle) % 360
        sector = int(normalized_angle // sector_angle)
        self.winner_number = self.numbers[sector]
        winner_color = self.number_colors[self.winner_number]
        self.result_label.config(text=f"Випало: {self.winner_number} ({winner_color})")
        self.calculate_winnings()
        self.set_state(ResultState())

    def calculate_winnings(self):
        total_winnings = 0
        winner_color = self.number_colors[self.winner_number]
        is_even = self.winner_number % 2 == 0 and self.winner_number != 0
        is_low = 1 <= self.winner_number <= 18
        for bet_type, amount in self.active_bets.items():
            if bet_type == "red" and winner_color == "red":
                total_winnings += amount * 2
            elif bet_type == "black" and winner_color == "black":
                total_winnings += amount * 2
            elif bet_type == "green" and winner_color == "green":
                total_winnings += amount * 36
            elif bet_type == "even" and is_even:
                total_winnings += amount * 2
            elif bet_type == "odd" and not is_even and self.winner_number != 0:
                total_winnings += amount * 2
            elif bet_type == "1-18" and is_low:
                total_winnings += amount * 2
            elif bet_type == "19-36" and not is_low and self.winner_number != 0:
                total_winnings += amount * 2
            elif bet_type.startswith("number_"):
                bet_number = int(bet_type.split("_")[1])
                if bet_number == self.winner_number:
                    total_winnings += amount * 36
        if total_winnings > 0:
            self.player.chips += total_winnings
            self.result_label.config(text=f"Ви виграли {total_winnings} фішок!")
        else:
            self.result_label.config(text="Ви програли!")
        self.active_bets.clear()
        self.bet_amount = 0
        self.bet_label.config(text=f"Ставка: {self.bet_amount}")
        self.update_chips_display()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Курсова робота")
    root.geometry("1000x700")

    player = Player("Гравець")

    notebook = ttk.Notebook(root)
    blackjack_frame = Frame(notebook, bg="#2c3e50")
    roulette_frame = Frame(notebook, bg="#2c3e50")

    notebook.add(blackjack_frame, text="Блекджек")
    notebook.add(roulette_frame, text="Рулетка")
    notebook.pack(fill=tk.BOTH, expand=True)

    blackjack_game = BlackjackGame(blackjack_frame, player)
    roulette_game = RouletteGame(roulette_frame, player)

    root.mainloop()