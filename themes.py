class ThemeManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._init_default_values()
        return cls._instance

    def _init_default_values(self):
        self.BUTTONS_BG_COLOR = "#0077B6"
        self.LABELS_TEXT_COLOR = "#0077B6"
        self.BACKGROUND_COLOR = "#DFF6FF"
        self.BUTTONS_HOVER_COLOR = "#023E8A"
        self.BUTTONS_TEXT_COLOR = "white"
        self.INPUT_SCREEN_BG_COLOR = "#DFF6FF"
        self.INPUT_FIELDS_LABEL_COLOR = "#0077B6"
        self.BACKGROUND_IMG = "Assets/blue_background.png"

        self.THEMES = {
            "blue": {
                "buttons_bg": "#0077B6",
                "labels_text": "#0077B6",
                "background": "#DFF6FF",
                "buttons_hover": "#023E8A",
                "buttons_text": "white",
                "input_screen_bg": "#DFF6FF",
                "input_fields_label": "#0077B6",
                "background_img": "Assets/blue_background.png"
            },
            "orange": {
                "buttons_bg": "#FF876C",
                "labels_text": "#FF876C",
                "background": "#FFCFC4",
                "buttons_hover": "#D96548",
                "buttons_text": "white",
                "input_screen_bg": "#FFE7E2",
                "input_fields_label": "#BF6551",
                "background_img": "Assets/orange_background.png"
            },
            "black": {
                "buttons_bg": "#575352",
                "labels_text": "#2C2C2C",
                "background": "#b3afaf",
                "buttons_hover": "#333030",
                "buttons_text": "white",
                "input_screen_bg": "#b3afaf",
                "input_fields_label": "#2C2C2C",
                "background_img": "Assets/black_background.png"
            }
        }

    def update_theme(self, theme_name):
        if theme_name not in self.THEMES:
            raise ValueError(f"Theme '{theme_name}' not found")

        theme = self.THEMES[theme_name]
        self.BUTTONS_BG_COLOR = theme["buttons_bg"]
        self.LABELS_TEXT_COLOR = theme["labels_text"]
        self.BACKGROUND_COLOR = theme["background"]
        self.BUTTONS_HOVER_COLOR = theme["buttons_hover"]
        self.BUTTONS_TEXT_COLOR = theme["buttons_text"]
        self.INPUT_SCREEN_BG_COLOR = theme["input_screen_bg"]
        self.INPUT_FIELDS_LABEL_COLOR = theme["input_fields_label"]
        self.BACKGROUND_IMG = theme["background_img"]
