import random
from itertools import chain
from collections.abc import Callable
from Agent import Agent

class PatternBasedAgent(Agent):
    """
    Class representing an agent with a pattern based genome which is a list of boolean values.  
    
    The phenotype is given by a concatenation of the pattern repeated until the genome_size is filled.
    
    """
    
    def __init__(self) -> None:
        super().__init__(None,None)
        
    def set_genome(self,genome_size : int,genome : list = None) -> 'PatternBasedAgent':
        """
        Sets the genome of the agent to a random genome of size genome_size 
        ----------
        Parameters
        - genome_size (int) - The size of the genome to be set
        - genome (list) - The genome to be set (optional)

        Returns
        - PatternBasedAgent - The agent with the new genome
        """

        self.genome_size = genome_size
        self.pattern_size = random.randint(genome_size//50,genome_size//5)
        self.pattern = [random.uniform(0, 1) < 0.5 for _ in range(self.pattern_size)]
        self.generate_genome()
        return self
    
    def set_mutation_rate(self,mutation_rate : float) -> 'PatternBasedAgent':
        super().set_mutation_rate(mutation_rate)
        self._pattern_mutation_rate = min(mutation_rate * self.pattern_size / 10 , 0.2)
        return self

    
    def generate_genome(self) -> None:
        """
        Function that generates the genome from the given pattern. Must be called after each mutation of the pattern.
        """
        
        if self.pattern is None:
            ValueError("Pattern is not set")
        self.genome = list(chain.from_iterable([self.pattern for _ in range(self.genome_size//self.pattern_size + 1)])) # overshoot the size to be sure to have enough
        self.genome = self.genome[:self.genome_size]

    def mutation(self,mutation_rate : float = None) -> 'PatternBasedAgent':
        """
        Function that mutates the agent's pattern content and/or size. After the mutation, the genome is regenerated.
        ----------
        Parameters
        - mutation_rate (float) - The mutation rate to be used (optional). If not given, the agent's mutation rate is used.
        """
        
        super().mutation(mutation_rate)
        
        ###### mutate the pattern_size
        if random.random() < (self._pattern_mutation_rate if mutation_rate is None else mutation_rate * 10) :
            adding = random.choices([-1, 1], weights=[1, 2])[0]
            if adding == -1 and self.pattern_size > 1:
                self.pattern_size -= 1
                self.pattern = self.pattern[:-1]
            else:
                temp = random.choices([0, 1], k = adding)
                self.pattern_size += adding
                self.pattern += temp

        ###### mutate the pattern
        for (i,state) in enumerate(self.pattern):
            if random.random() < (mutation_rate if mutation_rate is not None else self.mutation_rate) :
                self.pattern[i] = not state
        self.generate_genome()
        return self

    def __repr__(self) -> str:
        return f"AgentGA({self._id},{self.fitness}) with pattern {self.pattern}"

    def crossover(self,other : 'PatternBasedAgent',crossover_type : Agent.Crossover = 1,other_weight = 0.5) -> 'PatternBasedAgent':
        """
        Implements a crossover between self and an other Agent (of the same type)  
        Parameters
        - other (PatternBasedAgent) - The other agent to be crossed over with
        - crossover_type (Agent.Crossover) - The type of crossover to be used
        - other_weight (float) - The weight of the other agent in the crossover (only used for random crossover)

        Returns
        - PatternBasedAgent - The crossed over agent
        """
        match crossover_type:
            case Agent.Crossover.RANDOM:
                self.random_crossover(other,other_weight)
            case Agent.Crossover.MULTI_CUT:
                self.multi_cut_crossover(other)
            case Agent.Crossover.ONE_CUT:
                self.one_cut_crossover(other)
            case Agent.Crossover.PARTIAL:
                self.partial_crossover(other)
            case _:
                raise ValueError("Unknown crossover type")
        self.generate_genome()
        return self

    def random_crossover(self,other : 'PatternBasedAgent',other_weight = 0.5) -> 'PatternBasedAgent':
        """ Implements a random crossover between self and an other Agent (of the same type)  
        ----------
        Parameters
        - other (PatternBasedAgent) - The other agent to be crossed over with
        - other_weight (float) - The weight of the other agent in the crossover

        Returns
        - PatternBasedAgent - The crossed over agent
        """

        offset = self.pattern_size - other.pattern_size
        if offset > 0:
            temp = random.randint(0,offset)
            for (i,_) in enumerate(other.pattern):
                self.pattern[i + temp] = random.choices([self.pattern[i + temp],other.pattern[i]],weights=[1-other_weight,other_weight])[0]
        else:
            temp = random.randint(0,abs(offset))
            for (i,_) in enumerate(self.pattern):
                self.pattern[i] = random.choices([self.genome[i],other.genome[i + temp]],weights=[1-other_weight,other_weight])[0]
        return self
    
    def multi_cut_crossover(self,other : 'PatternBasedAgent') -> 'PatternBasedAgent':
        """ Implements a multi cut crossover between self and an other Agent (of the same type)
        ----------
        Parameters
        - other (PatternBasedAgent) - The other agent to be crossed over with

        Returns
        - PatternBasedAgent - The crossed over agent
        """

        for _ in range(random.randint(0, (min(self.pattern_size , other.pattern_size) - 1)//2)):
            n = random.randint(0, min(self.pattern_size , other.pattern_size) - 1)
            m = random.randint(0, min(self.pattern_size , other.pattern_size) - 1)
            if n > m:
                n,m = m,n
            self.pattern[n:m] = other.pattern[n:m]
        return self

    def one_cut_crossover(self, other: 'PatternBasedAgent') -> 'PatternBasedAgent':
        """ Implements a one cut crossover between self and an other Agent (of the same type)
        ----------
        Parameters
        - other (PatternBasedAgent) - The other agent to be crossed over with

        Returns
        - PatternBasedAgent - The crossed over agent
        """

        min_length = min(self.pattern_size, other.pattern_size)
        n = random.randint(0, min_length - 1)

        self.pattern[:min_length-n] = other.pattern[:min_length-n]
    
    def partial_crossover(self, other: 'PatternBasedAgent') -> 'PatternBasedAgent':
        """ Performs a one-cut crossover between itself and another agent (of the same type). Only an "inner" part of the pattern is taken.
        ----------
        Parameters
        - other (PatternBasedAgent) - The other agent to be crossed over with

        Returns
        - PatternBasedAgent - The crossed over agent
        """
        
        min_length = min(self.pattern_size, other.pattern_size)
        n = random.randint(0, min_length - 1)
        m = random.randint(0, min_length - 1)

        if n > m:
            n, m = m, n

        self.pattern[n:m] = other.pattern[n:m]
        return self

    def compute_fitness(self,fitness_function : Callable) -> None:
        super().compute_fitness(fitness_function)
    
    @property
    def fitness(self):
        return self._fitness