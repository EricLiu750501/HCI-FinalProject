class BaseScreen:
    def __init__(self, callback):
        self.callback = callback
        self.button_areas = []
    
    def draw(self, frame):
        """Draw the screen content"""
        raise NotImplementedError
    
    def handle_click(self, x, y):
        """Handle mouse clicks"""
        raise NotImplementedError