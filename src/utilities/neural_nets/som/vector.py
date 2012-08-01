import math

class SOMVector():
    """
    A simple helper class that contains an input vector.
    """
    
    def __init__(self, tag, weights):
        # Tag can be anything. Usually it's a reference to the object that belongs to this input vector
        self.tag = tag
        # The input weights to the vector
        self.weights = weights
       
    def euclidean_dist(self, compare):
        """
        Calculate the euclidian distance between this vector's input and that of the candidate BMU (best matching unit)
        
        See Equation 1 
        """
        
        # Value check
        if len(compare.weights) != len(self.weights):
            return -999
        
        summation, temp = 0, 0
        for x in range(0, len(self.weights)):
            temp = math.pow(self.weights[x] - compare.weights[x], 2)
            summation += temp
            
        return summation
        #return math.sqrt(summation) # Should we square root?     