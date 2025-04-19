from globs import r3frame
from procs import LoadAssetsProc, ConfigureProc, UpdateProc, RenderProc

class THEGAME:
    def __init__(self) -> None:
        self.version: str = "2025.0.1"
        self.state: int = 0
        self.init()

    def set_state(self, flag: int) -> None:
        self.state |= flag

    def get_state(self, flag: int) -> bool:
        return ((self.state & flag) == flag)

    def rem_state(self, flag: int) -> None:
        self.state &= ~flag

    def init(self) -> None:
        self.clock: r3frame.app.Clock = r3frame.app.Clock()
        self.assets: r3frame.app.AssetManager = r3frame.app.AssetManager()
        self.events: r3frame.app.EventManager = r3frame.app.EventManager()
        self.window: r3frame.app.Window = r3frame.app.Window(
            [800, 600], [32*50, 32*50],
            [10, 10, 10]
        )
        self.camera: r3frame.app.Camera = r3frame.app.Camera(self.window)
        self.renderer: r3frame.app.Renderer = r3frame.app.Renderer(self.camera)

        LoadAssetsProc(self).callback(None)
        ConfigureProc(self).callback(None)

    def run(self) -> None:
        update = UpdateProc(self)
        render = RenderProc(self)
        while not self.events.quit:
            update.callback(None)
            render.callback(None)
        else:
            self.exit()

    def exit(self) -> None:
        print("exiting...")

THEGAME().run()