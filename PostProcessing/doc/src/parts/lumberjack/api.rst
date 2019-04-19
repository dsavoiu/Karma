*Lumberjack* API
================

**Lumberjack** is a tool for processing large amounts of columnar data stored in ROOT ``TTree``
objects. For analysis purposes, these data are typically processed to obtain simpler
analysis-level objects such as histograms or profile histograms ("profiles" for short).

Consider the following typical workflow:

#. apply arbitrary filters to the data
#. split a dataset into several (possibly overlapping) regions
#. bin the data (possibly in more than one dimension) to produce histograms and/or profiles

In principle, this is achievable by using the interface provided by the ``TTree`` directly,
but this implies writing a lot of "boilerplate" C++ and/or Python code, which can be tedious
and error-prone. In addition, this approach often results in generic code (e.g. the event loop)
being mixed with analysis-specific code and metadata (binnings, threshold values for filters, etc.),
which can prove difficult to debug and maintain.

Lumberjack aims to provide users with a simple but powerful interface for configuring and running
such a workflow. It uses the ``RDataFrame`` interface in ROOT for fast multi-threaded processing
of ``TTrees`` and outputs the resulting analysis-level objects to a ROOT file in an intuitive
structure.


Configuration tools
-------------------

.. autoclass:: Lumberjack.Quantity
    :members:
    :show-inheritance:
