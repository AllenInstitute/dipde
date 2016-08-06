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
import numpy.linalg as npla
import scipy.integrate as spint
import scipy.optimize as spsol
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection

'Returns list of amplitudes for all positive inputs into the ith population'
def get_positive_inputs(i, ampDistInt, ampDistExt):
    positives = []
    for j in range(0, ampDistInt.shape[1]):
        if (ampDistInt[i,j] > 0):
            positives.append(ampDistInt[i,j])
    for j in range(0, ampDistExt.shape[1]):
        if (ampDistExt[i, j] > 0):
            positives.append(ampDistExt[i, j])
    return positives


'Returns list of tuples of amplitude + firing rate pairs for all inputs into the ith population'
def get_all_inputs(i, ampDistInt, firingRateInt, ampDistExt, firingRateExt, nsynInt, nsynExt):
    inputs = []
    for j in range(0, ampDistInt.shape[1]):
        if (ampDistInt[i, j] != 0):
            tup = (ampDistInt[i,j], firingRateInt[j]*nsynInt[i,j])
            inputs.append(tup)
    for j in range(0, ampDistExt.shape[1]):
        if (ampDistExt[i, j] != 0):
            tup = (ampDistExt[i, j], firingRateExt[j]*nsynExt[i,j])
            inputs.append(tup)
    return inputs


'Main program'
def get_firing_rates(firingRateExt, ampDistInt, ampDistExt, tau, vth, nsynInt, nsynExt):
    'f factory takes a list of amplitude-firing rate tuples and contructs a function to be integrated with'
    'Generates integrating functions f_ij, which are coefficients for the jth component of the ith firing rate'
    def f_factory(ampRate, positiveInput):
        def f(x):
            prod = 1.0
            prod *= (tau / x)
            for i in range(0, len(ampRate)):
                amp = ampRate[i][0]
                rate = ampRate[i][1]
                if (x <= 1 / amp):
                    ci = (1. - amp * x) ** (tau * rate)
                else:
                    ci = np.cos(tau * rate * np.pi) * (np.abs(1. - amp * x) ** (tau * rate))
                prod *= ci
            cn = np.exp(vth * x) / (1.0 - positiveInput * x) - 1.0
            prod *= cn
            return prod
        return f

    'for a given internal firing rate, constructs integrating functions and solves for internal firing rate'
    def consistency_eq(firingRateExt, ampDistInt, ampDistExt, firingRateInt, i, nsynInt, nsynExt):
        allInputs = get_all_inputs(i, ampDistInt, firingRateInt, ampDistExt, firingRateExt, nsynInt, nsynExt)
        positiveInputs = get_positive_inputs(i, ampDistInt, ampDistExt)
        # Remove duplicate amplitudes and sort them in decreasing order
        positiveInputs = sorted(list(set(positiveInputs)), reverse=True)
        funclist = []
        for j in range(0, len(positiveInputs)):
            funclist.append(f_factory(allInputs, positiveInputs[j]))
        # make matrix of integrated fj to multiply with various firing rate subcomponents
        A = np.zeros((len(positiveInputs), len(positiveInputs)))
        # Fill out first row of matrix with zero as the lower limit
        for j in range(0, len(positiveInputs)):
            A[0, j] = spint.quad(funclist[j], 0, 1./positiveInputs[0])[0]
        # Fill out pth row of matrix with 1/positiveInput[p-1] as lower limit and 1/positiveInput[p] as upper
        for p in range(1, len(positiveInputs)):
            for j in range(0, len(positiveInputs)):
                A[p, j] = spint.quad(funclist[j], 1./positiveInputs[p-1], 1./positiveInputs[p])[0]
        b = np.zeros((len(positiveInputs), 1))
        b[0,0] = 1
        print (A, i)
        x = npla.solve(A, b)
        return x.sum()
    def zero_func(rates):
        vec = []
        for i in range(0, len(rates)):
            vec.append(rates[i] - consistency_eq(firingRateExt,ampDistInt,ampDistExt,rates,i, nsynInt, nsynExt))
        return vec
    x0 = np.ones(ampDistInt.shape[0])
