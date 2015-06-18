"""Module containing ConnectionDistribution class, organizing connection details."""

# Copyright 2013 Allen Institute
# This file is part of dipde
# dipde is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dipde is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dipde.  If not, see <http://www.gnu.org/licenses/>.

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
    
    Parameters
    ----------
    edges: np.ndarray
        Voltage bin discretization of target population.
     weights: np.ndarray 
        Weights defining the discrete synaptic distribution. 
    probs : np.ndarray
        Probabilities corresponding to weights.
        
    Attributes
    ----------
    self.threshold_flux_vector : np.ndarray
        Vector used to compute over-threshold flux.
    self.flux_matrix : np.ndarray
        Matrix used to propagate voltage distribution.
    '''
    
    def __init__(self, edges, weights, probs, sparse=True):
        
        # Assign inputs:
        self.edges = edges
        self.weights = weights
        self.probs = probs
        
        
        # Not implemented yet
        self.reversal_potential = None
        if self.reversal_potential != None:
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
    
 
    

