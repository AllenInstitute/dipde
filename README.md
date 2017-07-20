[![Build Status](https://travis-ci.org/AllenInstitute/dipde.svg?branch=master)](https://travis-ci.org/AllenInstitute/dipde)

[![Documentation Status](https://readthedocs.org/projects/dipde/badge/?version=latest)](http://dipde.readthedocs.io/en/latest/?badge=latest)

[![Gitter chat](https://badges.gitter.im/dipde/gitter.png)](https://gitter.im/dipde/Lobby) 

[![Anaconda-Server Badge](https://anaconda.org/nicholasc/dipde/badges/installer/conda.svg)](https://conda.anaconda.org/nicholasc)

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

DiPDE (dipde) is a simulation platform for numerically solving the time evolution of coupled networks of neuronal populations.
Instead of solving the subthreshold dynamics of individual model leaky-integrate-and-fire (LIF) neurons, dipde models the voltage distribution of a population of neurons with a single population density equation.
In this way, dipde can facilitate the fast exploration of mesoscale (population-level) network topologies, where large populations of neurons are treated as homogeneous with random fine-scale connectivity.
