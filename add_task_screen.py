from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

class AddTaskScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.editing_task_id = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(16))
        
        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)]
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self.go_back()
        )
        header.add_widget(back_btn)
        
        self.title_label = MDLabel(
            text="New Task",
            font_style="H5",  # Changed from HeadlineSmall
            theme_text_color="Primary",
            bold=True
        )
        header.add_widget(self.title_label)
        main_layout.add_widget(header)
        
        form = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(24),
            adaptive_height=True
        )
        
        self.title_input = MDTextField(
            hint_text="Task Title",
            required=True,
            mode="rectangle"  # Changed from outlined for compatibility
        )
        form.add_widget(self.title_input)
        
        self.desc_input = MDTextField(
            hint_text="Description (optional)",
            mode="rectangle",  # Changed from outlined
            multiline=True,
            height=dp(100)
        )
        form.add_widget(self.desc_input)
        
        self.category_btn = MDRaisedButton(
            text="Category: General",
            on_release=self.show_category_menu,
            size_hint_x=1
        )
        self.selected_category = "General"
        form.add_widget(self.category_btn)
        
        self.priority_btn = MDRaisedButton(
            text="Priority: Medium",
            on_release=self.show_priority_menu,
            size_hint_x=1
        )
        self.selected_priority = "Medium"
        form.add_widget(self.priority_btn)
        
        date_box = MDBoxLayout(spacing=dp(8))
        self.date_label = MDLabel(
            text="Due Date: Not set",
            theme_text_color="Secondary",
            size_hint_x=0.7
        )
        date_box.add_widget(self.date_label)
        
        date_btn = MDRaisedButton(
            text="Pick Date",
            on_release=self.show_date_picker,
            size_hint_x=0.3
        )
        date_box.add_widget(date_btn)
        form.add_widget(date_box)
        
        main_layout.add_widget(form)
        main_layout.add_widget(MDBoxLayout())
        
        save_btn = MDRaisedButton(
            text="Save Task",
            pos_hint={"center_x": 0.5},
            size_hint=(0.8, None),
            height=dp(50),
            on_release=self.save_task
        )
        main_layout.add_widget(save_btn)
        
        self.add_widget(main_layout)
        
        self.init_menus()
    
    def init_menus(self):
        categories = self.db.get_categories()
        cat_items = [
            {
                "text": cat['name'],
                "on_release": lambda x=cat['name']: self.set_category(x)
            } for cat in categories
        ]
        self.category_menu = MDDropdownMenu(
            caller=self.category_btn,
            items=cat_items,
            width_mult=4
        )
        
        priority_items = [
            {"text": "High", "on_release": lambda x="High": self.set_priority(x)},
            {"text": "Medium", "on_release": lambda x="Medium": self.set_priority(x)},
            {"text": "Low", "on_release": lambda x="Low": self.set_priority(x)}
        ]
        self.priority_menu = MDDropdownMenu(
            caller=self.priority_btn,
            items=priority_items,
            width_mult=4
        )
    
    def show_category_menu(self, *args):
        self.category_menu.open()
    
    def set_category(self, category):
        self.selected_category = category
        self.category_btn.text = f"Category: {category}"
        self.category_menu.dismiss()
    
    def show_priority_menu(self, *args):
        self.priority_menu.open()
    
    def set_priority(self, priority):
        self.selected_priority = priority
        self.priority_btn.text = f"Priority: {priority}"
        self.priority_menu.dismiss()
    
    def show_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()
    
    def on_date_save(self, instance, value, date_range):
        self.selected_date = value.isoformat()
        self.date_label.text = f"Due Date: {value.strftime('%b %d, %Y')}"
    
    def save_task(self, *args):
        if not self.title_input.text.strip():
            self.title_input.error = True
            return
        
        if self.editing_task_id:
            self.db.update_task(
                self.editing_task_id,
                title=self.title_input.text,
                description=self.desc_input.text,
                category=self.selected_category,
                priority=self.selected_priority,
                due_date=getattr(self, 'selected_date', None)
            )
        else:
            self.db.add_task(
                title=self.title_input.text,
                description=self.desc_input.text,
                category=self.selected_category,
                priority=self.selected_priority,
                due_date=getattr(self, 'selected_date', None)
            )
        
        self.clear_form()
        self.manager.current = "task_list"
    
    def load_task(self, task_id):
        task = self.db.get_task(task_id)
        if task:
            self.editing_task_id = task_id
            self.title_label.text = "Edit Task"
            self.title_input.text = task['title']
            self.desc_input.text = task['description'] or ""
            self.set_category(task['category'])
            self.set_priority(task['priority'])
            if task['due_date']:
                self.selected_date = task['due_date']
                self.date_label.text = f"Due Date: {task['due_date']}"
    
    def clear_form(self):
        self.editing_task_id = None
        self.title_label.text = "New Task"
        self.title_input.text = ""
        self.desc_input.text = ""
        self.set_category("General")
        self.set_priority("Medium")
        self.date_label.text = "Due Date: Not set"
        if hasattr(self, 'selected_date'):
            delattr(self, 'selected_date')
    
    def go_back(self):
        self.clear_form()
        self.manager.current = "task_list"
    
    def on_enter(self):
        if not hasattr(self, 'category_menu'):
            self.init_menus()