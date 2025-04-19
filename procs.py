from globs import hflib, HF_GAME_STATE

class LoadAssetsProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "render")
        self.game = game
    
    def callback(self, data):
        self.game.assets.load_image("burber", "assets\\images\\burber.png", [32, 32])

class ConfigureProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "configure")
        self.game = game

    def callback(self, data):
        self.game.player = hflib.game.HFObject(
            size=[32, 32], color=[255, 255, 255],
            location=[64, 64], mass=500
        )

        self.game.player._image = self.game.assets.get_image("burber")
        self.game.player.image = self.game.player._image

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

        self.game.renderer.set_flag(self.game.renderer.FLAGS.SHOW_CAMERA)

        self.game.partition = hflib.game.HFStaticPartition([10, 10], 32)
        self.game.partition.set_cell(self.game.player)
        self.game.partition.set_cell(self.game.map.tiles)
        
class UpdateProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "update")
        self.game = game

    def callback(self, data) -> None:
        self.game.clock.update()
        self.game.events.update()
        # self.game.window.clear()

        if self.game.events.key_pressed(hflib.HFKeyboard.Escape):
            self.game.rem_state(HF_GAME_STATE.RUNNING)

        if self.game.events.key_held(hflib.HFKeyboard.A):
            self.game.player.set_velocity(vx=-100)
        if self.game.events.key_held(hflib.HFKeyboard.D):
            self.game.player.set_velocity(vx=100)
        
        if self.game.events.key_held(hflib.HFKeyboard.W):
            self.game.player.set_velocity(vy=-100)
        if self.game.events.key_held(hflib.HFKeyboard.S):
            self.game.player.set_velocity(vy=100)

        if self.game.events.key_pressed(hflib.HFKeyboard.Space):
            self.game.player.set_velocity(vy=-500)

        if self.game.events.mouse_wheel_up: self.game.camera.mod_viewport(-2)
        if self.game.events.mouse_wheel_down: self.game.camera.mod_viewport(2)

        self.game.partition.rem_cell(self.game.player)
        self.game.player.update(self.game.map.get_region([1, 1], self.game.player.center()), self.game.clock.delta)
        self.game.partition.set_cell(self.game.player)

        self.game.camera.center_on(self.game.player.size, self.game.player.location)
        self.game.camera.update(self.game.clock.delta)
        self.game.clock.rest()
        return True

class RenderProc(hflib.HFProc):
    def __init__(self, game) -> None:
        super().__init__(0, "render")
        self.game = game

        def post_render():
            self.game.partition.debug_render(self.game.renderer, self.game.player.center())
            # either of these spatial queries works :)
            [self.game.window.draw_rect(t.size, t.location, [255, 0, 0], 1)
            for cell in self.game.partition.get_region([1, 1], self.game.player.center()) for t in cell]
            # for t in self.game.map.get_region([1, 1], self.game.player.center())]

        self.game.renderer.post_render = post_render

    def callback(self, data):
        [self.game.renderer.draw_call(obj.image, obj.location) for obj in [self.game.player, *self.game.map.tiles] if obj]
        self.game.renderer.render()
