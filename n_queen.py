import random
from time import time
from itertools import combinations
import math
import os
import sys
import pygame

clear = lambda: os.system('clear') if sys.platform.startswith('linux') else os.system('cls')

class Queen:
    MUTATION_PROBABILITY = 0.05
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    DISPLAY_SIZE = (1360, 1000)
    BLOCK_SIZE = 30
    QUEEN_THUMB = 'images/queen.png'

    def __init__(self, N: int , population_size: int = 4, threshold: int = 15):
        self.N = N
        self.population_size = population_size
        self.threshold = threshold
        self.maximum_conflict = self.ncr(N, 2)
        self.current_solutions = self.generateRandomSolution(population_size)
        self.initdisplay()

    def drawChessBoard(self):
        xp = 0
        xy = -1
        gameDisplay = self.board_window
        size = self.BLOCK_SIZE
        boardLength = self.N
        queenimage = pygame.image.load(self.QUEEN_THUMB)
        queenimage = pygame.transform.scale(queenimage, (size, size))
        no_board = len(self.current_solutions)
        for j in range(no_board):
            cnt = 0
            if xp % 4 == 0:
                xy += 1
                xp = 0            
            for i in range(1,self.N+1):
                for z in range(1,self.N+1):         
                    #check if current loop value is even
                    if cnt % 2 == 0:
                        pygame.draw.rect(gameDisplay, self.BLACK,[size*z+(xp*(size*boardLength+50)),size*i+(xy*(size*boardLength+50)),size,size])
                    else:
                        pygame.draw.rect(gameDisplay, self.RED, [size*z+(xp*(size*boardLength+50)),size*i+(xy*(size*boardLength+50)),size,size])
                    cnt +=1          
                    if self.current_solutions[j][z-1] == i:
                        gameDisplay.blit(queenimage, [size*z+(xp*(size*boardLength+50)),size*i+(xy*(size*boardLength+50)), 10, 10])
          
                #since theres an even number of squares go back one value
                if boardLength % 2 == 0:
                    cnt-=1
                
                #Add a nice boarder
                pygame.draw.rect(gameDisplay,self.BLACK,[size*z+(xp*(size*boardLength+50)),size*i+(xy*(size*boardLength+50)),size,size],3)

            # print the fitness
            monaco_font = pygame.font.SysFont('monaco', 24)
            f_ = self.fitness(self.current_solutions[j])
            if f_ == self.maximum_conflict:
                fitness_text = monaco_font.render(f'{f_}', True, self.RED)
            else:
                fitness_text = monaco_font.render(f'{f_}', True, self.BLACK)
            fitness_text_rect = fitness_text.get_rect()
            fitness_text_rect.midtop = ((size * self.N * xp) + (size * (xp + 1) * (self.N // 2 + 1)) - (xp * 2 * size), (size * (xy + 1) * self.N) + (50 * (xy + 1)) )
            self.board_window.blit(fitness_text, fitness_text_rect)
            xp += 1

    def updateWindow(self):
        self.board_window.fill(self.WHITE)
        self.drawChessBoard()
        pygame.display.flip()
        self.fpsController.tick(15)

    def initdisplay(self):
        pygame.init()
        pygame.font.init()
        self.board_window = pygame.display.set_mode(self.DISPLAY_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption('Chessboard')
        self.board_window.fill(self.WHITE)
        self.fpsController = pygame.time.Clock()

    def findsolution(self):
        iteration = 1
        startime = time()
        current_fitnesses = self.getFitness()
        while True:
            (solutionFound, solution) = self.checkFitness(current_fitnesses)
            print(f'Iteration # {iteration}:')
            if solutionFound:
                self.finishSimulation()
                break
            print(f'Current Number of candidate: {len(self.current_solutions)}')
            for (sol, fitness) in zip(self.current_solutions, current_fitnesses):
                print(f'{sol} fitness: {fitness}')
            self.naturalselection()
            print(f'After natural selection # of candidate: {len(self.current_solutions)}')
            self.crossover()
            current_fitnesses = self.getFitness()
            print(f'After crossover # of candidate: {len(self.current_solutions)}')
            for (sol, fitness) in zip(self.current_solutions, current_fitnesses):
                print(f'{sol} fitness: {fitness}')
            iteration += 1
            print(f'Max fitness: {max(current_fitnesses)}')
            print()
            self.updateWindow()
        print(f'Time required: {time() - startime}s')
        input('Press any key to continue')

    def finishSimulation(self):
        print('Solution found')
        for (sol, fitness) in zip(self.current_solutions, self.getFitness()):
            print(f'{sol} : {fitness} ', end='')
            if fitness == self.maximum_conflict:
                print(' # Solution')
            else:
                print()
        pass

    def checkFitness(self, fitness_array):
        if self.maximum_conflict in fitness_array:
            return (True, self.current_solutions[fitness_array.index(self.maximum_conflict)])
        else:
            return (False, [])

    def getFitness(self):
        return [self.fitness(x) for x in self.current_solutions]

    def fitness (self, arr):
        count = 0
        for i in range(len(arr)):
            for j in range(i+1, len(arr)):
                if math.fabs(arr[i] - arr[j]) == j - i or arr[i] == arr[j]:
                    count += 1
        return self.maximum_conflict - count
    
    def generateRandomSolution(self, n_solution):
        return [self.randomsolution() for i in range(n_solution)]

    def randomsolution(self):
        return [random.randint(1, self.N) for x in range(self.N)]

    def crossover(self):
        random_parents = self.getrandomcouples()
        crossed_childs = self.cross(random_parents)
        self.current_solutions += crossed_childs
        if len(self.current_solutions) < self.population_size:
            self.current_solutions += self.generateRandomSolution(self.population_size - len(self.current_solutions))

    def mutate(self, sol):
        n = random.randint(0, len(sol) - 1)
        val = random.randint(1, self.N)
        sol[n] = val
        return sol
    
    def cross(self, parents):
        new_generation = []
        for (p1, p2) in parents:
            children = self.reproduce(p1, p2)
            new_generation = new_generation + children
        return new_generation

    def reproduce(self, parent1, parent2):
        break_point = random.randint(0, len(parent1) - 1)
        parent_length = len(parent1)
        child_1 = parent1[0: break_point] + parent2[break_point: parent_length]
        if random.random() < self.MUTATION_PROBABILITY:
            child_1 = self.mutate(child_1)
        child_2 = parent2[0: break_point] + parent1[break_point: parent_length]
        if random.random() < self.MUTATION_PROBABILITY:
            child_2 = self.mutate(child_2)
        return [child_1, child_2]

    def getrandomcouples(self):
        number_couple = self.population_size // 2      
        couples = []
        for i in range(number_couple):
            all_couples = list(combinations(self.current_solutions, 2))
            if len(all_couples) == 0:
                break
            random_selection = random.randint(0, len(all_couples)-1)
            chosen_couple = all_couples[random_selection]
            # removing the chosen solutions from current solutions 
            self.removeSolution(chosen_couple[0])
            self.removeSolution(chosen_couple[1])
            
            couples.append(chosen_couple)
        return couples

    def removeSolution(self, sol):
        index_sol = self.current_solutions.index(sol)
        solution_current_length = len(self.current_solutions)
        self.current_solutions = self.current_solutions[0 : index_sol] + self.current_solutions[index_sol + 1: solution_current_length]

    def naturalselection(self):
        # only keep the solution that matches the minimum fitness threshold
        self.current_solutions = [x for x in self.current_solutions if self.fitness(x) >= self.threshold]
        if len(self.current_solutions) == 0:
            self.current_solutions = self.generateRandomSolution(self.population_size)

    def ncr(self, n, r):
        def fact(n):
            res = 1
            for i in range(2, n + 1):
                res = res * i
            return res
        return (fact(n) // (fact(r) * fact(n - r)))

if __name__ == '__main__':
    solver = Queen(6, 10)
    solver.findsolution()