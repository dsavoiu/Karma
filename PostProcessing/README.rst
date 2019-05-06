.. image:: https://readthedocs.org/projects/karma-hep/badge/?version=latest
    :target: https://karma-hep.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

##################################
**Karma** toolset for HEP analyses
##################################

**Karma** is a set of tools intended for use in high-energy physics (HEP)
analyses which typically need to process large amounts of data.

This is the **PostProcessing** module. It contains two Python packages
intended for the following purposes:

**Lumberjack**
  used for *data reduction* of ROOT n-tuples (*TTrees*) to analysis-level objects
  like histograms, profiles, graphs, etc.

**Palisade** 
  used for further processing of ROOT files containing analysis-level objects (in particular
  *Lumberjack* output files. Can be used for plotting or manipulating objects in the input files
  and writing the results to one or more output ROOT files.

For more information about how to use these tools, consult the
`Karma documentation <https://karma-hep.readthedocs.io/en/latest/?badge=latest>`_
on *Read the Docs*.

************
Installation
************

The full *Karma* toolset (including skimming and ntuple-generating tools)
requires the *CMS Software Framework* (CMSSW). Any version starting with
the ``CMSSW_8_0_X`` series should already contain all the required packages.
To install the *Karma* toolset inside a *scram*/*CMSSW* development area,
follow the instructions in the *CMSSW* section titled below.

The *PostProcessing* tools **Lumberjack** and **Palisade** do not depend on
*CMSSW* and can be installed independently. To do this, follow the instructions
in the *Standalone* section below.

CMSSW
=====

    **Note**: This section assumes you are familiar with *CMSSW*, that the
    *CERN Virtual File System* (CVMFS) is mounted on your machine, and that you
    have access to the *CMS VO* software repository on CVMFS. (normally
    under ``/cvmfs/cms.cern.ch``).

First, set up a *scram*/*CMSSW* working area, if you have not already done so:

.. code:: bash

  export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
  source $VO_CMS_SW_DIR/cmsset_default.sh
  scramv1 project CMSSW CMSSW_10_2_8

The above commands will create a directory ``CMSSW_10_2_8`` containing a
*scram* working area for version ``CMSSW_10_2_8`` of *CMSSW*.

Next, switch to the ``src`` subdirectory of your working area and clone the
*Karma* repository inside of it:

.. code:: bash

  cd CMSSW_10_2_8/src
  git clone https://github.com/dsavoiu/Karma

Finally, activate the environment and compile all packages inside the source
directory using *scram*:

.. code:: bash

  eval `scramv1 runtime -sh`
  scram b -j10

That's it! Now you should be able to run ``lumberjack.py`` and ``palisade.py``
on the command line and import the post-processing modules in Python.
To test:

.. code:: bash

  python -c 'from Karma.PostProcessing import Lumberjack, Palisade'
  lumberjack.py --help
  palisade.py --help

Additionally, you may want to install the optional dependency ``tqdm``. This
will allow *Lumberjack* and *Palisade* to display a progress bar in the command
line while running. You can install it with ``pip`` by running:

.. code:: bash

  pip install --user tqdm


Standalone
==========

To run in standalone mode, a working *ROOT* instalation (with *PyROOT*)
is required. For more information, refer to the *ROOT* documentation at
http://root.cern.ch.

To install the *PostProcessing* package as a standalone package, simply clone
it to a directory of your choice and install it from the *PostProcessing*
directory using *pip*:

.. code:: bash

  git clone https://github.com/dsavoiu/Karma
  cd Karma/PostProcessing
  pip install --user .

You can also tell pip to install the *PostProcessing* package in "editable"
or "developer" mode. This will create a symbolic link to the package directory
instead of copying the files, so any changes to the source code have immediate
effect without needing to reinstall. For this, run *pip* with the ``-e`` flag
instead:

.. code:: bash

  pip install --user -e .
  
*Pip* should install all remaining dependencies automaticallu.  You may also
want to install the optional dependency ``tqdm`` to display a progress bars
while processing. You can install it with ``pip`` by running:

.. code:: bash

  pip install --user tqdm
