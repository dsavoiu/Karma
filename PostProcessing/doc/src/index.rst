#######################
**Karma** documentation
#######################

**Karma** is a set of tools intended for use in high-energy physics (HEP)
analyses. These analyses process a large amount of data and typically involve
many data-processing steps.

Consider the following typical workflow for HEP analyses performed at the CMS
experiment:

1. **Skimming**: event data in an experiment-specific format (``AOD``, ``miniAOD``, etc.)
   is "skimmed" to an analysis-specific format which only stores information
   relevant for the analysis in question.
2. **N-tuple production**: the "skims" are then processed by the main analysis code. This produces so-called
   n-tuples, which store a fixed number of characteristic quantities for each event
3. **Data reduction**: the raw data contained in the n-tuples is then filtered, split into regions
   and binned to produce final analysis-level objects (i.e. histograms, profile histograms, etc.)
4. **Post-processing**: finally, post-processing operations (histogram manipulation, fits, etc.) are
   applied to the analysis-level objects and the results are extracted or represented
   graphically ("plotted").

While the *Karma* package provides tools for performing each of the steps outlined above,
this guide only covers the tools used for the last two steps. They are called **Lumberjack**
(used for *data reduction* to e.g. histograms) and **Palisade** (used for generic *post-processing*).

.. toctree::
   :name: mastertoc
   :maxdepth: 3
   :includehidden:

   parts/installation
   parts/concepts
   parts/lumberjack/user_guide
   parts/palisade/user_guide
   parts/api_documentation/index
