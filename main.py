from Folder.view import CardScreen, AddScreen, ListScreen
from Folder.data import Data


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager


# Window.size = (720, 1280)
# Window.size = (380, 653)

class FlashcardApp(App):
    def build(self):
        self.data_manager = Data()

        self.sm = ScreenManager()
        self.sm.add_widget(CardScreen(name='cards'))
        self.sm.add_widget(AddScreen(name='add'))
        self.sm.add_widget(ListScreen(name='list'))
        return self.sm


if __name__ == '__main__':
    FlashcardApp().run()
