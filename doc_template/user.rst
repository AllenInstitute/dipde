User Guide
==========
This guide is a resource for installing the dipde package.
It is maintained by the `Allen Institute for Brain Science <http://www.alleninstitute.org/>`_.

Quick Start Install Using Pip
-------------------------------------

 #. Pip install for a single user:
    
    .. code-block:: bash
     
    	pip install git+http://stash.corp.alleninstitute.org/scm/~nicholasc/dipde2.git --user
    	


Install Using Setup Tools
-------------------------

 #. Download the distribution.
 
    .. code-block:: bash
     
    	TODO
 
 #. Unpack the distribution.
     
    .. code-block:: bash
     
    	tar xvzf dipde-|version|.tar.gz

 #. Install using setuptools
     
    .. code-block:: bash
     
    	cd dipde-|version| python setup.py install --user
        
Uninstall
---------

 #. Simply use pip.
      
    .. code-block:: bash
     
    	pip uninstall dipde

       

 		 
Required Dependencies
---------------------

 * `NumPy <http://wiki.scipy.org/Tentative_NumPy_Tutorial>`_
 * `SciPy <http://www.scipy.org/>`_
 * `MatPlotLib <http://matplotlib.org/>`_ 
 * `SymPy <http://www.sympy.org/>`_
