from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class SimpleCarApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titolo = Label(text="SimpleCar", font_size=32, bold=True)
        sottotitolo = Label(text="Auto: scadenze Tecniche e Amministrative", font_size=18)

        layout.add_widget(titolo)
        layout.add_widget(sottotitolo)

        return layout


if __name__ == "__main__":
    SimpleCarApp().run()
