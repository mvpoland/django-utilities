import math

from threading import Thread

START_LEARNING_RATE = [0.9, 0.1]
NUM_ITERATIONS = [100, 200]

class SOMTrainer():
    def __init__(self, lattice):
        self.lattice = lattice
        self.LATTICE_RADIUS = 0
        self.TIME_CONSTANT = 0
        
    def get_neighborhood_radius(self, iteration, phase):
        """
        Calculates the new neighbourhood radius. This radius determines 
        the region where the nodes will have their weight adjusted
        
        See formula 2a
        """
        if phase == 0:
            return self.LATTICE_RADIUS * math.exp(-iteration / self.TIME_CONSTANT)
        else:
            # just BMU in phase 2
            return self.LATTICE_RADIUS
    
    def get_distance_falloff(self, distsq, radius):
        """
        Calculate the weight alteration based on the distance from the BMU and the current neigbourhood radius
        """
        
        return math.exp(-distsq / (2 * math.pow(radius, 2)))
    
    def start_training(self, inputs):        
        """
        Train the neural net
        """
        
        try:
            lattice_width = self.lattice.width
            lattice_height = self.lattice.height
            
            # 2 phases.
            # Phase 1: reduce learning rate from 0.9 to 0.1 in 100 iterations.
            # Phase 2: smooth out lattice and reduce learning rate further from 0.1 to 0.0 in 200 iterations
            for phase in range(0, 2):
                iteration = 0
                learning_rate = START_LEARNING_RATE[phase]
                
                if phase == 0:                
                    # Initially the radius is half of the diameter of the lattice
                    self.LATTICE_RADIUS = (lattice_width if lattice_width > lattice_height else lattice_height) / 2.0
                else:
                    # In phase 2 the radius is fixed to just the BMU
                    self.LATTICE_RADIUS = 1                
                
                # See forumla 2b
                self.TIME_CONSTANT = NUM_ITERATIONS[phase] / self.LATTICE_RADIUS
                
                while iteration < NUM_ITERATIONS[phase]:
                    percentage = (float(iteration) / float(NUM_ITERATIONS[phase])) * 100                    
                    
                    # Reset associated input vectors
                    for x in range(0, self.lattice.width):
                        for y in range(0, self.lattice.height):
                            self.lattice.matrix[x][y].associates = []
                    
                    # Get the neighbourhood radius for the current iteration
                    nbh_radius = self.get_neighborhood_radius(iteration, phase)
                    
                    # Loop the input vectors
                    for i in range(0, len(inputs)):
                        cur_input = inputs[i]                
                        
                        # Find the BMU for this input vector and associated it with this unit
                        bmu, best_dist = self.lattice.get_bmu(cur_input)                    
                        bmu.associates.append({'associated_object': cur_input,
                                               'error': best_dist})
                            
                        # For statistics track how many times this neuron has been BMU
                        bmu.bmu_count += 1;                    
                            
                        # Adjust weights for all nodes
                        for x in range(0, self.lattice.width):
                            for y in range(0, self.lattice.height):
                                temp = self.lattice.get_node(x, y)
                                dist = bmu.distance_to(temp)
                                
                                # Make sure the node falls within the current neighbourhood radius
                                if dist <= math.pow(nbh_radius, 2):   
                                    # Calculate the weight factor that determines the rate of adjustment.
                                    # The closer the node is to the BMU, the greater the weight                                                            
                                    dist_falloff = self.get_distance_falloff(dist, nbh_radius)
                                    
                                    # Adjust the weights of the node's feature vector
                                    temp.adjust_weights(cur_input, learning_rate, dist_falloff)
                                    
                    iteration += 1
                    learning_rate = START_LEARNING_RATE[phase] * math.exp(-float(iteration) / NUM_ITERATIONS[phase])
                    print "The SOM network is training. Learning rate: %s - Iteration: %s" % (learning_rate,
                                                                                              iteration)
        finally:
            print 'The learning process has finished.'            