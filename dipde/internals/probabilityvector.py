import bisect
import numpy as np
import simulation

class ProbabilityVector(object):
    
    def __init__(self, edges, zero_bin=False):
        
        self.edges = edges
        if zero_bin == True:
            self.zero_index = bisect.bisect_left(self.edges, 0) - 1
        
        self.pv_list = [np.zeros(len(self.edges)-1).astype(simulation.precision), np.zeros(len(self.edges)-1).astype(simulation.precision)]
        self.p0i = 0
        
    @property
    def p0(self):
        return self.pv_list[self.p0i]
    
    @property
    def p1(self):
        return self.pv_list[1-self.p0i]
    
    @property
    def p1i(self):
        return 1-self.p0i
    
    @property
    def len_edge_vec(self):
        return len(self.edges)
    
    @property
    def len_prob_vec(self):
        return len(self.p0)
    
    def swap(self):
        self.p0i = 1- self.p0i
        
        
# edges = [-2,-1,1,2,4]
# pv = ProbabilityVector(edges, zero_bin=True)
# 
# pv.p0[1] = 1
# pv.swap()
# print pv.p0, pv.p1