#    x0 = [.5, 2.5, 12, 10, 7, 5, 3.5, 12]
    rates = spsol.root(zero_func, x0)
    return rates.x

# ampDistExt = np.array([[.001, .00196]])
# firingRateExt = np.array([1000, 50])
# ampDistInt = np.array([[0]])

def predict(network):
    internalList = []
    externalList = []
    internalConnections = []
    externalConnections = []
    for p in network.population_list:
        if isinstance(p, InternalPopulation):
            internalList.append(p)
        if isinstance(p, ExternalPopulation):
            externalList.append(p)
    for c in network.connection_list:
        p = c.source_gid_or_population
        if isinstance(p, ExternalPopulation):
            externalConnections.append(c)
        if isinstance(p, InternalPopulation):
            internalConnections.append(c)
    print len(internalList)
    print len(externalList)
    pop_to_ind_ext = {}
    for ii, p in enumerate(externalList):
        pop_to_ind_ext[p] = ii
    pop_to_ind_int = {}
    for ii, p in enumerate(internalList):
        pop_to_ind_int[p] = ii
    # tau = .01
    # vth = .015
    tau = internalList[0].tau_m.mean()
    vth = internalList[0].v_max
    ampDistInt = np.zeros((len(internalList),len(internalList)))
    ampDistExt = np.zeros((len(internalList), len(externalList)))
    nsynInt = np.zeros((len(internalList), len(internalList)))
    nsynExt = np.zeros((len(internalList), len(externalList)))
    firingRateExt = np.zeros((len(externalList)))
    for p in externalList:
        j = pop_to_ind_ext[p]
        firingRateExt[j] = p.firing_rate_record[len(p.firing_rate_record) - 1]
    for c in internalConnections:
        j = pop_to_ind_int[c.source_gid_or_population]
        i = pop_to_ind_int[c.target_gid_or_population]
        nsynInt[i, j] = c.nsyn
        amp = c.synaptic_weight_distribution.mean()
        ampDistInt[i, j] = amp
    for c in externalConnections:
        j = pop_to_ind_ext[c.source_gid_or_population]
        i = pop_to_ind_int[c.target_gid_or_population]
        nsynExt[i, j] = c.nsyn
        amp = c.synaptic_weight_distribution.mean()
        ampDistExt[i, j] = amp
    print ampDistExt
    print firingRateExt
    print ampDistInt
    print nsynInt
    print nsynExt
    rates = get_firing_rates(firingRateExt, ampDistInt, ampDistExt, tau, vth, nsynInt, nsynExt)
    return rates
    # print rates
    # for p in internalList:

#        print 'predicted for layer ' + str(p.metadata['layer']) + ' cell type ' + p.metadata['celltype']
#         print 'predicted for element ' + str(pop_to_ind_int[p])
#         print rates[pop_to_ind_int[p]]
#         print 'simulation result: '
#         print p.firing_rate_record[len(p.firing_rate_record) - 1]

#Case 2: Reccurence with nysn
# tau = .02
# vth = .02
# ampDistExt = np.array([[.002, 0], [0, .002]])
# ampDistInt = np.array   ([[.002, -.002], [.002, -.002]])
# firingRateExt = np.array([150.0, 200.0])
# nsynInt = np.array([[20.0, 1.0], [30.0, 1.0]])
# nsynExt = np.array([[1.0, 0], [0, 1.0]])
# get_firing_rates(firingRateExt, ampDistInt, ampDistExt, tau, vth, nsynInt, nsynExt)

#Dipde1:
#   Exact:
#     Rate1:       0.732185936565
#     Rate2:       1.99372726136
#   Approx(0=1):
#     Did not converge
#Output of Exponential Solver:

#     Rate1:       0.73456822
#     Rate2:       2.0246198

#case3: Recurrence with nsyn
#   Exact:
#       [ 1.2660087 ,  3.59118034]
#   Dipde1:
#       [1.21061840737, 3.45247506746]
