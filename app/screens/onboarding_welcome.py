from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty

class OnboardingWelcomeScreen(MDScreen):
    # Percorso reale del logo
    logo_path = StringProperty("app/assets/logo_home.png")
