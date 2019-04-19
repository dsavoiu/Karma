********
Concepts
********

Both *Lumberjack* and *Palisade* share some common concepts, which are outlined here.

First, both tools use *Python* modules for **configuration**. These must be written by
the user following a series of conventions (see below) and placed under ``python/Lumberjack/cfg/``
and ``python/Palisade/cfg/``. A configuration module is also called an **analysis**, since
the configuration it contains is often specific to a single *analysis* (with different
conventions, variable names, binnings, etc.).

.. note::
    The above configuration paths must be importable *Python* modules. That is, they must
    either be simple Python files (enough for "small" analyses) or directories containing
    a file called ``__init__.py``. The organization of each configuration module into files
    is left to the user. However, all configurations must declare a number of mandatory
    variables (more details below) and make them available for import at the module level.

Second, both tools provide a way of defining **tasks** in the configuration modules.
The exact meaning of "task" differs slightly between the two, but it can be thought of
as a single unit of work in a particular workflow.

**Tasks** are configured and given a name in the analysis configuration modules and can then
be executed via the **command-line interfaces** provided by both tools:
``lumberjack.py`` and ``palisade.py``.
