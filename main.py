import sys
sys.path.append("libs")

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from app.screens.home_screen import HomeScreen


class SimpleCarApp(MDApp):
    title = "EasyAuto"   # ← elimina “SimpleCar” in alto a sinistra

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        return sm


if __name__ == "__main__":
    SimpleCarApp().run()
