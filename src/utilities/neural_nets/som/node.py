import random
import math

from utilities.neural_nets.som.vector import SOMVector

class SOMNode():
    def __init__(self, feature_count, x, y, names):
        self.bmu_count = 0
        self.error = float(0)
        self.x = x
        self.y = y
        self.associates = []    
        self.names = names
        self.feature_vector = SOMVector(0, [])
        
        for _ in range(0, feature_count):
            self.feature_vector.weights.append(random.random())
                        
    def distance_to(self, compare):
        return math.pow(self.x - compare.x, 2) + math.pow(self.y - compare.y, 2)
    
    def adjust_weights(self, input_vector, learning_rate, distance_falloff):
        for i in range(0, len(self.feature_vector.weights)):
            feature_weight = self.feature_vector.weights[i]
            input_weight = input_vector.weights[i]
            
            feature_weight += distance_falloff * learning_rate * (input_weight - feature_weight);
            self.feature_vector.weights[i] = feature_weight
            
    def encode_json(self):
        return {'vector': self.feature_vector.encode_json(),
                'x': self.x,
                'y': self.y,
                'error': self.error,
                'bmu_count': self.bmu_count,
                'associates': map(lambda a: {'associated_object': a['associated_object'].encode_json(),
                                             'error': a['error']}, self.associates)}
        
            