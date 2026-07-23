The Input File
==============

Input file format
-----------------

AthenaK requires an input file containing runtime parameters. Usually this file is
given the name ``<problem-name>.athinput``, where ``<problem-name>`` is an identifier of
the problem. Sample input files are provided in ``inputs/``.

Within the input file, parameters are grouped into named blocks, with the name of each
block appearing on a single line within angle brackets, for example

.. code-block:: text

   <time>
   cfl_number = 0.4       # The Courant, Friedrichs, & Lewy (CFL) Number
   nlim       = -1        # cycle limit
   tlim       = 1.0       # time limit

Block names must always appear in angle brackets on a separate line (blank lines above
and below the block names are not required, but can be used for clarity).

Below each block name is a list of parameters, with syntax

.. code-block:: text

   parameter = value [# comments]

White space after the parameter name, after the ``=``, and before the ``#`` character is
ignored. Everything after (and including) the ``#`` character is also ignored. Only one
parameter value can appear per line. Comment lines (i.e. lines beginning with ``#``) are
allowed for documentation purposes. Both block names and parameter names are case
sensitive. Note that tabs should not be used in the input file as the parser does not
support them.

.. note::

   This page documents the **general, physics-agnostic blocks** that appear in nearly
   every input file. Options specific to a particular physics module (for example the
   ``<hydro>``, ``<mhd>``, ``<radiation>``, ``<z4c>``, and ``<coord>`` blocks) or to an
   individual problem (``<problem>``) are documented alongside the physics or problem
   generator that owns them. See :ref:`physics-and-problem-blocks` below for pointers.

General blocks
--------------

- ``<comment>`` (optional): for documentation purposes

  - ``problem`` (optional): problem description
  - ``reference`` (optional): journal reference (if any)
  - ``configure`` (optional): suggested configuration parameters

- ``<job>`` (**mandatory**)

  - ``basename`` (**mandatory**): base name used for all output file names

- ``<output[n]>`` (optional): output information (``[n]`` is an integer)

  - ``file_type`` (**mandatory**): file type (``vtk``, ``bin``, ``rst``, etc.; see
    :doc:`outputs`)
  - ``dt`` (``dt`` or ``dcycle`` is **mandatory**): output interval in computing time
  - ``dcycle`` (``dt`` or ``dcycle`` is **mandatory**): output interval in cycles
  - ``variable`` (depends): variable(s) to be output (see :doc:`outputs`)
  - ``data_format`` (optional; used only for ``.tab`` and ``.hst``): format specifier
    string used for writing data (e.g. ``%12.5e``)
  - ``id`` (optional): output ID used in file names (default = ``out[n]``)
  - ``slice_x?`` (optional): sliced output in orthogonal directions at the specified
    position (``? = 1, 2, or 3``)
  - ``ghost_zones`` (optional): include boundary ghost cells in output (default =
    ``false``)

- ``<time>`` (**mandatory**): the CFL number and limit of the simulation

  - ``cfl_number`` (**mandatory**): the Courant, Friedrichs, & Lewy (CFL) Number
  - ``nlim`` (**mandatory**): time step (cycle) limit (-1 = infinity)
  - ``tlim`` (**mandatory**): time limit in computing time
  - ``start_time`` (optional): time at the beginning of new simulation (default = 0)
  - ``integrator`` (optional): time-integration scheme (e.g. ``rk2`` [*default*],
    ``rk3``)

- ``<mesh>`` (**mandatory**): grid geometry

  - ``nx1, nx2, nx3`` (**mandatory**): the number of cells in the x1, x2, x3 directions,
    respectively (``nx3=1`` means 2D, ``nx2=1`` implies 1D)
  - ``x1min, x1max``, etc. (**mandatory**): positions of the minimum and maximum
    surfaces (i.e., the box size)
  - ``ix1_bc, ox1_bc``, etc. (**mandatory**): boundary conditions

  .. note::

     Mesh refinement is configured in the separate ``<mesh_refinement>`` block (with
     ``<refined_region#>`` and ``<amr_criterion#>`` blocks), **not** in ``<mesh>``. See
     :doc:`smr` and :doc:`amr`.

- ``<meshblock>`` (optional): domain decomposition unit

  - ``nx1, nx2, nx3`` (**mandatory**): the number of cells per MeshBlock in x1, x2, x3,
    respectively

.. _physics-and-problem-blocks:

Physics and problem blocks
--------------------------

Which physics a run includes is determined by which blocks are present in the input file.
The parameters for these blocks are documented with the physics or problem that owns them
(dedicated physics-module pages are forthcoming):

- ``<hydro>`` — hydrodynamics (EOS, reconstruction, Riemann solver, floors, ...)
- ``<mhd>`` — magnetohydrodynamics
- ``<radiation>`` — radiation transport
- ``<z4c>`` — numerical relativity (Z4c)
- ``<coord>`` — coordinate system (e.g. black-hole spin for GR)
- ``<mesh_refinement>``, ``<refined_region#>``, ``<amr_criterion#>`` — mesh refinement;
  see :doc:`smr` and :doc:`amr`
- ``<problem>`` — problem-specific parameters read by the problem generator; see
  :doc:`problem_generators`
- ``<chemistry>`` - chemical evolution; see :doc:`chemistry`

Changes from Athena++
---------------------

In many instances, options that were specified at compile time in Athena++ are now
specified at run time. For example, the number of ghost zones, reconstruction
algorithm, and Riemann solver are now runtime parameters. Furthermore, the inclusion of
certain blocks inside the input file determines which physics are incorporated into a
given run.
