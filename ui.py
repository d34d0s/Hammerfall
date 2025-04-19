from globs import r3frame

class DebugButton(r3frame.ui.Button):
    def __init__(self, game):
        self.game = game
        super().__init__(font_path="assets\\fonts\\megamax.ttf", text="Debug", size=[100, 100])
        self.padding = [20, 40]
        self.show_border = 1
        self.border_color = [255, 0, 0]
        self.border_radius = [1, 1, 1, 1]
        self.location = [
            self.game.window.size[0] - self.size[0],
            self.game.window.size[1] - self.size[1]
        ]

    def on_click(self):
        self.game.debug_mode = not self.game.debug_mode
        if self.game.debug_mode:
            self.border_color = [0, 255, 0]
        else: self.border_color = [255, 0, 0]

class InteractTip(r3frame.ui.Tooltip):
    def __init__(self) -> None:
        super().__init__(
            size=[150, 64],
            text='Press\n"Interact"',
            font_path="assets\\fonts\\megamax.ttf"
        )
        self.show_border = True
        self.padding = [5, 5]
        self.offset = [10, -10]
        self.location = r3frame.app.input.Mouse.get_location()

