"""Module containing ConnectionDistribution class, organizing connection details."""

import numpy as np
from dipde.internals import utilities as util

class ConnectionDistribution(object):
    '''Container for matrix that computes element flux, and associated methods.
    
    A ConnectionDistribution object contains a matrix used to compute the time
    propogation of the voltage probability distribution, and a vector used to
    compute the flux over threshold at the end of the timestep. It is unique up
    to the descretization of the target voltage distribution, and the specific
    synaptic weight distribution of the connection.  Therefore, whenever
    possible, a ConnectionDistribution object is reused for multiple connections
    with identical signatures, to reduce memory consumption.
    
    Attributes:
        edges: voltage descretization of target population (np.ndarray)
        
         weights: weights defining synaptic distribution (np.ndarray)

         probs: probabilities corresponding to weights (np.ndarray)
         
         threshold_flux_vector: vector used to compute over-threshold flux (np.ndarray)
         
         flux_matrix: matrix used to propagate voltage distribution
    '''
    
    def __init__(self, edges, weights, probs, reversal_potential=None, sparse=True):
        
        # Assign inputs:
        self.edges = edges
        self.weights = weights
        self.probs = probs
        self.reversal_potential = reversal_potential
        
        # Not implemented yet
        if reversal_potential != None:
            assert NotImplementedError  # pragma: no cover
        
        # Must be probabilty distribution
        assert np.sum(probs) == 1.
        
        # Defined at runtime:
        self.threshold_flux_vector = None
        self.flux_matrix = None
        
    def initialize(self):
        """Initialize connection distribution.

        Initialization creates the flux_matrix and threshold_flux_vector.
        Implemented lazily via a try catch when flux matrix is requested, that
        does not exist.
        """
        
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
        """A unique key used to organize ConnectionDistributions."""
        
        return (tuple(self.edges), 
                tuple(self.weights),
                tuple(self.probs), 
                self.reversal_potential)
    
 
    

