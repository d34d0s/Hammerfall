from .globs import pg
from .util import damp_lin

class HFGameObject:
    def __init__(self, size: list[int]=[32, 32], color: list[int]=[255, 255, 255], location: list[int]=[0, 0], mass: float=100) -> None:
        self.id = "obj"
        self.mass = mass
        self.size = size
        self.color = color
        self.velocity = [0, 0]
        self.minvelocity = 5.0
        self.location = location
        self.movement = [0, 0, 0, 0]    # l, r, u, d

        self._image = pg.Surface(size)
        self._image.fill(color)
        self.image = self._image

    def set_color(self, color: list[int]) -> None:
        self.color = color
        self._image.fill(color)
        self.image = self._image

    def rect(self) -> pg.Rect:
        return pg.Rect(self.location, self.size)
    
    def render(self, window) -> None:
        window.blit(self.image, self.location)

    def set_velocity(self, vx: float=0.0, vy: float=0.0) -> None:
        self.velocity[0] = vx if vx else self.velocity[0]
        self.velocity[1] = vy if vy else self.velocity[1]

    def move(self, direction:int) -> None:
        if direction < 0 or direction > 3: return
        self.movement[direction] = 1

    def stop(self, direction:int) -> None:
        if direction < 0 or direction > 3: return
        self.movement[direction] = 0

    def update(self, delta_time: float) -> None:
        transform = [
            (self.movement[1] - self.movement[0]) + self.velocity[0],
            (self.movement[3] - self.movement[2]) + self.velocity[1],
        ]

        self.location[0] += transform[0] * delta_time
        self.location[1] += transform[1] * delta_time

        self.velocity = [*map(lambda v: damp_lin(v, self.mass, self.minvelocity, delta_time), self.velocity)]
