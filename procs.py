from globs import hflib, HF_GAME_STATE

class ConfigureProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "configure")
        self.game = game

    def callback(self, data):
        self.game.player = hflib.HFGameObject(
            size=[16, 16], color=[255, 255, 255]
        )

        self.game.map = hflib.HFTilemap([10, 10], 32)
        self.game.map.import_data("hfmap.txt")
        self.game.map.load()
        # self.game.map.read_data([
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        # ])
        # self.game.map.export_data("hfmap.txt")
        
class UpdateProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "update")
        self.game = game

    def callback(self, data) -> None:
        self.game.clock.update()
        self.game.events.update()
        self.game.window.clear()

        if self.game.events.key_pressed(hflib.HFKeyboard.Escape):
            self.game.rem_state(HF_GAME_STATE.RUNNING)

        if self.game.events.key_held(hflib.HFKeyboard.A):
            self.game.player.move(0)
            self.game.player.set_velocity(vx=-100)
        else: self.game.player.stop(0)
        if self.game.events.key_held(hflib.HFKeyboard.D):
            self.game.player.move(1)
            self.game.player.set_velocity(vx=100)
        else: self.game.player.stop(1)
        
        if self.game.events.key_held(hflib.HFKeyboard.W):
            self.game.player.move(2)
            self.game.player.set_velocity(vy=-100)
        else: self.game.player.stop(2)
        if self.game.events.key_held(hflib.HFKeyboard.S):
            self.game.player.move(3)
            self.game.player.set_velocity(vy=100)
        else: self.game.player.stop(3)

        if self.game.events.mouse_pressed(hflib.HFMouse.LeftClick):
            region = self.game.map.get_tile_region([1, 1], hflib.HFMouse.get_location())
            for tile in region:
                if not tile: continue
                tile.set_color([255, 0, 0])

        self.game.player.update(self.game.clock.delta)

        self.game.clock.rest()
        return True

class RenderProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "render")
        self.game = game

    def callback(self, data):
        for t in self.game.map.tiles:
            if not t: continue
            t.render(self.game.window)
        self.game.player.render(self.game.window)
        self.game.window.update()
