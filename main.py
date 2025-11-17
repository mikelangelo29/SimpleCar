from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

# Import delle schermate (vuote per ora)
from app.screens.home_screen import HomeScreen
from app.screens.add_auto_screen import AddAutoScreen
from app.screens.tecniche_screen import TecnicheScreen
from app.screens.administrative_screen import AdministrativeScreen
from app.screens.multe_screen import MulteScreen


class SimpleCarManager(ScreenManager):
    pass


class SimpleCarApp(App):
    def build(self):
        sm = SimpleCarManager()

        # Registriamo le schermate (vuote per ora)
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddAutoScreen(name="add_auto"))
        sm.add_widget(TecnicheScreen(name="tecniche"))
        sm.add_widget(AdministrativeScreen(name="amministrative"))
        sm.add_widget(MulteScreen(name="multe"))

        return sm


if __name__ == "__main__":
    SimpleCarApp().run()
