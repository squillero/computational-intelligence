import random
from enum import Enum
import pickle

class Agent():

    class Crossover(Enum):
        RANDOM = 1
        MULTI_CUT = 2
        ONE_CUT = 3
        PARTIAL = 4

    class AgentType(Enum):
        BINARY = 1
        PATTERN = 2

    def __init__(self,genome,mutation_rate : float = None) -> None:
        self.genome = genome
        self.mutation_rate = mutation_rate
        self._id = random.randint(0, 1000000000)
        self._fitness = None
        self._hash = None
        pass

    def set_mutation_rate(self, mutation_rate : float) -> None:
        self.mutation_rate = mutation_rate

    def set_genome(self, genome) -> None:
        self.genome = genome

    def set_fitness(self, fitness) -> None:
        self._fitness = fitness

    def compute_fitness(self,fitness_function) -> None:
        if self.genome is None:
            ValueError("Genome is not set")
        self._fitness = fitness_function(self.genome)
        pass  

    def mutation(self,mutation_rate) -> None:
        """
        Checks if the genome is set and if the mutation rate is set.
        """
        
        if self.genome is None:
            ValueError("Genome is not set")
        if mutation_rate is None and self.mutation_rate is None:
            ValueError("Mutation rate is not set")
        if self.mutation_rate is not None and mutation_rate is None:
            self.mutation_rate *= [0.999,1.001][random.randint(0,1)]
        pass      

    @property
    def fitness(self):
        if self._fitness is None:
            self.compute_fitness()
        return self._fitness

    @property
    def hash(self):
        if self.genome is None:
            ValueError("Genome is not set")
        if self._hash is None:
            self._hash = hash(tuple(self.genome))
        return self._hash

    def load_agent(self, path):
        with open(path, 'rb') as f:
            self.genome = pickle.load(f)
        return self
    
    def save_agent(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.genome, f)