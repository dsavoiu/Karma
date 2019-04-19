.. _api-palisade:

*Palisade* API
==============

Input modules
-------------

.. autoclass:: Palisade.InputROOT
    :members:

Processors
----------

.. autoclass:: Palisade.AnalyzeProcessor
    :members:
    :show-inheritance:

.. autoclass:: Palisade.PlotProcessor
    :members:
    :show-inheritance:


.. autoclass:: Palisade.Processors._base._ProcessorBase
    :members:


Configuration tools
-------------------

.. autoclass:: Palisade.ContextValue
    :members:

.. autoclass:: Palisade.LiteralString
    :members:


Built-in input functions
------------------------

A number of common functions are already registered in
:py:class:`~Palisade.InputROOT`
as "built-ins". They are listed below.

.. warning::
    The functionality of each of these functions is not stable and may change
    in the future. This list is provided for the sake of completeness only.


.. autoclass:: Palisade._input._ROOTObjectFunctions
    :members:
    :no-special-members:
    :exclude-members: get_all, __init__
