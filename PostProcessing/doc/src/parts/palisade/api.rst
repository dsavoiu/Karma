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


Context-dependent placeholders
------------------------------

A *Palisade* task **configuration** describes a workflow
that involves accessing content from input files, processing
it, and writing the result to output files. More often than
not, the same workflow is applied to a series of inputs,
specified by an **expansion context**. As a result, the
concrete value of many configuration entries will depend on
the particular context.

The need for context-dependent configurations is addressed by
*Palisade* in two ways. The first involves performing *string
interpolation* with the current context, while the second
provides users with a series of dedicated *placeholder* objects
to be used where a context-dependent value is needed.

Two high-level objects are provided for this purpose:
``ContextValue`` and ``InputValue``. The former resolves
to a concrete value provided in the current expansion context,
while the latter allows users to specify an expression for
retrieving objects from input files:

.. autoclass:: Palisade.ContextValue
    :show-inheritance:
    :members:

.. autoclass:: Palisade.InputValue
    :show-inheritance:
    :members:

A powerful feature of the above objects is that they can be
combined using arbitrarily complex expressions. A large portion
of native Python expression syntax is supported, including
arithmetical expressions and string formatting operations.
However, not all Python syntax is supported. Consult the
documentation ref:`below <api-palisade-lazy-expressions>` for
an overview of supported operations and current limitations.

Expressions involving the above classes will store the
entire expression syntax tree, allowing the values to be
reconstructed at runtime, while also substituting
context-dependent values from the current context.



.. note::
    To disable string interpolation explicitly for a string,
    it must be wrapped in the :py:class:`~Palisade.String`
    helper class.


Configuration helper classes
----------------------------

Context-dependent configuration entries are implemented
using lazy evaluation techniques. A configuration entry
whose value depends on an **evaluation context** cannot
be initialized with a concrete value at configuration-time,
so it is initialized in a *lazy* manner.

This means that it is initialized to a *placeholder*
structure that contains all the necessary information to
produce the concrete value, except the information
contained in the evaluation context.

The placeholder is kept unevaluated until the evaluation
context is available at run-time. Its concrete value is
then be determined by **dispatching** it over the context.

The implementation of the context-dependent configuration
entries is done using a series of **helper classes**. Each
class represents a type of **node** in the abstract syntax
tree of expressions involving context-dependent values.

All such nodes inherit from the ``LazyNodeBase`` class.

.. autoclass:: Palisade.LazyNodeBase
    :members:

In particular, the high-level placeholders
:py:class:`~Palisade.ContextValue` and
:py:class:`~Palisade.InputValue` inherit from
:py:class:`~Palisade.LazyNodeBase`, so this section
also applies to them.

Nodes that support iteration derive from the
``LazyIterableNodeBase`` class:

.. autoclass:: Palisade.LazyIterableNodeBase
    :show-inheritance:
    :members:


Simple lazy nodes
^^^^^^^^^^^^^^^^^

The simplest lazy node is the ``Lazy`` node, which is used to wrap a (typically non-lazy) value
``value``:

.. autoclass:: Palisade.Lazy
    :show-inheritance:
    :members:

``Lazy`` nodes stay unevaluated until their :py:meth:`~Palisade.LazyNodeBase.eval` method is called:

.. code:: python

   >>> a = Lazy('a')
   >>> a
   Lazy('a')
   >>> a.eval()
   'a'

``Lazy`` nodes can be used as lazy containers for other ``Lazy`` nodes. In this case, the
:py:meth:`~Palisade.LazyNodeBase.eval` method must be called multiple times to
resolve to the contained value:

.. code:: python

   >>> a = Lazy(Lazy('a'))
   >>> a
   Lazy(Lazy('a'))
   >>> a.eval()
   Lazy('a')
   >>> a.eval().eval()
   'a'

Turning objects into lazy nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A non-lazy expression can be made lazy using the ``lazify`` helper function:

.. autofunction:: Palisade.lazify

.. note:
    There is a difference between wrapping an object in the :py:class:`~Palisade.Lazy` class and calling
    :py:func:`~Palisade.lazify` on it. In the former case, the object is wrapped as-is, while the latter
    also threads over lists, tuples and dictionaries, making only their elements (or keys and values)
    in :py:class:`~Palisade.Lazy`.

    .. code:: python

       >>> l = [1, [2, {'3': (4, 5)}]]
       >>> Lazy(l)
       Lazy([1, [2, {'3': (4, 5)}]])
       >>> lazify(l)
       List([Lazy(1), List([Lazy(2), Map({Lazy('3') : List([Lazy(4), Lazy(5)])})])])


