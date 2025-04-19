from globs import hflib, HF_GAME_STATE
from procs import ConfigureProc, UpdateProc, RenderProc

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
            [800, 600], [800, 600],
            [10, 10, 10]
        )

        ConfigureProc(self).callback(None)

        self.set_state(HF_GAME_STATE.RUNNING)

    def run(self) -> None:
        while self.get_state(HF_GAME_STATE.RUNNING):
            UpdateProc(self).callback(None)
            RenderProc(self).callback(None)
        else:
            self.exit()

    def exit(self) -> None:
        print("exiting...")

THEGAME().run()