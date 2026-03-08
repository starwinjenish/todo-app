from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from chart_widget import StatsChart

class StatsScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical')
        
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
        
        title = MDLabel(
            text="Statistics",
            font_style="H5",  # Changed from HeadlineSmall
            theme_text_color="Primary",
            bold=True
        )
        header.add_widget(title)
        main_layout.add_widget(header)
        
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None,
            adaptive_height=True
        )
        
        summary_box = MDBoxLayout(spacing=dp(12), size_hint_y=None, height=dp(100))
        
        self.total_card = self.create_stat_card("Total", "0")
        self.completed_card = self.create_stat_card("Done", "0")
        self.rate_card = self.create_stat_card("Rate", "0%")
        
        summary_box.add_widget(self.total_card)
        summary_box.add_widget(self.completed_card)
        summary_box.add_widget(self.rate_card)
        content.add_widget(summary_box)
        
        progress_card = MDCard(
            style="elevated",
            padding=dp(16),
            radius=dp(16),
            size_hint_y=None,
            height=dp(120)
        )
        
        progress_layout = MDBoxLayout(orientation='vertical', spacing=dp(8))
        progress_label = MDLabel(
            text="Completion Progress",
            font_style="H6",  # Changed from TitleMedium
            theme_text_color="Primary"
        )
        progress_layout.add_widget(progress_label)
        
        self.progress_bar = ProgressBar(
            value=0,
            max=100,
            size_hint_y=None,
            height=dp(8)
        )
        
        with self.progress_bar.canvas:
            Color(0.9, 0.9, 0.9, 1)
            self.progress_bg = Rectangle(pos=self.progress_bar.pos, size=self.progress_bar.size)
            Color(0.4, 0.34, 0.98, 1)
            self.progress_fill = Rectangle(pos=self.progress_bar.pos, size=(0, self.progress_bar.height))
        
        self.progress_bar.bind(pos=self.update_progress_bar)
        self.progress_bar.bind(size=self.update_progress_bar)
        self.progress_bar.bind(value=self.update_progress_bar)
        
        progress_layout.add_widget(self.progress_bar)
        
        self.progress_text = MDLabel(
            text="0% complete",
            font_style="Caption",  # Changed from BodySmall
            theme_text_color="Secondary",
            halign="center"
        )
        progress_layout.add_widget(self.progress_text)
        progress_card.add_widget(progress_layout)
        content.add_widget(progress_card)
        
        self.category_chart = StatsChart(size_hint_y=None, height=dp(350))
        content.add_widget(self.category_chart)
        
        self.priority_chart = StatsChart(size_hint_y=None, height=dp(350))
        content.add_widget(self.priority_chart)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)
    
    def update_progress_bar(self, *args):
        if hasattr(self, 'progress_bg'):
            self.progress_bg.pos = self.progress_bar.pos
            self.progress_bg.size = self.progress_bar.size
            percentage = self.progress_bar.value / self.progress_bar.max
            fill_width = self.progress_bar.width * percentage
            self.progress_fill.pos = self.progress_bar.pos
            self.progress_fill.size = (fill_width, self.progress_bar.height)
    
    def create_stat_card(self, title, value):
        card = MDCard(
            style="elevated",
            radius=dp(16),
            padding=dp(12)
        )
        
        layout = MDBoxLayout(orientation='vertical')
        
        value_label = MDLabel(
            text=value,
            font_style="H4",  # Changed from HeadlineMedium
            theme_text_color="Primary",
            halign="center",
            bold=True
        )
        layout.add_widget(value_label)
        
        title_label = MDLabel(
            text=title,
            font_style="Overline",  # Changed from LabelSmall
            theme_text_color="Secondary",
            halign="center"
        )
        layout.add_widget(title_label)
        
        if title == "Total":
            self.total_value_label = value_label
        elif title == "Done":
            self.completed_value_label = value_label
        elif title == "Rate":
            self.rate_value_label = value_label
        
        card.add_widget(layout)
        return card
    
    def go_back(self):
        self.manager.current = "task_list"
    
    def on_enter(self):
        stats = self.db.get_statistics()
        
        self.total_value_label.text = str(stats['total_tasks'])
        self.completed_value_label.text = str(stats['completed_tasks'])
        self.rate_value_label.text = f"{stats['completion_rate']:.0f}%"
        
        self.progress_bar.value = stats['completion_rate']
        self.progress_text.text = f"{stats['completion_rate']:.1f}% complete"
        
        self.category_chart.update_data(stats['category'], "Tasks by Category")
        self.priority_chart.update_data(stats['priority'], "Tasks by Priority")