Pretty-printing lazy nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^

As can be seen in the above note, lazy expressions can easily become large. To display a pretty-printed
structure of a lazy expression on multiple lines, the method :py:meth:`~Palisade.pprint` is provided:

.. code:: python

   >>> l = [1, [2, {'3': (4, 5)}]]
   >>> lazify(l).pprint()
   List([
     Lazy(1),
     List([
       Lazy(2),
       Map({
         Lazy('3') : List([
           Lazy(4),
           Lazy(5)
         ])
       })
     ])
   ])


Lazy containers
^^^^^^^^^^^^^^^

Two types of lazy containers are provided: ``List`` and ``Map``,
which will evaluate to lists and dictionaries, respectively.

.. autoclass:: Palisade.List
    :show-inheritance:
    :members:

.. autoclass:: Palisade.Map
    :show-inheritance:
    :members:


.. _api-palisade-lazy-expressions:

Lazy expressions
^^^^^^^^^^^^^^^^

Lazy nodes can be used almost seamlessly in Python expressions. Expressions involving
lazy nodes will be lazy nodes themselves and evaluating them will cause the nodes
to be evaluated. The result is in most cases identical to what the equivalent non-lazy
expression would return.

Supported expressions include:

* basic arithmetical and logical operations:

  .. code-block:: python

     >>> (Lazy(2) + Lazy(3)).eval()
     5

     >>> (Lazy(True) & Lazy(False)).eval()
     False

  .. warning::
    Logical operations must use the ``&`` and ``|`` operators,
    not the Python keywords ``and`` and ``or``, which will give
    the wrong results.

* basic comparisons:

  .. code:: python

     >>> (Lazy(2) < Lazy(3)).eval()
     True

     >>> (Lazy(2) > Lazy(3)).eval()
     False

  .. note::
    Multi-term comparisons do not work!

    .. code:: python

       >>> (Lazy(3) < Lazy(4) < Lazy(1)).eval()  # should be False
       True

    As a workaround, expand these using only binary comparisons:

    .. code:: python

       >>> (((Lazy(3) < Lazy(4)) & (Lazy(4) < Lazy(1)))).eval()
       False

* string formatting

  .. code:: python

     >>> String("{0}{0}").format(Lazy('a')).eval()
     'aa'

  .. note::

      The string containing the template expression has to be wrapped
      inside a :py:class:`~Palisade.String`. Using a regular string here
      will not work:

      .. code:: python

         >>> "{0}{0}".format(Lazy('a')).eval()
         AttributeError: 'str' object has no attribute 'eval'

* function calls:

  .. code:: python

     >>> Lazy(str)(2).eval()  # function needs to be lazified
     '2'

* object attribute access:

  .. code:: python

     >>> my_object.my_attribute = 42
     >>> Lazy(my_object).my_attribute.eval()
     42

The following lazy nodes are used to represent the
abstract syntax tree of the lazy expression:

.. autoclass:: Palisade.Attribute
    :show-inheritance:
    :members:

.. autoclass:: Palisade.BinOp
    :show-inheritance:
    :members:

.. autoclass:: Palisade.Call
    :show-inheritance:
    :members:

.. autoclass:: Palisade.FormatString
    :show-inheritance:
    :members:

.. autoclass:: Palisade.Op
    :show-inheritance:
    :members:

.. autoclass:: Palisade.String
    :show-inheritance:
    :members:


Lazy control flow structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The use of lazy nodes is not limited to basic expressions. With the
help of the following classes, control structures such as
conditionals and exception handlers can be implemented using lazy
nodes:

* conditional expressions using :py:class:`~Palisade.If`

  .. code:: python

     >>> If(Lazy(True), Lazy('true!'), Lazy('false!')).eval()
     'true!'
     >>> If(Lazy(False), Lazy('yes!'), Lazy('no!')).eval()
     'no!'

* exception handling using :py:class:`~Palisade.Try`

  .. code:: python

     >>> Lazy(len)(2).eval()
     TypeError: object of type 'int' has no len()
     >>> Try(Lazy(len)(2), TypeError, 'ERROR').eval()
     'ERROR'

.. autoclass:: Palisade.If
    :show-inheritance:
    :members:

.. autoclass:: Palisade.Try
    :show-inheritance:
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
