from collections import deque, namedtuple
import math
import numpy as np
import torch
from torch import nn,optim
from torch.nn import functional as F
import random

LEARN_RATE=0.0001
BATCH_SIZE=1024
GAMMA=0.99
ALPHA=.1
EPS_END=0.01
EPS_START=0.95
EPS_DECAY=500

class SimpleAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.flat=nn.Flatten()
        self.layer1=nn.Linear(14,256) # 5x5
        self.layer2=nn.Linear(256,128)
        self.final=nn.Linear(128,4)

    def forward(self, in_data) -> torch.Tensor:
        x=self.flat(in_data)
        x=self.layer1(x)
        x=F.relu(x)
        x=F.relu(self.layer2(x))
        x=self.final(x)
        return x

# A silly attempt at making a network that can see the whole screen and play (it didn't work they way it should have [it didn't work at all])
class Agent(nn.Module):  
    def __init__(self):
        super().__init__()
        self.layer1=nn.Linear(3*10*10,256) # 5x5
        self.flat=nn.Flatten()
        self.final=nn.Linear(256,3)

    def forward(self, in_data) -> torch.Tensor:
        x=self.flat(in_data)
        x=self.layer1(x)
        x=F.relu(x)
        x=self.final(x)
        return x
    
Transition=namedtuple('Transition', ('state','action','reward','next_state'))

# Keeps track of transitions
class ReplayMemory():
    def __init__(self, max_capacity=10000):
        self.memory=deque(maxlen=max_capacity)
    
    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def __len__(self):
        return len(self.memory)


memory=ReplayMemory(10000)

agent_ai=SimpleAgent().cuda()
target_agent_ai=SimpleAgent().cuda()
target_agent_ai.load_state_dict(agent_ai.state_dict())

#IF IT WORKS DON'T TOUCH IT
optimizer=optim.Adam(agent_ai.parameters(), LEARN_RATE, (0.5,.999), amsgrad=True)
criterion=nn.MSELoss()
#criterion=nn.SmoothL1Loss()
#criterion=nn.HuberLoss()
steps_done=0


#Train with just a transition
def train_one_pass(state,action,reward,next_state):
    state_action_value=agent_ai(state).gather(1,action).view(-1)
    expected_value=reward.clone().view(-1)
    if next_state is not None:
        with torch.no_grad():
            expected_value+=GAMMA*target_agent_ai(next_state).max(1).values.view(-1)

    optimizer.zero_grad()
    loss=criterion(state_action_value, expected_value)
    loss.backward()
    optimizer.step()

def train_step():
    if len(memory)<BATCH_SIZE:
        batch=memory.memory
    else:
        batch=memory.sample(BATCH_SIZE)

    #Build a batch tensor
    batch_transition=Transition(*zip(*batch))
    batch_state=torch.cat(batch_transition.state,0)
    batch_action=torch.cat(batch_transition.action,0)
    batch_reward=torch.cat(batch_transition.reward,0)

    #Calculate which states were final
    non_final_states=[s for s in batch_transition.next_state if s is not None]
    if not non_final_states:
        return
    non_final_mask=[ns!=None for ns in batch_transition.next_state]
    non_final_states=torch.cat(non_final_states)

    # For those that are not final we calculate the value through the Bellman equation 
    # we are trying to estimate the Q function through a network

    q_state_action_values=batch_reward.clone().view(-1)
    with torch.no_grad():
       pred=target_agent_ai(non_final_states).max(1).values.view(-1)
       q_state_action_values[non_final_mask]+=GAMMA*pred

    
    # We then retrieve the predicted value for the state-action pair
    state_action_values=agent_ai(batch_state).gather(1,batch_action).view(-1)

    # Based on that and the q state-action values we backpropagate on the network
    optimizer.zero_grad()
    loss=criterion(state_action_values, q_state_action_values)
    loss.backward()

    optimizer.step()

    # To stabilize the training a possible trick is to "blend" between two networks to make a so-called soft update
    # the first Agent AI is trained, the second, Target Agent AI is used to estimate the Q values
    
    agent_dict=agent_ai.state_dict()
    target_dict=target_agent_ai.state_dict()
    for k in agent_dict.keys():
        target_dict[k]=target_dict[k]*ALPHA + agent_dict[k]*(1-ALPHA)
    target_agent_ai.load_state_dict(target_dict)
    #if((steps_done+1)%100==0):
        #target_agent_ai.load_state_dict(agent_ai.state_dict())



def select_action(state, training):
    global steps_done
    eps_threshold=((EPS_DECAY-steps_done)/EPS_DECAY)*EPS_START

    steps_done+=1
    # if not training:
    #     print(agent_ai(state).tolist())
    if(random.random()<eps_threshold and training):

        return torch.tensor(random.randint(0,3), device=torch.device('cuda'), dtype=torch.int64)
    else:
        with torch.no_grad():
            return agent_ai(state).max(1).indices
    