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

class ConnectionDistributionCollection(dict):
    '''Container that organizes connection components for a simulation, to reduce redundancy.
    
    In a simulation, connections that share the same weights and probabilities,
    as well as the same target bin edges, can make use of the same flux_matrix
    and threshold_flux_vector.  This can significantly improve the overall
    memory efficiency of the simulation. To facilitate this, each simulation
    creates a ConnectionDistributionCollection object that indexes the
    ConnectionDistribution objects according to their signature, and re-uses the
    for multiple connections.
    '''

    def add_connection_distribution(self, cd):
        '''Try and add a ConnectionDistribution object, if signature not already used.'''
        
        if not cd.signature in self.keys():
            self[cd.signature] = cd