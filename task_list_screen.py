from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.chip import MDChip
from kivy.metrics import dp
from kivy.clock import Clock
from task_card import TaskCard

class TaskListScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.current_filter = "All"
        self.build_ui()
        Clock.schedule_once(self.load_tasks, 0)
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical')
        
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)]
        )
        
        title = MDLabel(
            text="My Tasks",
            font_style="H5",  # Changed from HeadlineSmall
            theme_text_color="Primary",
            bold=True
        )
        header.add_widget(title)
        
        stats_btn = MDIconButton(
            icon="chart-pie",
            on_release=lambda x: setattr(self.manager, 'current', "stats")
        )
        header.add_widget(stats_btn)
        main_layout.add_widget(header)
        
        filter_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), 0],
            spacing=dp(8)
        )
        
        self.filter_chips = {}
        filters = ["All", "Pending", "Completed"]
        for f in filters:
            chip = MDChip(
                text=f,
                active=f == "All"
            )
            chip.bind(on_press=lambda x, filt=f: self.set_filter(filt))
            self.filter_chips[f] = chip
            filter_box.add_widget(chip)
        
        main_layout.add_widget(filter_box)
        
        self.scroll = MDScrollView()
        self.task_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None,
            adaptive_height=True
        )
        self.scroll.add_widget(self.task_container)
        main_layout.add_widget(self.scroll)
        
        self.empty_label = MDLabel(
            text="No tasks yet!\nTap + to add one",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",  # Changed from BodyLarge
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        main_layout.add_widget(self.empty_label)
        
        fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={"right": 0.95, "y": 0.05},
            on_release=lambda x: setattr(self.manager, 'current', "add_task")
        )
        main_layout.add_widget(fab)
        
        self.add_widget(main_layout)
    
    def set_filter(self, filter_type):
        self.current_filter = filter_type
        
        for name, chip in self.filter_chips.items():
            chip.active = (name == filter_type)
        
        self.load_tasks()
    
    def load_tasks(self, *args):
        self.task_container.clear_widgets()
        
        status = None if self.current_filter == "All" else self.current_filter
        tasks = self.db.get_all_tasks(status)
        
        if tasks:
            self.empty_label.opacity = 0
            for task in tasks:
                card = TaskCard(
                    task_id=task['id'],
                    title=task['title'],
                    description=task['description'] or "",
                    category=task['category'],
                    due_date=task['due_date'] or "",
                    priority=task['priority'],
                    status=task['status'],
                    on_complete=self.on_task_complete,
                    on_delete=self.on_task_delete,
                    on_edit=self.on_task_edit
                )
                self.task_container.add_widget(card)
        else:
            self.empty_label.opacity = 1
    
    def on_task_complete(self, task_id, status):
        if status == "Completed":
            self.db.complete_task(task_id)
        else:
            self.db.update_task(task_id, status="Pending", completed_at=None)
        self.load_tasks()
    
    def on_task_delete(self, task_id):
        self.db.delete_task(task_id)
        Clock.schedule_once(self.load_tasks, 0.3)
    
    def on_task_edit(self, task_id):
        screen = self.manager.get_screen("add_task")
        screen.load_task(task_id)
        self.manager.current = "add_task"
    
    def on_enter(self):
        self.load_tasks()