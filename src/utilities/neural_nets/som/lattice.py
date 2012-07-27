import random

from utilities.neural_nets.som.node import SOMNode

class SOMLattice():
    
    def __init__(self, width, height, feature_count, names, gradient=False):
        self.feature_count = feature_count
        self.nodes = []
        self.width = width
        self.height = width
        self.gradient = gradient
        self.names = names
        
        xstep = float(0.5) / float(width)
        ystep = float(0.5) / float(width)
        
        print xstep, ystep
        
        self.matrix = []
        
        for x in range(0, width):
            self.matrix.append([])
            
            for y in range(0, height):
                print x, y
                node = SOMNode(feature_count, x, y, names)                
                
                for _ in range(0, feature_count):
                    if gradient:
                        node.weights.append(int(255 * ((xstep * x) + (ystep * y))))
                    else:
                        node.weights.append(int(random.uniform(0,256)))                                             
                        
                    for i in self.matrix:
                        for j in i:
                            self.nodes.append(j)
                    
                self.matrix[x].append(node)
                self.nodes.append(node)                
                
    def encode_json(self):
        return {'feature_count': self.feature_count,
                'nodes': [n.encode_json() for n in self.nodes],
                'height': self.height,
                'width': self.width}
        
    def clone(self):
        result = SOMLattice(self.width, self.height, self.feature_count)
        
        for x in range(0, result.width):
            for y in range(0, result.height):
                for i in range(0, result.feature_count):
                    result.get_node(x, y)[i] = self.get_node(x, y)[i]
                    
        return result
                    
    def get_node(self, x, y):
        return self.matrix[x][y]
    
    def get_bmu(self, input_vector):
        bmu = self.matrix[0][0]
        
        best_dist = input_vector.euclidean_dist(bmu.feature_vector)
        cur_dist = float(0)
        
        for x in range(0, self.width):
            for y in range(0, self.height):
                cur_dist = input_vector.euclidean_dist(self.matrix[x][y].feature_vector)
                
                if cur_dist < best_dist:
                    bmu = self.matrix[x][y]
                    best_dist = cur_dist
        
        return bmu, best_dist