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
from app.screens.gomme_screen import GommeScreen
from app.screens.revisione_screen import RevisioneScreen
from app.screens.onboarding_welcome import OnboardingWelcomeScreen
from app.screens.onboarding_create_auto import OnboardingCreateAutoScreen
from app.screens.onboarding_tacho import OnboardingTachimetroScreen
from kivy.lang import Builder

Builder.load_file("onboarding_welcome.kv")
Builder.load_file("onboarding_create_auto.kv")
Builder.load_file("onboarding_tachimetro.kv")



class SimpleCarApp(MDApp):
    def build(self):
        self.title = "EasyCar"
        self.icon = "app/assets/ea_icon.png"
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddAutoScreen(name="add_auto"))
        sm.add_widget(MyCarsScreen(name="mycars"))
        sm.add_widget(DetailAutoScreen(name="detail_auto"))
        sm.add_widget(GommeScreen(name="gomme"))
        sm.add_widget(RevisioneScreen(name="revisione"))
        sm.add_widget(OnboardingWelcomeScreen(name="onb_welcome"))
        sm.add_widget(OnboardingCreateAutoScreen(name="onb_create_auto"))
        sm.add_widget(OnboardingTachimetroScreen(name="onb_tacho"))
 
        sm.current = "onb_welcome"

        return sm


if __name__ == "__main__":
    SimpleCarApp().run()
