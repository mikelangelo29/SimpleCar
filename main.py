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
from app.screens.onboarding_welcome import OnboardingWelcomeScreen
from app.screens.onboarding_create_auto import OnboardingCreateAutoScreen
from app.screens.onboarding_tacho import OnboardingTachimetroScreen
from kivy.lang import Builder

Builder.load_file("onboarding_welcome.kv")
Builder.load_file("onboarding_create_auto.kv")
Builder.load_file("onboarding_tachimetro.kv")



class SimpleCarApp(MDApp):

    autos_file = "app/data/autos.json"

    def genera_colore_tachimetro(self):
        import random

        colors = ["blue", "red", "green", "yellow", "orange", "purple"]

        autos = self.load_autos() or []

        # Se nessuna auto esiste → random totale (prima auto della Premium)
        if not autos:
            return random.choice(colors)

        # Colore dell’ultima auto
        last_color = autos[-1].get("tacho_color")

        # Escludi il colore precedente
        available = [c for c in colors if c != last_color]

        return random.choice(available)


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
        sm.add_widget(OnboardingWelcomeScreen(name="onb_welcome"))
        sm.add_widget(OnboardingCreateAutoScreen(name="onb_create_auto"))
        sm.add_widget(OnboardingTachimetroScreen(name="onb_tacho"))
        print([s.name for s in sm.screens])


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
        """Legge il file autos.json e restituisce la lista di auto."""
        if not os.path.exists(self.autos_file):
            return []

        try:
            with open(self.autos_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("autos", [])
        except:
            return []

    def save_autos(self, autos_lista):
        """Salva l'elenco delle auto nel JSON."""
        data = {"autos": autos_lista}

        with open(self.autos_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    SimpleCarApp().run()
