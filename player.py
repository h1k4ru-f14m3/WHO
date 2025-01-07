import pygame
import settings
from map import getin_building
from time import sleep
from os import listdir

class Player(pygame.sprite.Sprite):
    def __init__(self,group,pos,othergroups=0):
        super().__init__(group)

        file_path = 'resources/entities/player'
        self.animation_index = 0
        self.facing = 'front'
        self.frames = {
            'back': [self.get_frames(file_path)[i] for i in range(0,5)],
            'front': [self.get_frames(file_path)[i] for i in range(5,10)],
            'left': [self.get_frames(file_path)[i] for i in range(10,15)],
            'right': [self.get_frames(file_path)[i] for i in range(15,20)]
        }

        self.image = self.frames[self.facing][self.animation_index]
        self.rect = self.image.get_rect(center=(pos)) # OG: 1710, 1820; Testing: 1710, 930; New: 1695, 1820; Interior Test: 848,910
        self.hitbox = self.rect.inflate(-75,-75)
        self.direction = pygame.math.Vector2()
        self.speed = 3
        self.z = settings.draw_order["Player"]
        self.y_sort = self.rect.centery

        self.group = group
        self.othergroups = othergroups


    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.facing = 'back'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 'front'
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = 'left'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'right'
        else:
            self.direction.x = 0


    def animation(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.image = self.frames[self.facing][0]
            return

        self.animation_index += 0.15
        if self.animation_index >= 5:
            self.animation_index = 1
        self.image = self.frames[self.facing][int(self.animation_index)]
        

    def get_frames(self,path):
        newlist = []
        for file in listdir(path):
            newlist.append(pygame.transform.scale(pygame.image.load(f'{path}/{file}').convert_alpha(), (100,100)))
        return newlist


    def collision_check(self,direction):
        if self.othergroups == 0:
            return

        for sprite in self.othergroups:
            if sprite.name == 'door' and sprite.hitbox.colliderect(self.hitbox):
                print("1")
                self.group.unload_map(self)
                self.group.load_main()
                self.hitbox.centerx = settings.ending[0]
                self.hitbox.centery = settings.ending[1] + 25

                settings.current_floor = 0
                settings.stair_end = (0,0)
                settings.onMainMap = True
                settings.inBuilding = False
                settings.building = "None"
                return
            
            elif sprite.name == 'stair' and sprite.hitbox.colliderect(self.hitbox):
                self.group.unload_map(self)
                if settings.current_floor == 1:
                    getin_building((self.group), self, settings.building,floor_num = settings.current_floor + 1)
                    settings.current_floor += 1
                else:
                    getin_building((self.group), self, settings.building,floor_num = settings.current_floor - 1)
                    settings.current_floor -= 1
                
                print("1")
            
            elif settings.onMainMap and self.hitbox.collidepoint(sprite.door):
                print("2")
                print(sprite.type)
                settings.ending = self.hitbox.center

                if sprite.type == "House-3": settings.current_floor = 1
                getin_building((self.group), self, sprite.type,floor_num=settings.current_floor)


            if direction == 'h' and sprite.hitbox.colliderect(self.hitbox):
                if self.direction.x > 0:
                    self.hitbox.right = sprite.hitbox.left
                else:
                    self.hitbox.left = sprite.hitbox.right

            if direction == 'v' and sprite.hitbox.colliderect(self.hitbox):
                if self.direction.y > 0:
                    self.hitbox.bottom = sprite.hitbox.top
                else:
                    self.hitbox.top = sprite.hitbox.bottom

            
                # print(settings.ending)

        self.border_collision()


    def border_collision(self):
        if self.hitbox.collidepoint(0,self.hitbox.centery): self.hitbox.left = 0
        if self.hitbox.collidepoint(4096,self.hitbox.centery): self.hitbox.right = 4096
        if self.hitbox.collidepoint(self.hitbox.centerx,0): self.hitbox.top = 0
        if self.hitbox.collidepoint(self.hitbox.centerx,4096): self.hitbox.bottom = 4096  


    def collision_functions(self):
        for sprite in self.othergroups:
            if sprite.name != "door": continue
            if self.hitbox.colliderect(sprite.hitbox):
                print("OK!")


    def update(self):
        self.y_sort = self.rect.centery
        self.input()
        self.hitbox.centerx += self.direction.x * self.speed
        self.collision_check('h')
        self.hitbox.centery += self.direction.y * self.speed
        self.collision_check('v')
        self.rect.center = self.hitbox.center
        self.animation()