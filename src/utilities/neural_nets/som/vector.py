import math

class SOMVector():
    def __init__(self, tag, weights):
        self.tag = tag
        self.weights = weights
       
    def euclidean_dist(self, compare):
        if len(compare.weights) != len(self.weights):
            return -999
        
        summation, temp = 0, 0
        for x in range(0, len(self.weights)):
            temp = math.pow(self.weights[x] - compare.weights[x], 2)
            summation += temp
            
        return math.sqrt(summation)