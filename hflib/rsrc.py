from .globs import re, os, pg, time
from .obj import HFGameObject

# ------------------------------------------------------------ #
class HFClock:
    FPS:int=0
    maxFPS:int=60
    last:float=0.0
    delta:float=0.0
    current:float=0.0

    def update(self) -> None:
        self.current = time.time()

        if self.last == 0.0:
            self.delta = 0.0
        else: self.delta = self.current - self.last

        self.last = self.current

        if self.delta > 0: self.FPS = 1 / self.delta

    def rest(self) -> None:
        time.sleep(max(1 / self.maxFPS - self.delta, 0))
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class HFWindow:
    def __init__(self, size: list[int], display_size: list[int], color: list[int]=[25, 25, 25]) -> None:
        self.icon = None
        self.title = "HFWindow"
        self.size = size
        self.color = color
        self.clip_range = [1, 1]
        self.display_size = display_size
        self.window = pg.display.set_mode(size)
        
        self.draw_line = lambda start, end, color, width: pg.draw.line(self.display, color, start, end, width=width)
        self.draw_rect = lambda size, location, color, width: pg.draw.rect(self.display, color, pg.Rect(location, size), width=width)
        self.draw_circle = lambda center, radius, color, width: pg.draw.circle(self.display, color, [*map(int, center)], radius, width)
        
        self.blit_rect = lambda rect, color, width: self.draw_rect(rect.size, rect.topleft, color, width)

        self.configure()

    def set_title(self, title: str) -> None: self.title = title
    def set_icon(self, icon: pg.Surface) -> None: self.icon = icon

    def configure(self) -> None:
        self.display = pg.Surface(self.display_size)
        if isinstance(self.title, str): pg.display.set_caption(self.title)
        if isinstance(self.icon, pg.Surface): pg.display.set_icon(self.icon)

    def clear(self) -> None:
        self.display.fill(self.color)
        self.window.fill(self.color)

    def blit(self, surface: pg.Surface, location: list[int], offset: list[int]=[0, 0]) -> None:
        # display-culling
        if ((location[0] + surface.size[0]) - self.clip_range[0] < 0 or location[0] + self.clip_range[0] > self.display_size[0]) \
        or ((location[1] + surface.size[1]) - self.clip_range[1] < 0 or location[1] + self.clip_range[1] > self.display_size[1]):
            return
        self.display.blit(surface, [location[0] - offset[0], location[1] - offset[1]])

    def update(self) -> None:
        self.window.blit(self.display, [0, 0])
        pg.display.flip()
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class HFAnimation:
    def __init__(self, frames: list[pg.Surface], loop: bool=1, frame_duration: float=5.0, frame_offset: list[int]=[0, 0]) -> None:
        self.done = 0
        self.frame = 0
        self.loop = loop
        self.flip_x = False
        self.flip_y = False
        self.frames = frames
        self.frame_offset = frame_offset
        self.frame_duration = frame_duration

    def reset(self) -> None: self.frame, self.done = 0, 0

    def copy(self):
        return HFAnimation(self.frames, self.loop, self.frame_duration, self.frame_offset)

    def get_frame(self):
        return pg.transform.flip(self.frames[int(self.frame / self.frame_duration)], self.flip_x, self.flip_y)

    def update(self) -> None:
        if self.loop:
            self.frame = (self.frame + 1) % (self.frame_duration * len(self.frames))
        else:
            self.frame = min(self.frame + 1, self.frame_duration * len(self.frames) - 1)
            if self.frame >= self.frame_duration * len(self.frames) - 1:
                self.done = 1
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class HFAssetManager:
    def __init__(self) -> None:
        self.font:dict = {}
        self.image:dict = {}
        self.audio:dict = {}

        self.create_surface = lambda size, color: pg.Surface(size)
        self.create_rect = lambda location, size: pg.Rect(location, size)

        self.fill_surface = lambda surface, color: surface.fill(color)
        self.flip_surface = lambda surface, x, y: pg.transform.flip(surface, x, y)
        self.scale_surface = lambda surface, scale: pg.transform.scale(surface, scale)
        self.rotate_surface = lambda surface, angle: pg.transform.rotate(surface, angle)

    def flip_image(self, key: str, x: bool, y: bool) -> None:
        try:
            image = self.image[key]
            if isinstance(image, pg.Surface):
                self.image[key] = self.flip_surface(image, x, y)
            elif isinstance(image, list):
                self.image[key] = [self.flip_surface(i, x, y) for i in image]
        except (KeyError) as err: print(err)

    def get_image(self, key:str) -> pg.Surface|pg.Surface:
        return self.image.get(key, None)
    
    def set_image(self, key:str, image:pg.Surface) -> pg.Surface|None:
        try:
            self.image[key] = image
        except (KeyError) as err: print(err)

    def load_image(self, key:str, path:str, scale:list=None, colorKey:list=None) -> pg.Surface:
        try:
            image:pg.Surface = pg.image.load(path).convert_alpha()
            image.set_colorkey(colorKey)
            if scale: image = self.scale_surface(image, scale)
            self.image[key] = image
            return self.image[key]
        except (FileNotFoundError) as err: print(err)
    
    def load_image_dir(self, key:str, path:str, scale:list=None, colorKey:list=None) -> list:
        try:
            images:list = []
            for _, __, image in os.walk(path):
                sorted_images = sorted(image, key=lambda string_: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)])
                for image in sorted_images:
                    full_path = path + '/' + image
                    image_surface = self.load_image(full_path, scale, colorKey)
                    if self.image_visible(image_surface):
                        images.append(image_surface)
            self.image[key] = images
            return self.image[key]
        except (FileNotFoundError) as err: ...
    
    def load_image_sheet(self, key: str, path: str, frameSize: list[int], colorKey: list=None) -> list:
        try:
            sheet = self.load_image(key, path)
            frame_x = int(sheet.get_size()[0] / frameSize[0])
            frame_y = int(sheet.get_size()[1] / frameSize[1])
            
            frames = []
            for row in range(frame_y):
                for col in range(frame_x):
                    x = col * frameSize[0]
                    y = row * frameSize[1]
                    frame = pg.Surface(frameSize, pg.SRCALPHA).convert_alpha()
                    frame.set_colorkey(colorKey)
                    frame.blit(sheet, (0,0), pg.Rect((x, y), frameSize))   # blit the sheet at the desired coords (texture mapping)
                    if self.image_visible(frame):
                        frames.append(frame)
            self.image[key] = frames
            return self.image[key]
        except (FileNotFoundError) as err: ...

    def image_visible(self, image:pg.Surface, threshold:int=1) -> bool:
        result = False
        pixels, noPixels = 0, 0
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                pixel = image.get_at([x, y])
                if pixel[3] == 0:
                    noPixels += 1
                pixels += 1
        if pixels-noPixels >= threshold:
            result = True
        return result
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class HFTilemap:
    def __init__(self, size: list[int], tilesize: int=32) -> None:
        self.size = size
        self.tilesize = tilesize
        self.data = [None for _ in range(size[0] * size[1])]
        self.tiles = [None for _ in range(size[0] * size[1])]

    def export_data(self, path: str) -> bool:
        with open(path, "w") as save:
            for c in map(str, self.data):
                save.write(c)
        return True
    
    def import_data(self, path:str) -> bool:
        with open(path, "r") as save:
            data = re.split(r'(\d)', save.read())
            data = [t for t in data if t != '']
            for i in range(len(data)):
                try: data[i] = int(data[i])
                except: pass
            self.data = data
        return True

    def set_data(self, location: list[int], data: int|str) -> None:
        mapx = (location[0] * self.tilesize) // self.tilesize
        mapy = (location[1] * self.tilesize) // self.tilesize
        if mapx < 0 or mapy < 0 or mapx > self.size[0] or mapy > self.size[1]: return
        self.data[mapy * self.size[0] + mapx] = data

    def get_data(self, location: list[int]) -> int|str|None:
        mapx = (location[0] * self.tilesize) // self.tilesize
        mapy = (location[1] * self.tilesize) // self.tilesize
        if mapx < 0 or mapy < 0 or mapx > self.size[0] or mapy > self.size[1]: return None
        return self.data[mapy * self.size[0] + mapx]

    def read_data(self, data: list[int|str]) -> None:
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.set_data([x, y], data[y * self.size[0] + x])
    
    def get_tile(self, location: list[int]) -> HFGameObject|None:
        mapx = (location[0] * self.tilesize) // self.tilesize
        mapy = (location[1] * self.tilesize) // self.tilesize
        if mapx < 0 or mapy < 0 or mapx > self.size[0] or mapy > self.size[1]: return None
        return self.tiles[mapy * self.size[0] + mapx]

    def _generate_region(self, size:list[int], location:list[int]) -> list[list]|None:
        region = []
        for x in range(int((location[0] - size[0]) // self.tilesize), int((location[0] + size[0]) // self.tilesize) + 1):
            for y in range(int((location[1] - size[1]) // self.tilesize), int((location[1] + size[1]) // self.tilesize) + 1):
                region.append([x, y])
        return region

    def get_tile_region(self, size:list[int], location:list[int]) -> list[HFGameObject]|None:
        region = self._generate_region(size, location)
        if not region: return None
        tiles = []
        for map_location in region:
            index = map_location[1] * self.size[0] + map_location[0]
            if index < 0 or index >= (self.size[0] * self.size[1]): continue
            tiles.append(self.tiles[index])
        return tiles

    def load(self) -> None:
        if not isinstance(self.data, list): return
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                data_tile = self.data[y * self.size[0] + x]
                if data_tile != 0 and data_tile != None:
                    tile = HFGameObject(
                        size=[self.tilesize, self.tilesize], color=[255, 255, 255],
                        location=[x * self.tilesize, y * self.tilesize]
                    )
                    tile.id = data_tile
                    self.tiles[y * self.size[0] + x] = tile
# ------------------------------------------------------------ #
