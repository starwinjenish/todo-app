from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', False)

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDFadeSlideTransition
from kivy.core.window import Window
from kivy.utils import platform

from database import Database
from task_list_screen import TaskListScreen
from add_task_screen import AddTaskScreen
from stats_screen import StatsScreen

class TodoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"
    
    def build(self):
        if platform == 'android' or platform == 'ios':
            Window.softinput_mode = 'below_target'
        
        sm = MDScreenManager(transition=MDFadeSlideTransition())
        
        sm.add_widget(TaskListScreen(self.db, name="task_list"))
        sm.add_widget(AddTaskScreen(self.db, name="add_task"))
        sm.add_widget(StatsScreen(self.db, name="stats"))
        
        return sm

if __name__ == '__main__':
    TodoApp().run()