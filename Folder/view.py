import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen


class AddScreen(Screen):
    front_input = ObjectProperty("")
    back_input = ObjectProperty("")

    def save_text_input(self, front_input, back_input):
        app = App.get_running_app()
        app.data_manager.save_text(str(front_input), str(back_input))


class ListScreen(Screen):
    rv = ObjectProperty(None)

    def on_enter(self):
        # Метод срабатывает автоматически, когда мы переходим на этот экран
        self.refresh_table()

    def refresh_table(self):
        app = App.get_running_app()

        # Формируем данные для RecycleView.
        # Каждая строка должна получить front, back и свой индекс в массиве
        self.rv.data = [
            {
                "front": card.get("front"),
                "back": card.get("back"),
                "card_index": key
            }
            for key, card in app.data_manager.current_data.items()
        ]


class Card(BoxLayout):
    front = StringProperty('')
    back = StringProperty('')
    card_text = StringProperty('')
    label_card_text = ObjectProperty(None)
    rect_color = ObjectProperty(None)
    bg_color = ListProperty([0.9, 0.9, 0.9, 1.0])

    def __init__(self, front='front', back='back', stack=None, **kwargs):
        super().__init__(**kwargs)
        self.front = front
        self.back = back
        self.stack = stack
        self.showing_back = False
        self.card_text = front

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.pos = self.pos
        self.size = self.size
        # self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            touch.userdata = {'start_x': touch.x, 'start_y': touch.y}
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.x - touch.userdata['start_x']
            self.x = self.parent.x + dx
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            dx = touch.x - touch.userdata['start_x']
            dy = touch.y - touch.userdata['start_y']

            if abs(dx) > 100:
                if dx > 0:
                    self.swipe_right()
                else:
                    self.swipe_left()
            elif abs(dx) < 20 and abs(dy) < 20:
                self.flip_card()
            else:
                self.return_to_center()
            return True
        return super().on_touch_up(touch)

    def show_back(self):
        if not self.showing_back:
            self.card_text = self.back
            self.ids.label_card_text.text = self.card_text
            self.showing_back = True
            Clock.schedule_once(lambda dt: self.hide_back(), 2)

    def flip_card(self):
        if not self.showing_back:
            self.show_back()
        else:
            self.hide_back()

    def hide_back(self):
        self.card_text = self.front
        self.ids.label_card_text.text = self.card_text
        self.showing_back = False

    def swipe_left(self):

        # Анимация фона на красный
        anim = Animation(bg_color=[1.0, 0.3, 0.3, 1], duration=0.15)
        anim.start(self)
        # Улетаем влево
        move_anim = Animation(x=-Window.width, duration=0.3)
        move_anim.bind(on_complete=lambda *args: self.stack.remove_card(self, 'left'))
        move_anim.start(self)

    def swipe_right(self):
        # Анимация фона на зелёный
        anim = Animation(bg_color=[0.3, 0.8, 0.4, 1], duration=0.15)
        anim.start(self)
        move_anim = Animation(x=Window.width, duration=0.3)
        move_anim.bind(on_complete=lambda *args: self.stack.remove_card(self, 'right'))
        move_anim.start(self)

    def return_to_center(self):
        anim = Animation(x=self.parent.x, duration=0.2)
        anim.start(self)

    # der die das color
    def get_article_color(self, text):
        """Возвращает цвет для немецкого слова в зависимости от артикля"""
        text_lower = text.lower().strip()
        if text_lower.startswith('der '):
            return (0.2, 0.6, 1.0, 1)  # голубой
        elif text_lower.startswith('die '):
            return (1.0, 0.3, 0.3, 1)  # красный
        elif text_lower.startswith('das '):
            return (0.2, 0.8, 0.2, 1)  # зелёный
        else:
            # стандартный цвет (зависит от темы)
            return (0, 0, 0, 1)


class CardScreen(Screen):
    stack = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cards_data = {}
        self.current_cards = []
        self.init_cards()

    def init_cards(self):
        app = App.get_running_app()
        self.cards_data = app.data_manager.current_data
        self.reset_cards()

    def reset_cards(self):
        self.ids.cards_container.clear_widgets()
        self.current_cards = []
        self.shuffled_cards = []
        for key, card_data in self.cards_data.items():
            card = Card(
                front=card_data["front"],
                back=card_data["back"],
                stack=self
            )
            self.current_cards.append(card)
        if self.current_cards:
            random.shuffle(self.current_cards)
            self.show_next_card()

    def show_next_card(self):
        if self.current_cards:
            card = self.current_cards[0]
            self.ids.cards_container.add_widget(card)
            self.update_counter()

    #
    def remove_card(self, card, direction):
        if card in self.current_cards:
            self.current_cards.remove(card)
            self.ids.cards_container.clear_widgets()
            if self.current_cards:
                self.show_next_card()
            else:
                self.show_complete_message()

    def update_counter(self):
        total = len(self.cards_data)
        remaining = len(self.current_cards)
        self.ids.label_counter.text = f"Осталось карточек: {remaining} из {total}"

    def show_complete_message(self):
        complete_label = Label(
            text="🎉 Поздравляю! Все карточки изучены! 🎉\n\nНажмите 'Начать заново'",
            font_size='18sp',
            halign='center',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        complete_label.bind(size=complete_label.setter('text_size'))
        self.ids.cards_container.add_widget(complete_label)

    def on_enter(self, *args):
        self.reset_cards()
        self.update_counter()

    def restart_cards(self):
        self.reset_cards()
        self.update_counter()


class CardRow(BoxLayout):
    front = StringProperty("")
    back = StringProperty("")
    card_index = StringProperty("")

    def cr_edit_row(self, card_index, front, back):
        app = App.get_running_app()
        app.data_manager.edit_card()

    def cr_delete_row(self, card_index):
        app = App.get_running_app()
        app.data_manager.delete_card(card_index)

        list_screen = App.get_running_app().root.get_screen('list')
        list_screen.refresh_table()
