import tkinter as tk
from tkinter import messagebox, Button, Label, Frame
import random
import os
from PIL import Image, ImageTk
from typing import List, Tuple, Optional


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
        # Припускаємо, що зображення мають назву формату "rank_of_suit.png"
        # наприклад "ace_of_hearts.png"
        image_path = f"cards/{self.rank}_of_{self.suit}.png"

        # Якщо файл не існує, повертаємо зображення звороту карти
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
        self.aces = 0  # Відстежуємо кількість тузів для зміни їх значення

    def add_card(self, card: Card) -> None:
        """Додати карту в руку і обчислити значення руки."""
        self.cards.append(card)
        self.value += card.value

        # Відстежуємо тузи
        if card.rank == 'ace':
            self.aces += 1

        # Змінюємо значення тузів, якщо загальна сума перевищує 21
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
        self.chips = 1000  # Початкова кількість фішок

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
    def __init__(self, root):
        self.root = root
        self.root.title("БлекДжек")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Ініціалізація змінних гри
        self.deck = Deck()
        self.player = Player("Гравець")
        self.dealer = Player("Дилер")
        self.bet_amount = 0
        self.game_over = False

        # Розміри карт
        self.card_width = 80
        self.card_height = 120

        # Створення інтерфейсу
        self.setup_ui()

        # Завантаження зображень карт
        self.load_card_images()

        # Початок гри
        self.new_game()

    def setup_ui(self):
        """Налаштування інтерфейсу користувача."""
        # Основні фрейми
        self.info_frame = Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X)

        self.dealer_frame = Frame(self.root, bg="#34495e", padx=10, pady=10)
        self.dealer_frame.pack(fill=tk.BOTH, expand=True)

        self.player_frame = Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        self.player_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)

        # Інформаційні мітки
        self.chips_label = Label(self.info_frame, text=f"Фішки: {self.player.chips}",
                                 bg="#2c3e50", fg="white", font=("Arial", 14))
        self.chips_label.pack(side=tk.LEFT, padx=5)

        self.bet_label = Label(self.info_frame, text=f"Ставка: {self.bet_amount}",
                               bg="#2c3e50", fg="white", font=("Arial", 14))
        self.bet_label.pack(side=tk.LEFT, padx=5)

        self.result_label = Label(self.info_frame, text="",
                                  bg="#2c3e50", fg="white", font=("Arial", 14))
        self.result_label.pack(side=tk.RIGHT, padx=5)

        # Мітки для карт дилера і гравця
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

        # Кнопки управління
        self.hit_button = Button(self.control_frame, text="Взяти карту",
                                 command=self.hit, font=("Arial", 12), bg="#3498db", fg="white")
        self.hit_button.pack(side=tk.LEFT, padx=5)

        self.stand_button = Button(self.control_frame, text="Достатньо",
                                   command=self.stand, font=("Arial", 12), bg="#2ecc71", fg="white")
        self.stand_button.pack(side=tk.LEFT, padx=5)

        self.new_game_button = Button(self.control_frame, text="Нова гра",
                                      command=self.new_game, font=("Arial", 12), bg="#e74c3c", fg="white")
        self.new_game_button.pack(side=tk.RIGHT, padx=5)

        # Фрейм для ставок
        self.bet_frame = Frame(self.control_frame, bg="#2c3e50")
        self.bet_frame.pack(side=tk.RIGHT, padx=20)

        self.bet_buttons = []
        for bet in [10, 25, 50, 100]:
            bet_btn = Button(self.bet_frame, text=f"{bet}",
                             command=lambda b=bet: self.place_bet(b),
                             font=("Arial", 12), bg="#f39c12", fg="white", width=3)
            bet_btn.pack(side=tk.LEFT, padx=2)
            self.bet_buttons.append(bet_btn)

    def load_card_images(self):
        """Завантаження зображень карт."""
        # В реальному проекті тут ви б завантажували зображення карт
        # Для спрощення будемо вважати, що вони вже існують в папці cards/
        # Також можна створити папку cards/ і скачати набір зображень карт
        # або використати Canvas для малювання карт

        # Перевірка і створення папки для карт, якщо вона не існує
        if not os.path.exists('cards'):
            os.makedirs('cards')
            messagebox.showinfo("Інформація",
                                "Будь ласка, додайте зображення карт у папку 'cards'.\n"
                                "Назви файлів мають бути у форматі: 'rank_of_suit.png'\n"
                                "Наприклад: 'ace_of_hearts.png'")

    def place_bet(self, amount: int) -> None:
        """Зробити ставку."""
        if not self.game_over:
            return

        if amount <= self.player.chips:
            self.bet_amount = amount
            self.bet_label.config(text=f"Ставка: {self.bet_amount}")
            self.deal_cards()
            self.game_over = False

            # Увімкнути/вимкнути відповідні кнопки
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
        # Скидання колоди
        self.deck.reset()

        # Очищення рук
        self.player.hand.clear()
        self.dealer.hand.clear()

        # Скидання ставки
        self.bet_amount = 0
        self.bet_label.config(text=f"Ставка: {self.bet_amount}")

        # Оновлення інтерфейсу
        self.clear_cards()
        self.result_label.config(text="")
        self.player_value.config(text="")
        self.dealer_value.config(text="")

        # Увімкнути кнопки ставок і вимкнути ігрові кнопки
        self.toggle_bet_buttons(True)
        self.toggle_game_buttons(False)

        # Оновлення кількості фішок
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
        # Обробка ставки
        try:
            self.player.bet(self.bet_amount)
            self.chips_label.config(text=f"Фішки: {self.player.chips}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return

        # Роздача карт (2 гравцю, 2 дилеру)
        for _ in range(2):
            # Роздаємо карту гравцю
            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.player.hand.add_card(card)
                self.display_card(card, self.player_cards_frame)

            # Роздаємо карту дилеру
            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.dealer.hand.add_card(card)

                # Для першої карти дилера показуємо зворот
                if _ == 0:
                    self.dealer_hidden_card = card
                    back_image = self.get_card_back_image()
                    label = Label(self.dealer_cards_frame, image=back_image)
                    label.image = back_image
                    label.pack(side=tk.LEFT, padx=2)
                else:
                    self.display_card(card, self.dealer_cards_frame)

        # Відображення значення руки гравця
        self.player_value.config(text=f"Сума: {self.player.hand.value}")

        # Перевірка на Blackjack
        if self.player.hand.value == 21:
            self.stand()  # Автоматично закінчуємо хід при Blackjack

    def display_card(self, card: Card, frame: Frame) -> None:
        """Відобразити карту на екрані."""
        try:
            photo = card.get_image(self.card_width, self.card_height)
            label = Label(frame, image=photo)
            label.image = photo  # Зберігаємо посилання на зображення
            label.pack(side=tk.LEFT, padx=2)
        except Exception as e:
            # Якщо помилка при завантаженні зображення, відображаємо текст
            label = Label(frame, text=f"{card.rank} of {card.suit}",
                          bg="white", width=8, height=5)
            label.pack(side=tk.LEFT, padx=2)

    def get_card_back_image(self) -> ImageTk.PhotoImage:
        """Отримати зображення звороту карти."""
        try:
            image_path = "cards/back.png"
            if not os.path.exists(image_path):
                # Якщо зображення звороту немає, використовуємо заглушку
                image = Image.new('RGB', (self.card_width, self.card_height), color='blue')
            else:
                image = Image.open(image_path)

            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception:
            # Якщо помилка, повертаємо None
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

        # Показати приховану карту дилера
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

        self.display_card(self.dealer_hidden_card, self.dealer_cards_frame)
        for card in self.dealer.hand.cards[1:]:
            self.display_card(card, self.dealer_cards_frame)

        self.dealer_value.config(text=f"Сума: {self.dealer.hand.value}")

        # Дилер бере карти, поки не набере хоча б 17
        while self.dealer.hand.value < 17:
            card_data = self.deck.deal_card()
            if card_data:
                card = Card(card_data[0], card_data[1])
                self.dealer.hand.add_card(card)
                self.display_card(card, self.dealer_cards_frame)
                self.dealer_value.config(text=f"Сума: {self.dealer.hand.value}")

        # Визначення переможця
        self.determine_winner()

    def determine_winner(self) -> None:
        """Визначення переможця гри."""
        player_value = self.player.hand.value
        dealer_value = self.dealer.hand.value

        # Перебір у дилера - гравець виграє
        if dealer_value > 21:
            self.player.win_bet(self.bet_amount)
            self.end_game("Дилер перебрав! Ви виграли!")
        # Перебір у гравця - дилер виграє
        elif player_value > 21:
            self.end_game("Перебір! Ви програли.")
        # Блекджек у гравця (21 з 2 карт)
        elif player_value == 21 and len(self.player.hand.cards) == 2:
            # Виплата 3:2 для блекджека
            self.player.chips += self.bet_amount * 2.5
            self.end_game("Блекджек! Ви виграли!")
        # Гравець має більше очок
        elif player_value > dealer_value:
            self.player.win_bet(self.bet_amount)
            self.end_game("Ви виграли!")
        # Дилер має більше очок
        elif dealer_value > player_value:
            self.end_game("Ви програли.")
        # Нічия
        else:
            self.player.push(self.bet_amount)
            self.end_game("Нічия!")

    def end_game(self, result_message: str) -> None:
        """Завершення гри і відображення результату."""
        self.result_label.config(text=result_message)
        self.toggle_game_buttons(False)
        self.chips_label.config(text=f"Фішки: {self.player.chips}")
        self.game_over = True

        # Перевірка на банкрутство
        if self.player.chips <= 0:
            messagebox.showinfo("Кінець гри", "У вас закінчились фішки. Гра завершена.")
            self.player.chips = 1000  # Починаємо нову гру з початковою кількістю фішок


# Функція для запуску гри
def main():
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()