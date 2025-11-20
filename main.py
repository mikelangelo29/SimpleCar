from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from app.screens.add_auto_screen import AddAutoScreen
from app.screens.home_screen import HomeScreen


class SimpleCarApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddAutoScreen(name="add_auto"))
        return sm


if __name__ == "__main__":
    SimpleCarApp().run()
