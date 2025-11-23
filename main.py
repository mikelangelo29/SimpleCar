# ------------------------------------------------
# 📱 Emulatore MOBILE-First per vedere l'app come su Android
# ------------------------------------------------
from kivy.config import Config
Config.set('graphics', 'width', '390')    # larghezza smartphone
Config.set('graphics', 'height', '844')   # altezza smartphone
Config.set('graphics', 'resizable', False)
# ------------------------------------------------

from kivymd.uix.button.button import MDRaisedButton
# 🔥 FIX FONDAMENTALE DEL BUG DI KIVYMD SU WINDOWS
MDRaisedButton.rounded_button = False
# ------------------------------------------------

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from app.screens.mycars_screen import MyCarsScreen
from app.screens.add_auto_screen import AddAutoScreen
from app.screens.home_screen import HomeScreen
from app.screens.detail_auto_screen import DetailAutoScreen



class SimpleCarApp(MDApp):
    def build(self):
        self.title = "EasyAuto"
        self.icon = "app/assets/ea_icon.png"
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddAutoScreen(name="add_auto"))
        sm.add_widget(MyCarsScreen(name="mycars"))
        sm.add_widget(DetailAutoScreen(name="detail_auto"))

        return sm


if __name__ == "__main__":
    SimpleCarApp().run()
