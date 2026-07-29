import os
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.uix.boxlayout import BoxLayout

Window.size = (400, 700)

from database import init_db
from screens.catalog_screen import CatalogScreen
from screens.comanda_screen import ComandaScreen, ComandaDetailScreen


class HomeScreen(Screen):
    pass


class VendasComandasApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"

        init_db()

        Builder.load_file(
            os.path.join(os.path.dirname(__file__), "kv", "catalog_screen.kv")
        )
        Builder.load_file(
            os.path.join(os.path.dirname(__file__), "kv", "comanda_screen.kv")
        )
        Builder.load_file(
            os.path.join(os.path.dirname(__file__), "kv", "comanda_detail_screen.kv")
        )
        Builder.load_file(
            os.path.join(os.path.dirname(__file__), "kv", "home_screen.kv")
        )

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ComandaDetailScreen(name="comanda_detail"))

        return sm

    def get_screen(self, name):
        return self.root.get_screen(name)

    def back_to_comandas(self):
        self.root.current = "home"
        home = self.root.get_screen("home")
        nav = home.ids.nav
        nav.switch_tab("comandas_tab")


if __name__ == "__main__":
    VendasComandasApp().run()
