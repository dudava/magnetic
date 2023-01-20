import pygame as pg
import random

from GameClient import *
from settings import HOST

pg.init()
SIZE = WIDTH, HEIGHT = 1280, 720
display = pg.display.set_mode(SIZE)    
running = True
fps = 60
clock = pg.time.Clock()

allSprites = pg.sprite.Group()

class Hero(pg.sprite.Sprite, ISynchronizedObject):
    def __init__(self, rect, color):
        ISynchronizedObject.__init__(self)
        super().__init__(allSprites)
        self.velocity = 100
        self.rect = pg.rect.Rect(*rect)
        self.image = pg.Surface((self.rect.w, self.rect.h))
        self.color = color
        pg.draw.rect(self.image, self.color, (0, 0, self.rect.w, self.rect.h))

    @staticmethod
    def getInitSyncObjectData(packageDict):
        packageDict["rect"] = tuple(packageDict["rect"])
        return packageDict

    def returnPackingData(self):
        return {"rect": [self.rect.x, self.rect.y, self.rect.w, self.rect.h], 
                "color": self.color}

    def setPackingData(self, dictionary):
        self.rect = pg.Rect(dictionary["rect"])
        self.color = dictionary["color"]
        pg.draw.rect(self.image, self.color, (0, 0, self.rect.w, self.rect.h))

    def update(self, delta, direction):
        self.rect = self.rect.move(round(direction * self.velocity * delta), 0)

    def remove(self):
        for _ in self.groups():
            _.remove(self)
        print(self.groups())


if __name__ == "__main__":
    client = GameTCPClient(HOST, globals(), True)
    client.start()
    client.isInitDone.wait()
    print(client.id)
    hero = client.synchronize(Hero, None, rect=(0, random.randint(100, 300), 20, 20), color=(random.randint(0, 255), 0, 0))
    direction = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        delta = clock.tick(fps) / 1000
        pack = client.getPackage()
        if pack:
            client.processPackage(pack)
            client.donePackage()

        display.fill((255, 255, 255))

        allSprites.update(delta, 1)
        allSprites.draw(display)

        pg.display.flip()

    pg.quit()
    client.close()