Outputs
=======

AthenaK supports a number of output options, each of which can be enabled by adding an
``<output##>`` block to the parameter file, e.g., ``<output1>``, ``<output2>``, etc. All
output blocks must define the following parameters:

- ``file_type``: the kind of output (e.g., full dumps, history files, restart files,
  etc.)
- ``dt``: how frequently in code time to write this output

Some output blocks also support an ``id`` parameter which can be used to choose the stem
for the filename. This is useful if the same variable needs to be output in different
ways, e.g., having 2D sliced outputs in both the x-y and x-z planes at a relatively
frequent cadence and full 3D grid dumps only occasionally.

Output types
------------

The ``file_type`` parameter selects the kind of output. The full set of supported types
is:

.. list-table::
   :header-rows: 1
   :widths: 12 40 48

   * - ``file_type``
     - Output
     - Notes
   * - ``bin``
     - AthenaK binary mesh dump
     - Full or sliced grid; supports SMR/AMR and parallel (MPI) I/O. Preferred for
       production runs. See :doc:`analysis` for reading ``.bin`` files.
   * - ``vtk``
     - Legacy (serial) VTK mesh dump
     - Full or sliced grid. Works with MPI, but **only for unigrid runs — VTK does not
       support SMR/AMR.** Readable by ParaView, VisIt, etc.
   * - ``tab``
     - ASCII table
     - One-dimensional data only; multidimensional grids must be sliced first.
   * - ``hst``
     - History file
     - Global reductions (mass, momentum, energy, constraint norms, …); ASCII.
   * - ``rst``
     - Restart / checkpoint
     - Complete state of the run, used to restart with ``-r``.
   * - ``pdf``
     - PDF / histogram
     - One- or two-dimensional histograms of grid variables.
   * - ``cbin``
     - Coarsened binary
     - Down-sampled (coarsened) binary dump; optionally computes moments.
   * - ``sph``
     - Interpolated spherical surface
     - Data interpolated onto a latitude/longitude grid at a given radius or a list of radii;
       written as VTK.
   * - ``cart``
     - Interpolated Cartesian grid
     - Data resampled onto a uniform Cartesian grid.
   * - ``pvtk``
     - Particle data (VTK)
     - Particle positions/attributes in VTK format.
   * - ``trk``
     - Tracked-particle output
     - Time series for individually tracked particles.
   * - ``log``
     - Event log
     - Runtime event log.

The most common grid outputs (``bin``, ``vtk``, ``tab``) are described next, followed by
restarts, history, and the interpolated/derived output types.

Full grid dumps
---------------

AthenaK can dump grid variables to either custom AthenaK binary files
(``file_type = bin``) or legacy VTK files (``file_type = vtk``). Binary output supports
SMR/AMR meshes and scales with MPI, so it is the appropriate choice for production runs.
VTK output works with MPI as well but is **limited to unigrid runs (it does not support
SMR/AMR)**; it is most convenient for small tests and for direct reading in ParaView or
VisIt.

A full grid dump would be done as follows:

.. code-block:: text

   <output1>
   file_type = bin # or vtk
   variable  = mhd_w_bcc # write the MHD primitive variables with cell-centered B-fields
   dt        = 100.0 # write out every 100.0 time units
   id        = prim_3D # File stem; filename defaults to mhd_w_bcc.*.bin if not specified

``variable`` specifies which quantity (or quantities) to output. A full list of
quantities is available in ``src/outputs/outputs.hpp``, but the following quantities are
among the most commonly used:

- ``hydro_u`` or ``mhd_u``: conserved hydrodynamical variables for the specified fluid
  module, including any weighting by the volume form (i.e., they are densitized)
- ``hydro_w`` or ``mhd_w``: primitive hydrodynamical variables

Sliced grid dumps
-----------------

Instead of the full domain, an output block can write a lower-dimensional slice through
the grid by specifying one or more ``slice_x#`` positions. This works with the ``bin``
and ``vtk`` types (and, for one-dimensional data, ``tab``).

A slice through the :math:`xy` plane at :math:`z=0` could be dumped using:

.. code-block:: text

   <output2>
   file_type = bin # or vtk
   variable  = adm # write the ADM variables
   dt        = 10.0 # write out every 10.0 time units
   slice_x3  = 0.0 # slice along z=0
   id        = adm_xy # File stem; filename defaults to adm.*.bin if not specified

A line in the :math:`z` direction at :math:`x=0.5`, :math:`y=0.25` could be specified
using:

.. code-block:: text

   <output3>
   file_type = bin # or vtk or tab
   variable  = hydro_u # write the conserved hydro variables
   dt        = 1.0 # write out every 1.0 time units
   slice_x1  = 0.5 # slice along x=0.5
   slice_x2  = 0.25 # slice along y=0.25

Note that no interpolation is done during slicing operations, so the actual data written
to the output file is sourced from the nearest cell center to the left of the desired
position, e.g., if there are cell centers at :math:`x=0.3` and :math:`x=0.55`, slicing
through :math:`x=0.5` will return the cell at :math:`x=0.3`. This means that meshblocks
sourced from different refinement levels will be output at slightly different points.

