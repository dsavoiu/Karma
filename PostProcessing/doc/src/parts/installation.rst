************
Installation
************

The full *Karma* toolset (including skimming and ntuple-generating tools)
requires the *CMS Software Framework* (CMSSW). Any version starting with
the ``CMSSW_8_0_X`` series should already contain all the required packages.
To install the *Karma* toolset inside a *scram*/*CMSSW* development area,
follow the instructions in the section titled
:ref:`CMSSW <installation-cmssw>` below.

The *PostProcessing* tools **Lumberjack** and **Palisade** do not depend on
*CMSSW* and can be installed independently. To do this, follow the instructions
in the section titled :ref:`Standalone <installation-standalone>`  below.

.. _installation-cmssw:

CMSSW
=====

.. note::
    This section assumes you are familiar with *CMSSW*, that the
    *CERN Virtual File System* (CVMFS) is mounted on your machine, and that you
    have access to the *CMS VO* software repository on CVMFS. (normally
    under ``/cvmfs/cms.cern.ch``).

First, set up a *scram*/*CMSSW* working area, if you have not already done so:

.. code:: bash

  $> export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
  $> source $VO_CMS_SW_DIR/cmsset_default.sh
  $> scramv1 project CMSSW CMSSW_10_2_8

The above commands will create a directory ``CMSSW_10_2_8`` containing a
*scram* working area for version ``CMSSW_10_2_8`` of *CMSSW*.

Next, switch to the ``src`` subdirectory of your working area and clone the
*Karma* repository inside of it:

.. code:: bash

  $> cd CMSSW_10_2_8/src
  $> git clone https://github.com/dsavoiu/Karma

Finally, activate the environment and compile all packages inside the source
directory using *scram*:

.. code:: bash

  $> eval `scramv1 runtime -sh`
  $> scram b -j10

That's it! Now you should be able to run ``lumberjack.py`` and ``palisade.py``
on the command line and import the post-processing modules in Python.
To test:

.. code:: bash

  $> python -c 'from Karma.PostProcessing import Lumberjack, Palisade'
  $> lumberjack.py --help
  $> palisade.py --help

Additionally, you may want to install the optional dependency ``tqdm``. This
will allow *Lumberjack* and *Palisade* to display a progress bar in the command
line while running. You can install it with ``pip`` by running:

.. code:: bash

  $> pip install --user tqdm



.. _installation-standalone:

Standalone
==========

.. todo::

    Test this and add this section.
