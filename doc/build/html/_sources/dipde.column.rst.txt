.. _ref-column:

Cortical Column Model
=========================

:download:`Download potjans_diesmann_cortical_column.py <../dipde/examples/potjans_diesmann_cortical_column.py>`

Potjans and Diesmann [#]_ parameterized a four-layer, two cell-type (i.e excitatory and inhibitory) model of a cortical column. 
Beginning with their detailed model description, we implemented a version of their model using dipde. 
The population statistic approach lends itself to quickly analyzing the mean response properties of population-scale firing-rate dynamics of neural models.  

Model Output at steady-state:

.. image:: cortical_column.png
	:width: 45%
	:align: center

.. [#] Potjans T.C., & Diesmann, M. (2014) The cell-type specific cortical microcircuit: relating structure and activity in a full-scale spiking network model. *Cerebral Cortex* 24: 785–806.	    
	    