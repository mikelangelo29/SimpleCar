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
import json
import os
from app.screens.mycars_screen import MyCarsScreen
from app.screens.add_auto_screen import AddAutoScreen
from app.screens.home_screen import HomeScreen
from app.screens.detail_auto_screen import DetailAutoScreen
from app.screens.gomme_screen import GommeScreen
from app.screens.revisione_screen import RevisioneScreen
from app.screens.tagliando_screen import TagliandoScreen
from app.screens.dischi_freno_screen import DischiFrenoScreen
from app.screens.pastiglie_freno_screen import PastiglieFrenoScreen
from app.screens.ammortizzatori_screen import AmmortizzatoriScreen
from app.screens.cinghia_screen import CinghiaScreen
from app.screens.batteria_screen import BatteriaScreen
from app.screens.assicurazione_screen import AssicurazioneScreen
from app.screens.bollo_screen import BolloScreen
from app.screens.onboarding_welcome import OnboardingWelcomeScreen
from app.screens.onboarding_create_auto import OnboardingCreateAutoScreen
from app.screens.onboarding_tacho import OnboardingTachimetroScreen
from kivy.lang import Builder
from app.storage.data_store import ensure_live_file, load_autos_list, save_autos_list


Builder.load_file("onboarding_welcome.kv")
Builder.load_file("onboarding_create_auto.kv")
Builder.load_file("onboarding_tachimetro.kv")



class SimpleCarApp(MDApp):

    autos_file = "app/data/autos.json"

    def genera_colore_tachimetro(self, index: int) -> str:
        colors = [
            "purple",
            "blue",
            "green",
            "orange",
            "red",
            "yellow",
        ]
        return colors[index % len(colors)]



    def build(self):
        self.title = "EasyCar"
        self.icon = "app/assets/ea_icon.png"

        sm = MDScreenManager()

        # --- Aggiunta degli screen ---
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddAutoScreen(name="add_auto"))
        sm.add_widget(MyCarsScreen(name="mycars"))
        sm.add_widget(DetailAutoScreen(name="detail_auto"))
        sm.add_widget(GommeScreen(name="gomme"))
        sm.add_widget(RevisioneScreen(name="revisione"))
        sm.add_widget(TagliandoScreen(name="tagliando"))
        sm.add_widget(DischiFrenoScreen(name="dischi_freno"))
        sm.add_widget(PastiglieFrenoScreen(name="pastiglie_freno"))
        sm.add_widget(AmmortizzatoriScreen(name="ammortizzatori"))
        sm.add_widget(CinghiaScreen(name="cinghia"))
        sm.add_widget(BatteriaScreen(name="batteria"))
        sm.add_widget(AssicurazioneScreen(name="assicurazione"))
        sm.add_widget(BolloScreen(name="bollo"))
        sm.add_widget(OnboardingWelcomeScreen(name="onb_welcome"))
        sm.add_widget(OnboardingCreateAutoScreen(name="onb_create_auto"))
        sm.add_widget(OnboardingTachimetroScreen(name="onb_tacho"))
       


        ensure_live_file()

        # --- Carico autos.json ---
        autos = self.load_autos()

        # --- Logica di avvio ---
        if autos:
            # Ci sono auto → salto onboarding e vado a MyCars
            sm.current = "home"
        else:
            # Nessuna auto → avvio onboarding
            sm.current = "onb_welcome"

        return sm

 

    autos_file = "app/data/autos.json"
    
    def load_autos(self):
        """Legge il file DATI VIVO e restituisce la lista di auto."""
        from app.storage.data_store import load_autos_list
        return load_autos_list()


    def save_autos(self, autos_lista):
        """Salva l'elenco delle auto nel file DATI VIVO."""
        from app.storage.data_store import save_autos_list
        save_autos_list(autos_lista)



if __name__ == "__main__":
    SimpleCarApp().run()
