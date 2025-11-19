from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from app.screens.home_screen import HomeScreen

class SimpleCarApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        return sm

if __name__ == "__main__":
    SimpleCarApp().run()

