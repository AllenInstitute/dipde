[![Build Status](https://travis-ci.org/AllenInstitute/dipde.svg?branch=master)](https://travis-ci.org/AllenInstitute/dipde)
[![Documentation Status](https://readthedocs.org/projects/dipde/badge/?version=latest)](http://dipde.readthedocs.io/en/latest/?badge=latest)
 

DiPDE (dipde) is a simulation platform for numerically solving the time evolution of coupled networks of neuronal populations.
Instead of solving the subthreshold dynamics of individual model leaky-integrate-and-fire (LIF) neurons, dipde models the voltage distribution of a population of neurons with a single population density equation.
In this way, dipde can facilitate the fast exploration of mesoscale (population-level) network topologies, where large populations of neurons are treated as homogeneous with random fine-scale connectivity.
