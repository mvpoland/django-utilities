import random
import math

from utilities.neural_nets.som.vector import SOMVector

class SOMNode():
    """
    This class represents one of the many neurons in a neural net.
    """
    
    def __init__(self, feature_count, x, y):
        self.bmu_count = 0  # How many times has this node been BMU
        self.x = x # X - coord in a 2-dimensional representation of the lattice
        self.y = y # Y - coord in a 2-dimensional representation of the lattice
        self.associates = [] # input vectors that are associated to this node            
        self.feature_vector = SOMVector(0, []) # The node's weight vector
        
        # Initialize the weights of the feature vector with numbers between 0 and 1
        for _ in range(0, feature_count):
            self.feature_vector.weights.append(random.random())
                        
    def distance_to(self, compare):
        """
        Calculate the distance between this node and a comparison node
        """
        return math.pow(self.x - compare.x, 2) + math.pow(self.y - compare.y, 2)
    
    def adjust_weights(self, input_vector, learning_rate, distance_from_bmu):
        """
        Adjust the weights of the feature vector using the current input, learning rate and distance from BMU
        """
        
        # Loop over the weights and adjust
        for i in range(0, len(self.feature_vector.weights)):
            feature_weight = self.feature_vector.weights[i]
            input_weight = input_vector.weights[i]
            
            # See formula 3a
            feature_weight += distance_from_bmu * learning_rate * (input_weight - feature_weight);
            
            self.feature_vector.weights[i] = feature_weight