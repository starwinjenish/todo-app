from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle

class TaskCard(MDCard):
    task_id = NumericProperty(0)
    title = StringProperty("")
    description = StringProperty("")
    category = StringProperty("General")
    due_date = StringProperty("")
    priority = StringProperty("Medium")
    status = StringProperty("Pending")
    category_color = ListProperty([0.4, 0.34, 0.98, 1])
    
    def __init__(self, on_complete=None, on_delete=None, on_edit=None, **kwargs):
        super().__init__(**kwargs)
        self.on_complete_callback = on_complete
        self.on_delete_callback = on_delete
        self.on_edit_callback = on_edit
        
        self.elevation = 2
        self.padding = dp(12)
        self.radius = dp(16)
        self.size_hint_y = None
        self.height = dp(100)
        
        self.build_ui()
        self.bind(status=self.update_appearance)
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        
        self.indicator = MDBoxLayout(
            size_hint=(None, 1),
            width=dp(4),
            md_bg_color=self.category_color,
            radius=[dp(4), 0, 0, dp(4)]
        )
        main_layout.add_widget(self.indicator)
        
        content = MDBoxLayout(orientation='vertical', spacing=dp(4))
        
        title_row = MDBoxLayout(size_hint_y=None, height=dp(24))
        self.title_label = MDLabel(
            text=self.title,
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        title_row.add_widget(self.title_label)
        
        priority_colors = {
            'High': (0.96, 0.26, 0.21, 1),
            'Medium': (1.0, 0.76, 0.03, 1),
            'Low': (0.3, 0.69, 0.31, 1)
        }
        
        self.priority_badge = MDLabel(
            text=self.priority,
            theme_text_color="Custom",
            text_color=priority_colors.get(self.priority, (0.5, 0.5, 0.5, 1)),
            font_style="Caption",
            size_hint_x=None,
            width=dp(50),
            halign="right"
        )
        title_row.add_widget(self.priority_badge)
        content.add_widget(title_row)
        
        self.desc_label = MDLabel(
            text=self.description[:50] + "..." if len(self.description) > 50 else self.description,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        )
        content.add_widget(self.desc_label)
        
        bottom_row = MDBoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
        
        # Use a BoxLayout with canvas for background instead of md_bg_color
        category_container = MDBoxLayout(
            size_hint=(None, 1),
            width=dp(80),
            padding=[dp(8), 0]
        )
        
        with category_container.canvas.before:
            Color(*self.category_color[:3], 0.15)
            self.category_bg = Rectangle(pos=category_container.pos, size=category_container.size)
        
        category_container.bind(pos=self.update_category_bg)
        category_container.bind(size=self.update_category_bg)
        
        self.category_chip = MDLabel(
            text=self.category,
            theme_text_color="Custom",
            text_color=self.category_color,
            font_style="Caption",
            halign="center",
            valign="center"
        )
        category_container.add_widget(self.category_chip)
        bottom_row.add_widget(category_container)
        
        if self.due_date:
            date_label = MDLabel(
                text=f"📅 {self.due_date}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_x=None
            )
            bottom_row.add_widget(date_label)
        
        bottom_row.add_widget(MDBoxLayout())
        content.add_widget(bottom_row)
        main_layout.add_widget(content)
        
        actions = MDBoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=dp(40),
            spacing=dp(4)
        )
        
        self.complete_btn = MDIconButton(
            icon="check-circle-outline" if self.status == "Pending" else "check-circle",
            theme_icon_color="Custom",
            icon_color=(0.3, 0.69, 0.31, 1) if self.status == "Completed" else (0.6, 0.6, 0.6, 1),
            on_release=self.toggle_complete
        )
        
        edit_btn = MDIconButton(
            icon="pencil-outline",
            theme_icon_color="Secondary",
            on_release=self.edit_task
        )
        
        delete_btn = MDIconButton(
            icon="trash-can-outline",
            theme_icon_color="Error",
            on_release=self.delete_task
        )
        
        actions.add_widget(self.complete_btn)
        actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        main_layout.add_widget(actions)
        
        self.add_widget(main_layout)
    
    def update_category_bg(self, *args):
        if hasattr(self, 'category_bg'):
            self.category_bg.pos = self.category_chip.parent.pos
            self.category_bg.size = self.category_chip.parent.size
    
    def update_appearance(self, *args):
        if self.status == "Completed":
            self.complete_btn.icon = "check-circle"
            self.complete_btn.icon_color = (0.3, 0.69, 0.31, 1)
            self.title_label.theme_text_color = "Secondary"
            self.opacity = 0.7
        else:
            self.complete_btn.icon = "check-circle-outline"
            self.complete_btn.icon_color = (0.6, 0.6, 0.6, 1)
            self.title_label.theme_text_color = "Primary"
            self.opacity = 1
    
    def toggle_complete(self, *args):
        new_status = "Completed" if self.status == "Pending" else "Pending"
        self.status = new_status
        if self.on_complete_callback:
            self.on_complete_callback(self.task_id, new_status)
    
    def edit_task(self, *args):
        if self.on_edit_callback:
            self.on_edit_callback(self.task_id)
    
    def delete_task(self, *args):
        anim = Animation(opacity=0, height=0, duration=0.3)
        anim.bind(on_complete=lambda *x: self.on_delete_callback(self.task_id) if self.on_delete_callback else None)
        anim.start(self)