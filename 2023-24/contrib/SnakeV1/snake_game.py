from collections import deque
from itertools import count
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
import random
from copy import deepcopy
from time import sleep
import smart_snake
import torch
from itertools import product
SCREEN_SIZE=[10,10]
# screen=np.zeros([3,SCREEN_SIZE[0],SCREEN_SIZE[1]], dtype=float)
# screen[0,:,0]=1
# screen[0,:,SCREEN_SIZE[1]-1]=1
# screen[0,0,:]=1
# screen[0,SCREEN_SIZE[0]-1,:]=1



RIGHT:int=0
UP:int=1
LEFT:int=2
DOWN:int=3


class Snake():
    def __init__(self, start_pos):
        self.body=[start_pos]
        self.direction=UP
    def move(self):
        new_head=deepcopy(self.body[0])

        if self.direction==RIGHT:
            new_head[1]+=1
        elif self.direction==UP:
            new_head[0]-=1
        elif self.direction==LEFT:
            new_head[1]-=1
        elif self.direction==DOWN:
            new_head[0]+=1
        
        self.body.insert(0, new_head)
        self.body.pop()
    def grow(self):
        self.body.insert(-1, deepcopy(self.body[-1]))

    def setdir(self, direction):
        #self.direction=((self.direction+direction-1)+4)%4
        if (direction+self.direction)%2!=0:
            self.direction=direction
    @property
    def pos(self):
        return self.body[0]
    def __len__(self):
        return len(self.body)
    

    
class Ground():
    def __init__(self, eat_reward=1, survival_reward=0, lose_reward=-1):
        self.screen=np.zeros([3,SCREEN_SIZE[0],SCREEN_SIZE[1]], dtype=float)
        self.snake=Snake([random.randint(1,SCREEN_SIZE[0]-2),
                            random.randint(1,SCREEN_SIZE[1]-2)])
        self.apple=[random.randint(1,SCREEN_SIZE[0]-2),
                            random.randint(1,SCREEN_SIZE[1]-2)]
        self.eat_reward=eat_reward
        self.survival_reward=survival_reward
        self.lose_reward=lose_reward
        self.update_screen()
        self.last_proximity_reward=0
        
    def update_screen(self, apple_proximity=False):
        self.screen=np.zeros([3,SCREEN_SIZE[0],SCREEN_SIZE[1]], dtype=float)
        self.screen[0,:,0]=1
        self.screen[0,:,SCREEN_SIZE[1]-1]=1
        self.screen[0,0,:]=1
        self.screen[0,SCREEN_SIZE[0]-1,:]=1
        self.place_apple(*self.apple)
        r=self.place_snake(apple_proximity)

        if r<self.survival_reward:
            self.reset()
        
        return r
    
    def get_snake_neighbour(self):
        head_collisions=[]
        for row in range(-1,2):
            for col in range(-1,2):
                if row==0 and col==0:
                    continue
                else:
                    head_collisions+=[int(self.is_wall(self.snake.pos[0]+row, self.snake.pos[1]+col))]
        return head_collisions


    def get_relative_apple_position(self):
        return np.array(self.apple)-np.array(self.snake.pos)

        
    
    def reset(self):
        self.snake=Snake([random.randint(1,SCREEN_SIZE[0]-2),
                            random.randint(1,SCREEN_SIZE[1]-2)])
        self.apple=[random.randint(1,SCREEN_SIZE[0]-2),
                            random.randint(1,SCREEN_SIZE[1]-2)]
        self.update_screen()

    def place_snake(self, apple_proximity=False):
        r=self.survival_reward
        for id in range(len(self.snake.body)-1,-1,-1):
            b=self.snake.body[id]
            if id==0:
                if self.is_wall(b[0],b[1]):
                    r=self.lose_reward

                self.place_snake_head(b[0],b[1])
                if self.is_apple(b[0],b[1]):
                    self.apple=[random.randint(1,SCREEN_SIZE[0]-2),
                            random.randint(1,SCREEN_SIZE[1]-2)]
                    self.snake.grow()
                    r=self.eat_reward
            else:
                self.place_snake_body(b[0],b[1])
        if apple_proximity and r!=self.lose_reward:
            a=self.get_relative_apple_position()
            r=20-(abs(a[0])+abs(a[1]))
        return r

    def is_wall(self, x,y):
        return self.screen[0,x,y]==1
    
    def is_apple(self, x,y):
        return self.screen[2,x,y]==1
    
    def step(self, action:int|None = None) ->(int, np.ndarray):
        if action!=None:
            self.snake.setdir(action)
        self.snake.move()
        r=self.update_screen(False)
        return r,self.screen 

    def place_apple(self,x,y):
        self.screen[2,x,y]=1
    def place_snake_head(self,x,y):
        self.screen[1,x,y]=1
    def place_snake_body(self,x,y):
        self.screen[0,x,y]=1


def action_to_str(action):
    if action==0:
        return 'TURN RIGHT'
    if action==1:
        return 'STRAIGHT'
    if action==2:
        return 'TURN LEFT'


def make_state(neighbours, direction, rel_apple, type):
    neighbours=torch.tensor(neighbours, dtype=type).cuda().view(-1)
    dir_onehot=torch.full([4,], 0., dtype=type).cuda().view(-1)
    dir_onehot[direction]=1
    rel_apple=torch.tensor(rel_apple, dtype=type).cuda().view(-1)

    return torch.cat([neighbours,dir_onehot,rel_apple], 0)
    


ground=Ground(10,0,-10)
plt.ion()
state=ground.screen
# state=torch.tensor(state, device=torch.device('cuda'), dtype=torch.float).unsqueeze(0)
state=make_state(ground.get_snake_neighbour(), ground.snake.direction, ground.get_relative_apple_position(), type=torch.float).unsqueeze(0)

training=True

for t in count():
    
    for d in count():
        plt.figure(1)
        plt.clf()
        plt.imshow(deepcopy(ground.screen).transpose(1,2,0))
        plt.pause(0.005)
        sleep(.005)


        action=smart_snake.select_action(state,training).view(1,1)
        reward, next_state=ground.step(action)
        game_over=reward==ground.lose_reward
        reward=torch.tensor(reward, device=torch.device('cuda'), dtype=torch.float).view(1,1)
        next_state=make_state(ground.get_snake_neighbour(), ground.snake.direction, ground.get_relative_apple_position(), type=torch.float).unsqueeze(0)

        # Add a penalty if it survives too long because probably it got stuck in some sort of loop
        if d>70*len(ground.snake):
            reward=torch.tensor(-30, device=torch.device('cuda'), dtype=torch.float).view(1,1)

        if not game_over:
            smart_snake.train_one_pass(state,action,reward,next_state)
            smart_snake.memory.push(state, 
                                    action, 
                                    reward, 
                                    next_state)
        else:
            smart_snake.train_one_pass(state,action,reward,None)
            smart_snake.memory.push(state, 
                                    action, 
                                    reward, 
                                    None)
            break
        smart_snake.train_step()
        state=next_state.clone()
        
    