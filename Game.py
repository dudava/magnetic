import pygame as pg
from loguru import logger

from GameClient import *
from settings import HOST

logger.add("file.log", backtrace=True, diagnose=True, enqueue=True, )


WIDTH, HEIGHT = SIZE = 640, 480
FPS = 100
display = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
running = True

allPersons = pg.sprite.Group()


class Person(pg.sprite.Sprite, ISynchronizedObject):
    def __init__(self, coords, color):
        ISynchronizedObject.__init__(self)
        super().__init__(allPersons)
        self.color = color

        self.wh = (30, 50)
        self.velocity = 100
        self.rect = pg.rect.Rect(*coords, *self.wh)
        self.image = pg.Surface(self.wh)
        pg.draw.rect(self.image, self.color, (0, 0, *self.wh))

    @staticmethod
    def getInitSyncObjectData(packageDict):
        logger.debug(packageDict)
        init_dict = {"coords": packageDict["coords"],
                     "color": (0, 0, 0)}
        logger.debug(init_dict)
        return init_dict

    def returnPackingData(self):
        logger.debug(f"Hero get pos: {self.rect}")
        return {"coords": (self.rect.x, self.rect.y)}

    def setPackingData(self, data):
        logger.debug(f"Hero set pos: {self.rect}")
        self.rect.x, self.rect.y = data["coords"]

    def remove(self):
        for _ in self.groups():
            _.remove(self)

    def update(self, delta, direction):
        self.rect = self.rect.move(round(direction[0]*self.velocity), round(direction[1]*self.velocity))
        logger.debug(self.rect)


client = GameTCPClient(HOST, globals(), globalsEnabled=True)
client.start()
client.isInitDone.wait()

hero = client.synchronize(Person, None, coords=(100, 200), color=(0, 0, 0))

while running:
    direction = (0, 0)
    delta = clock.tick(FPS) / 1000
    logger.debug(f"Hero pos before sync: {hero.rect}")
    package = client.getPackage()
    if package:     
        client.processPackage(package)
        
    logger.debug(f"Hero pos after sync: {hero.rect}")
    for event in pg.event.get():
        logger.debug(f"Proccess event: {event}")
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            direction = (pg.key.get_pressed()[pg.K_d] - pg.key.get_pressed()[pg.K_a],
                 pg.key.get_pressed()[pg.K_s] - pg.key.get_pressed()[pg.K_w])
        if event.type == pg.MOUSEBUTTONDOWN:
            logger.info(event.pos)
            hero.rect.x, hero.rect.y = event.pos 
    logger.debug("Start render")
    display.fill((255, 255, 255))

    
    if not(direction[0] == 0 and direction[1] == 0):
        hero.update(delta, direction)
    allPersons.draw(display)
    logger.debug("Frame prerendered")
    pg.display.flip()
    logger.debug("Frame rendered")
    client.donePackage()

print("Quited")
pg.quit()
client.close()