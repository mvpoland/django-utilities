import math

from threading import Thread

START_LEARNING_RATE = 0.3
NUM_ITERATIONS = 500

class SOMTrainer():
    def __init__(self, reset=True):
        self.lattice = None
        self.inputs = None
        self.runner = None
        self.stopping = False
        self.start_rate = START_LEARNING_RATE
        self.reset = reset
        self.done_handler = None
        self.progressing_handler = None
        self.status_changed_handler = None
        self.LATTICE_RADIUS = 0
        self.TIME_CONSTANT = 0
        
    def get_neighborhood_radius(self, iteration):
        return self.LATTICE_RADIUS * math.exp(-iteration / self.TIME_CONSTANT)
    
    def get_distance_falloff(self, distsq, radius):
        return math.exp(-distsq / (2 * math.pow(radius, 2)))
    
    def register_lattice(self, lattice):
        self.lattice = lattice
        
    def __on_done(self):
        if self.done_handler:
            self.done_handler()        
            
    def __on_progressing(self, percentage):
        if self.progressing_handler:
            self.progressing_handler(percentage)
            
    def __on_status_changed(self, status):
        if self.status_changed_handler:
            self.status_changed_handler(status)
    
    def __thread(self):
        learning_rate = 0
        
        if self.reset:
            self.start_rate = START_LEARNING_RATE if START_LEARNING_RATE < 1 else 1
            learning_rate = self.start_rate
        else:
            learning_rate = self.start_rate
            
        iteration = 0
        
        try:
            lattice_width = self.lattice.width
            lattice_height = self.lattice.height
            self.LATTICE_RADIUS = (lattice_width if lattice_width > lattice_height else lattice_height) / 2
            self.TIME_CONSTANT = NUM_ITERATIONS / math.log(self.LATTICE_RADIUS)
            
            while not self.stopping and iteration < NUM_ITERATIONS:
                percentage = (float(iteration) / float(NUM_ITERATIONS)) * 100
                
                self.__on_progressing(percentage)
                
                for node in self.lattice.nodes:
                    node.associates = []
                
                nbh_radius = self.get_neighborhood_radius(iteration)
                
                for i in range(0, len(self.inputs)):
                    cur_input = self.inputs[i]                
                    
                    bmu, best_dist = self.lattice.get_bmu(cur_input)
                    
                    if cur_input.tag:
                        bmu.associates.append({'associated_object': cur_input,
                                               'error': best_dist})
                        
                    bmu.bmu_count += 1;
                    
                    xstart = int(bmu.x - nbh_radius - 1)
                    ystart = int(bmu.y - nbh_radius - 1)
                    xend = int(xstart + (nbh_radius * 2) + 1)
                    yend = int(ystart + (nbh_radius * 2) + 1)
                    
                    if lattice_width < xend:
                        xend = lattice_width
                    if 0 > xstart:
                        xstart = 0
                    
                    if lattice_height < yend:
                        yend = lattice_height
                    
                    if 0 > ystart:
                        ystart = 0       
                        
                    for x in range(xstart, xend):
                        for y in range(ystart, yend):
                            temp = self.lattice.get_node(x, y)
                            dist = bmu.distance_to(temp)
                            
                            if dist <= math.pow(nbh_radius, 2):
                                dist_falloff = self.get_distance_falloff(dist, nbh_radius)
                                temp.adjust_weights(cur_input, learning_rate, dist_falloff)
                                
                iteration += 1
                learning_rate = self.start_rate * math.exp(-float(iteration) / NUM_ITERATIONS)
                self.__on_status_changed("The SOM network is training. Learning rate: %s - Iteration: %s" % (learning_rate,
                                                                                                             iteration))
        finally:
            if self.stopping:
                self.__on_status_changed('The learning process has been cancelled.')
            else:
                self.__on_status_changed('The learning process has finished.')
                
            self.start_rate = learning_rate
            self.__on_done()
            self.__on_progressing(0)
                
                
        
    def start_training(self, inputs, reset=False):
        self.reset = reset
        self.inputs = inputs
        
        if self.lattice:
            self.stopping = False
            
            self.runner = Thread(target=self.__thread)
            self.runner.start()
            
    def stop_training(self):
        self.stopping = True                                
        
        if self.runner:
            while self.runner.isAlive():
                pass            