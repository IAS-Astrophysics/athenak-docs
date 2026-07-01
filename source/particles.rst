Particles
=========

Introduction
------------

AthenaK can evolve Lagrangian particles alongside (or independently of) the fluid. Particles
are distributed across the same MeshBlock decomposition as the mesh and are migrated between
blocks (and MPI ranks) as they move. The module is under active development; the current
public version supports ``cosmic_ray`` particles advanced with a simple ``drift`` pusher, and
is primarily useful as the scaffolding for particle-based physics and for tracer diagnostics.

Particles require a 2D or 3D mesh (1D is not supported).

Inputs
------

Particles are enabled by adding a ``<particles>`` block:

- ``ppc`` (default ``1.0``): particles per cell. The total number allocated on a rank is
  ``ppc`` times the number of active cells across its MeshBlocks (fractional values ``< 1`` are
  allowed).
- ``particle_type`` (**mandatory**): the particle physics type. Currently the only supported
  value is ``cosmic_ray``.
- ``pusher`` (**mandatory**): the time-integration algorithm. Currently the only supported
  value is ``drift``.
- ``assign_tag`` (default ``index_order``): how unique particle tags are assigned; either
  ``index_order`` (sequential across ranks) or ``rank_order``.

The number of particles is set by ``ppc``, but their **initial positions and velocities are
set by the problem generator**, not by the input file. The bundled ``part_random`` generator,
for example, seeds each particle at a random position within its MeshBlock with a random
velocity.

Outputs
-------

Particles use dedicated output file types (set via ``<output>/file_type``):

- ``pvtk`` with ``variable = prtcl_all``: dumps **all** particles to a VTK file. Each particle
  records its position, owning MeshBlock ``gid``, and ``ptag``.
- ``trk`` with ``nparticles = <N>``: appends a time series for a tracked subset (the ``N``
  particles with the smallest tags), writing position **and** velocity for each. No
  ``variable`` line is needed for this type.

In addition, the particle number density can be binned onto the mesh and written with any
mesh output type by requesting ``variable = prtcl_d`` (the field is named ``pdens``). This is
the easiest way to visualize the particle distribution with the standard slice tools.

Example: randomly drifting particles
------------------------------------

The ``part_random`` problem generator fills the domain with randomly placed particles, each
given a random constant velocity, and lets them drift across MeshBlock and rank boundaries —
a good exercise of the particle infrastructure. AthenaK ships an input file at
``inputs/particles/random_particle_drift.athinput``.

**1. Build the problem generator** (it is a custom generator, selected at build time):

.. code-block:: bash

   cmake -B build -DPROBLEM=part_random
   cmake --build build -j

**2. Note the particle block:**

.. code-block:: text

   <particles>
   particle_type = cosmic_ray
   ppc    = 0.01           # particles per cell
   pusher = drift

**3. Slightly modify it.** The shipped file is a large 3D run; shrink the grid so it runs in
seconds and write the particle density to the native binary format so it can be visualized
with the slice plotter. Reduce the ``<mesh>`` and ``<meshblock>`` sizes (keep all three
dimensions — the ``part_random`` generator is 3D), and switch the density output to binary:

.. code-block:: text

   <mesh>
   nx1 = 64
   nx2 = 64
   nx3 = 64

   <meshblock>
   nx1 = 32
   nx2 = 32
   nx3 = 32

   <output1>
   file_type = bin         # native binary dump
   variable  = prtcl_d     # particle number density on the mesh
   dt        = 0.01

**4. Run and visualize** the particle number density (``plot_slice.py`` takes a midplane slice
of the 3D dump automatically):

.. code-block:: bash

   ./build/src/athena -i inputs/particles/random_particle_drift.athinput -d run
   python3 vis/python/plot_slice.py run/bin/random.prtcl_d.00016.bin pdens parts.png --notex

The binned particle density is nearly uniform (as expected for a random distribution), with
Poisson fluctuations from cell to cell:

.. image:: /_static/particles_density.png
   :alt: Particle number density binned onto the mesh
   :align: center
   :width: 70%

To follow individual trajectories instead, add a ``trk`` output with ``nparticles`` set to the
number of particles you want to track.
