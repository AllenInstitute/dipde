import numpy as np
from dipde.internals import utilities as util

class ConnectionDistribution(object):
    
    def __init__(self, edges, weights, probs, reversal_potential=None, sparse=True):
        
        # Assign inputs:
        self.edges = edges
        self.weights = weights
        self.probs = probs
        self.reversal_potential = reversal_potential
        self.initialized = False
        
        # Not implemented yet
        if reversal_potential != None:
            assert NotImplementedError  # pragma: no cover
        
        # Must be probabilty distribution
        assert np.sum(probs) == 1.
        
        # Defined in initialization:
        self.threshold_flux_vector = None
        self.flux_matrix = None
        
    def initialize(self):
        
        nv = len(self.edges)-1
        self.flux_matrix = np.zeros((nv, nv))
        self.threshold_flux_vector = np.zeros(nv)
        for curr_weight, curr_prob in zip(self.weights, self.probs):
            curr_threshold_flux_vector, curr_flux_matrix = util.flux_matrix(self.edges, curr_weight, curr_prob)
            self.flux_matrix += curr_flux_matrix
            self.threshold_flux_vector += curr_threshold_flux_vector

        # Guarantee zero flux:
        np.testing.assert_almost_equal(np.abs(np.sum(self.flux_matrix, axis=0)).sum(), 0, 12)
        
    @property
    def signature(self):
        
        return (tuple(self.edges), 
                tuple(self.weights),
                tuple(self.probs), 
                self.reversal_potential)
    
 
    

