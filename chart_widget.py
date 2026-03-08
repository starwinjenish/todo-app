from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.metrics import dp
from kivy.animation import Animation

class PieChartWidget(Widget):
    data = ListProperty([])
    animate = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(data=self.draw_chart, pos=self.draw_chart, size=self.draw_chart)
        self.bind(animate=self.draw_chart)
        
    def on_data(self, *args):
        anim = Animation(animate=1, duration=0.8, t='out_quad')
        anim.start(self)
    
    def draw_chart(self, *args):
        self.canvas.clear()
        
        if not self.data:
            return
            
        total = sum(item['value'] for item in self.data)
        if total == 0:
            return
        
        center_x = self.center_x
        center_y = self.center_y
        radius = min(self.width, self.height) * 0.35 * self.animate
        
        start_angle = 0
        
        with self.canvas:
            for item in self.data:
                angle = (item['value'] / total) * 360
                
                Color(*item['color'])
                Ellipse(pos=(center_x - radius, center_y - radius),
                       size=(radius * 2, radius * 2),
                       angle_start=start_angle,
                       angle_end=start_angle + angle)
                
                Color(1, 1, 1, 1)
                Line(circle=(center_x, center_y, radius, start_angle, start_angle + angle), 
                     width=dp(2))
                
                start_angle += angle
            
            Color(0.95, 0.95, 0.95, 1)
            inner_radius = radius * 0.6
            Ellipse(pos=(center_x - inner_radius, center_y - inner_radius),
                   size=(inner_radius * 2, inner_radius * 2))

class LegendItem(BoxLayout):
    color = ListProperty([0.5, 0.5, 0.5, 1])
    text = StringProperty("")
    count = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30)
        self.spacing = dp(8)
        self.padding = [dp(8), 0]
        
        from kivymd.uix.label import MDLabel
        
        color_box = Widget(size_hint=(None, None), size=(dp(12), dp(12)))
        with color_box.canvas:
            Color(*self.color)
            self.rect = Rectangle(pos=color_box.pos, size=color_box.size)
        color_box.bind(pos=lambda obj, val: setattr(self.rect, 'pos', val))
        color_box.bind(size=lambda obj, val: setattr(self.rect, 'size', val))
        
        label = MDLabel(
            text=f"{self.text} ({self.count})", 
            theme_text_color="Secondary",
            font_style="Caption"  # Changed from BodySmall
        )
        
        self.add_widget(color_box)
        self.add_widget(label)

class StatsChart(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(16)
        
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        
        self.title_label = MDLabel(
            text="Task Distribution",
            font_style="H6",  # Changed from TitleMedium
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.title_label)
        
        chart_card = MDCard(
            elevation=2,
            padding=dp(16),
            radius=dp(16),
            size_hint_y=0.7
        )
        
        chart_layout = BoxLayout(orientation='horizontal')
        self.pie_chart = PieChartWidget(size_hint_x=0.6)
        self.legend_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(4))
        
        chart_layout.add_widget(self.pie_chart)
        chart_layout.add_widget(self.legend_layout)
        chart_card.add_widget(chart_layout)
        self.add_widget(chart_card)
    
    def update_data(self, data_dict: dict, title: str = "Distribution"):
        self.title_label.text = title
        
        colors = [
            (0.4, 0.34, 0.98, 1),
            (0.96, 0.26, 0.21, 1),
            (0.13, 0.59, 0.95, 1),
            (0.3, 0.69, 0.31, 1),
            (1.0, 0.76, 0.03, 1),
            (0.01, 0.66, 0.96, 1),
            (1.0, 0.6, 0.0, 1),
            (0.61, 0.15, 0.69, 1),
        ]
        
        chart_data = []
        self.legend_layout.clear_widgets()
        
        for i, (label, value) in enumerate(data_dict.items()):
            color = colors[i % len(colors)]
            chart_data.append({
                'label': label,
                'value': value,
                'color': color
            })
            
            legend = LegendItem(color=color, text=label, count=str(value))
            self.legend_layout.add_widget(legend)
        
        self.pie_chart.data = chart_data