Data can also be written to ASCII tables by setting ``file_type = tab``, but only in one
dimension. Therefore, multidimensional grids must be sliced before outputting to
tabulated data. By default, ``tab`` outputs are written with six significant figures.
This can be changed by setting ``data_format`` to the corresponding C-string format
specifier (see the discussion below on history outputs).

One file per MPI rank
---------------------

By default, when running with MPI the ``bin``, ``cbin``, and ``rst`` outputs use
collective MPI-IO so that all ranks write into a *single shared file* per dump. On very
large (e.g. exascale) runs, collective writes to one shared file can become a
performance and filesystem bottleneck. To avoid this, these output types accept a
``single_file_per_rank`` option:

.. code-block:: text

   <output1>
   file_type = bin
   variable  = mhd_w_bcc
   dt        = 100.0
   single_file_per_rank = true # each MPI rank writes its own file

When ``single_file_per_rank = true``, each rank writes its own file into a per-rank
subdirectory of the output directory, e.g. ``bin/rank_00000000/``,
``bin/rank_00000001/``, and so on. This replaces the single collective write with many
independent per-rank writes, which can dramatically improve I/O throughput and scaling
on large node counts. The option defaults to ``false`` (single shared file), and is
currently supported for the ``bin``, ``cbin``, and ``rst`` output types. Analysis tools
that read these outputs must be aware of the per-rank directory layout.

Restart files
-------------

Restart (or checkpoint) outputs dump the entire state of the run at a regular interval
so that the run can be restarted from that point later on.

.. code-block:: text

   <output4>
   file_type = rst
   dt        = 1000.0 # dump a checkpoint every 1000.0 time units

Restarting is as simple as passing the ``-r`` flag with the restart file to AthenaK:

.. code-block:: bash

   ./athena -r rst/my_run.00001.rst

All input parameters are stored inside the restart file, so it is not necessary to pass
an input file when restarting. However, a parameter file passed to AthenaK during a
restart will take precedence over the parameters in the restart file:

.. code-block:: bash

   ./athena -r rst/my_run.00001.rst -i new_params.athinput

Note that while it is possible to update parameters in existing physics modules this way,
adding or subtracting physics during restarts via a new parameter file is not directly
supported at this time.

History outputs
---------------

History outputs are global reductions of the entire grid at a given time. For example,
hydro and MHD simulations will compute global integrals of the conserved variables to
measure things like the total mass or momentum in the system, and Z4c simulations will
calculate the L2 norm of various constraint monitors. It is also possible to add custom
history outputs via the problem generator, such as integrating various fluxes across
spherical surfaces in ``gr_torus`` or tracking the maximum density as in ``dyngr_tov``.

Below is an example of a history file output:

.. code-block:: text

   <output5>
   file_type = hst  # history output
   dt        = 10.0 # output interval

Additionally, if the pgen supports a custom history function, the input file should set
``problem/user_hist = true`` and may optionally set ``output#/user_hist_only = true`` if
only the user history file is desired:

.. code-block:: text

   <problem>
   ... # other parameters
   user_hist = true # enroll user-defined history

   ...
   <output1>
   file_type = hst       # history output
   dt        = 10.0      # output interval
   user_hist_only = false # set to true to output only the user-defined history function

History files are human-readable text files with columns separated by whitespace and
comments marked with ``#`` as in Python and other scripting languages. Consequently,
these files can be readily imported into numpy, gnuplot, etc. By default, outputs are
written with six digits. This can be modified by setting the ``data_format`` option. For
example,

.. code-block:: text

   <output2>
   file_type = hst       # history output
   dt        = 10.0      # output interval
   data_format = %20.15e # write out 15 significant digits

will write 15 significant digits in scientific notation, using whitespace to ensure the
string width is at least 20 characters. Formatting strings use C-style formatting
specifiers, as in `printf <https://cplusplus.com/reference/cstdio/printf/>`_.

PDF/histograms
--------------

TODO

Interpolated spherical grid
---------------------------

AthenaK can interpolate data to a latitude/longitude spherical grid and save it to a
``.vtk`` file. The user can either interpolate onto a single radius or a list of radii. 
This allows merging multiple output blocks for the same variable at different radii into 
a single output block. For a single radius we can add the following block:

.. code-block:: text

   <output3>
   file_type = sph       # spherical grid output
   dt        = 5.0       # output interval
   variable  = mhd_w_bcc # write out MHD variables
   radius    = 200.0     # extract data at a radius of 200 in code units
   ntheta    = 64        # number of angles in polar direction, 32 by default; azimuthal direction is always 2*ntheta.
   xc        = 0.0       # x, y, and z coordinates of center of sphere; (0, 0, 0) by default.
   yc        = 0.0
   zc        = 0.0

Alternatively, instead of ``radius``, we can manually add a list of radii with:

.. code-block:: text

  <output4>
  file_type = sph
  ...
  radii     = 10.0 20.0 30.0

A more convenient way is to specify a range of radii:

.. code-block:: text

  <output5>
  file_type = sph
  ...
  r_min     = 10.0
  r_max     = 100.0
  nradii    = 100
  r_spacing = log # linear

The user can choose between log- or linear-spacing.

Interpolated cartesian grid
---------------------------

TODO

Coarsened grids
---------------

TODO
