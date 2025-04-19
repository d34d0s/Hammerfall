from globs import r3frame
from ui import DebugButton, InteractTip

class LoadAssetsProc(r3frame.app.Process):
    def __init__(self, game) -> None:
        super().__init__(0, "render")
        self.game = game
    
    def callback(self, data):
        self.game.assets.load_image("burber", "assets\\images\\burber.png", [32, 32])
        self.game.assets.load_image("barrel", "assets\\images\\barrel.png", [10, 16])
        self.game.assets.load_image_sheet("tileset", "assets\\images\\tileset.png", [16, 16], scale=[32, 32])

class ConfigureProc(r3frame.app.Process):
    def __init__(self, game) -> None:
        super().__init__(0, "configure")
        self.game = game
        self.game.debug_mode = False

    def callback(self, data):
        self.game.player = r3frame.game.Object(
            size=[32, 32], color=[255, 255, 255],
            location=[64, 64], mass=500
        )
        self.game.barrel = r3frame.game.Object(
            size=[10, 16], color=[255, 255, 255],
            location=[200, 200], mass=500
        )

        self.game.player._image = self.game.assets.get_image("burber")
        self.game.player.image = self.game.player._image
        
        self.game.barrel._image = self.game.assets.get_image("barrel")
        self.game.barrel.image = self.game.barrel._image

        self.game.map = r3frame.app.Tilemap([10, 10], 32)
        
        # edit the map here
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
        #     1, 1, 1, 1, 2, 3, 4, 1, 1, 1,
        # ])
        # self.game.map.export_data("map.txt")
        
        self.game.map.import_data("map.txt")
        self.game.map.load()
        for tile in self.game.map.tiles:
            if not tile: continue
            tile._image = self.game.assets.get_image("tileset")[tile.id-1]
            tile.image = tile._image

        self.game.partition = r3frame.game.StaticPartition([10, 10], 32)
        self.game.partition.set_cell(self.game.player)
        self.game.partition.set_cell(self.game.barrel)
        self.game.partition.set_cell(self.game.map.tiles)
        
class UpdateProc(r3frame.app.Process):
    def __init__(self, game) -> None:
        super().__init__(0, "update")
        self.game = game

    def callback(self, data) -> None:
        self.game.clock.update()
        self.game.events.update()
        
        mouse_location = r3frame.app.Mouse.get_location()
        mouse_world_location = [
            mouse_location[0] / self.game.camera.viewport_scale[0] + self.game.camera.location[0],
            mouse_location[1] / self.game.camera.viewport_scale[1] + self.game.camera.location[1],
        ]

        self.game.interface.set_text_field("FPS", f"{self.game.clock.FPS:0.1f}")

        if self.game.events.key_pressed(r3frame.app.Keyboard.Escape):
            self.game.events.quit = True

        self.game.player.set_velocity(vx=100 * (self.game.events.key_held(r3frame.app.Keyboard.D) - self.game.events.key_held(r3frame.app.Keyboard.A)))
        self.game.player.set_velocity(vy=100 * (self.game.events.key_held(r3frame.app.Keyboard.S) - self.game.events.key_held(r3frame.app.Keyboard.W)))
        
        if self.game.events.key_pressed(r3frame.app.Keyboard.Space):
            self.game.player.set_velocity(vy=-500)

        if r3frame.point_inside(mouse_world_location, [*self.game.barrel.location, *self.game.barrel.size]):
            self.game.interface.set_tooltip("interact", InteractTip())
        else: self.game.interface.rem_tooltip("interact")

        if self.game.events.mouse_wheel_up: self.game.camera.mod_viewport(-2)
        if self.game.events.mouse_wheel_down: self.game.camera.mod_viewport(2)

        self.game.partition.rem_cell(self.game.player)
        self.game.player.update(self.game.map.get_region([1, 1], self.game.player.center()), self.game.clock.delta)
        self.game.partition.set_cell(self.game.player)

        self.game.camera.center_on(self.game.player.size, self.game.player.location)
        self.game.camera.update(self.game.clock.delta)
        self.game.clock.rest()

class RenderProc(r3frame.app.Process):
    def __init__(self, game) -> None:
        super().__init__(0, "render")
        self.game = game

        self.game.interface = r3frame.ui.Interface("debug", self.game.window, [100, 100], [0, 0], "assets\\fonts\\megamax.ttf", title_color=[100, 100, 100], text_color=[0, 255, 0])
        self.game.interface.set_button("Debug", DebugButton(self.game))
        def post_render():
            if self.game.debug_mode:
                self.game.partition.debug_render(self.game.renderer, self.game.player.center())
                # either of these spatial queries works :)
                [self.game.window.draw_rect(t.size, t.location, [255, 0, 0], 1)
                for cell in self.game.partition.get_region([1, 1], self.game.player.center()) for t in cell]
                # for t in self.game.map.get_region([1, 1], self.game.player.center())]

        self.game.renderer.post_render = post_render

    def callback(self, data):
        [self.game.renderer.draw_call(obj.image, obj.location) for obj in [self.game.player, self.game.barrel, *self.game.map.tiles] if obj]
        self.game.interface.update(self.game.events)
        self.game.renderer.render()
        self.game.interface.render()
        self.game.window.update()
