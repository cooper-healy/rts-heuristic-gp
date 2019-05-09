from random import sample, randrange
from copy import deepcopy
from statistics import mean
from math import floor, ceil
from Tree import Individual, Node
from Task import Problem

K_CONST = 10
MAX_EVALUATIONS = 2000
MIN_DELTA = 0.001
RUNS = 30


class GP:
    def __init__(self, population_size=1000, children_size=20, mutation=0.05, parsimony = 0.5):
        # dummy population representation
        self.population = []
        for _ in range(floor(population_size/2)):
            individual = Individual(parsimony)
            individual.grow(3)
            self.population.append(individual)
        for _ in range(ceil(population_size/2)):
            individual = Individual(parsimony)
            individual.full(3)
            self.population.append(individual)
        self.parents = []
        self.population_size = population_size
        self.children = []
        self.children_size = children_size
        self.mutation = mutation
        self.evaluations = 0
        self.parsimony = parsimony

    def parentSelection(self):
        # K-tournament
        self.parents = []
        for _ in range(self.children_size):
            self.parents.append(max(sample(self.population, K_CONST)))

    def childGeneration(self):
        self.children = []
        for i in range(self.children_size):
            if randrange(0, 1) < self.mutation:
                random_tree = Individual(self.parsimony)
                random_tree.root.grow(3)
                parent_copy = deepcopy(self.parents[i])
                parent_copy.stats = []
                parent_copy.root.choose_node(True, random_tree.root)
                self.children.append(parent_copy)
            else:
                parent_copy = deepcopy(self.parents[i]).recombine(self.parents[i+1%self.children_size])
                parent_copy.stats = []
                self.children.append(parent_copy)

    def reintroduction(self):
        self.population += self.children
        self.children = []

    def survivalSelection(self):
        # K-tournament
        new_pop = []
        for _ in range(self.population_size):
            chosen = max(sample(self.population, K_CONST))
            new_pop.append(chosen)
            self.population.remove(chosen)
        self.population = new_pop

    def evaluate(self, problems):
        for individual in self.children:
            individual.evaluate(problems)
            self.evaluations += 1

    def not_finished(self, delta):
        return self.evaluations <= MAX_EVALUATIONS #self.evaluations >= MAX_EVALUATIONS or delta <= MIN_DELTA

    def run(self, problems):
        bests = []
        generations = ceil((MAX_EVALUATIONS - self.population_size)/self.children_size)+2
        data_best = [[] for i in range(generations)]  # preallocate statistics arrays
        data_avg = [[] for i in range(generations)]
        for run in range(RUNS):
            self.__init__()
            delta = 0
            last_avg = 0
            # initial evaluation
            self.children = self.population
            self.evaluate(problems)
            self.population = self.children
            # end init
            fitness_data = [i.fitness for i in self.population]
            data_best[0].append(max(fitness_data))
            data_avg[0].append(mean(fitness_data))
            generation = 1
            while self.not_finished(delta):
                self.parentSelection()
                self.childGeneration()
                self.evaluate(problems)  # update fitness
                self.reintroduction()  # reintroduce children to population
                self.survivalSelection()
                # setting loop variables
                # avg = mean([i.fitness for i in self.population])
                # delta = avg - last_avg
                # last_avg = avg
                # print('\tevaluations: {}'.format(self.evaluations))
                fitness_data = [i.fitness for i in self.population]
                # print('Max Generations: {}\tGeneration: {}'.format(generations, generation))
                data_best[generation].append(max(fitness_data))
                data_avg[generation].append(mean(fitness_data))
                generation += 1
            print('==== RUN {} ===='.format(run))
            current_best = max(self.population)
            print('best: {}\nheuristic: {}'.format(
                current_best.fitness, current_best.root.string()))
            print('stats: {}'.format(current_best.stats))
            bests.append(current_best)
        print('==== GLOBAL OPTIMUM ====')
        best = max(bests)
        print('best: {}\nheuristic: {}'.format(best.fitness, best.root.string()))
        print('stats: {}'.format(best.stats))
        # print(data_avg)


# Helper Functions

def pairwise(iterable):
    's -> (s0, s1), (s2, s3), (s4, s5), ...'
    a = iter(iterable)
    return zip(a, a)
