from globs import hflib
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
        self.clock: hflib.HFClock = hflib.HFClock()
        self.assets: hflib.HFAssetManager = hflib.HFAssetManager()
        self.events: hflib.HFEventManager = hflib.HFEventManager()
        self.window: hflib.HFWindow = hflib.HFWindow(
            [800, 600], [32*50, 32*50],
            [10, 10, 10]
        )
        self.camera: hflib.HFCamera = hflib.HFCamera(self.window)
        self.renderer: hflib.HFRenderer = hflib.HFRenderer(self.camera)

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