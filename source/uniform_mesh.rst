The Mesh and MeshBlocks
=======================

Every AthenaK simulation is defined on a **uniform Cartesian mesh**: a rectangular domain
divided into equally sized cells. That mesh is in turn partitioned into rectangular
**MeshBlocks**, which are the units of computation, parallel decomposition, and (when enabled)
mesh refinement. Understanding the distinction between the ``<mesh>`` and ``<meshblock>``
blocks is essential, and mixing them up is one of the most common configuration mistakes.

Mental model
------------

- ``<mesh>`` defines the **full simulation domain** and its **total resolution**.
- ``<meshblock>`` defines how that domain is **partitioned into blocks**.

Think of ``<mesh>`` as the global grid and ``<meshblock>`` as the tile size. Each MeshBlock
carries a halo of ghost cells (set by ``<mesh>/nghost``) that is filled from neighboring
blocks or the physical boundary conditions before every update.

The ``<mesh>`` block
--------------------

The ``<mesh>`` block sets the domain extent, resolution, and boundary conditions:

.. code-block:: text

   <mesh>
   nghost = 2            # number of ghost cells per face

   nx1    = 256          # cells along x1
   x1min  = 0.0          # domain limits along x1
   x1max  = 1.0
   ix1_bc = periodic     # inner-x1 boundary
   ox1_bc = periodic     # outer-x1 boundary

   nx2    = 128
   x2min  = 0.0
   x2max  = 0.5
   ix2_bc = reflect
   ox2_bc = reflect

   nx3    = 1            # nx3 = 1 => a 2D calculation
   x3min  = -0.5
   x3max  = 0.5
   ix3_bc = periodic
   ox3_bc = periodic

Key parameters:

- ``nx1``, ``nx2``, ``nx3``: total number of cells along each direction. Setting a direction's
  size to ``1`` makes that direction inactive, so ``nx3 = 1`` gives a 2D run and
  ``nx2 = nx3 = 1`` gives a 1D run.
- ``x1min``/``x1max`` (and the x2, x3 analogues): physical extent of the domain. Cell spacing
  is uniform, e.g. :math:`\Delta x_1 = (x1max - x1min)/nx1`.
- ``nghost`` (default ``2``): number of ghost cells per face. Higher-order reconstruction needs
  more: ``ppm4``/``ppmx`` require ``nghost >= 3`` and ``wenoz`` typically ``nghost >= 4``. With
  SMR/AMR, ``nghost`` must be even.
- ``ix1_bc``/``ox1_bc`` (inner/outer boundary on each face): choose from ``periodic``,
  ``reflect``, ``outflow``, ``inflow``, ``diode``, ``vacuum``, ``shear_periodic`` (shearing
  box only), or ``user`` (defined by the problem generator). If either face of a direction is
  ``periodic``, both faces of that direction must be.

The ``<meshblock>`` block
-------------------------

The ``<meshblock>`` block sets the size of a single MeshBlock:

.. code-block:: text

   <meshblock>
   nx1 = 32
   nx2 = 32
   nx3 = 1

The root mesh is tiled by blocks of this size. Each ``meshblock/nx*`` must **evenly divide**
the corresponding ``mesh/nx*``. If the ``<meshblock>`` block is omitted, each block size
defaults to the full mesh size, i.e. the whole domain is a single MeshBlock.

For the example above (256 x 128 mesh, 32 x 32 blocks) this creates:

- ``256 / 32 = 8`` blocks along x1
- ``128 / 32 = 4`` blocks along x2
- ``1 / 1 = 1`` block along x3

for a total of ``8 * 4 * 1 = 32`` MeshBlocks at the root level.

Why partition into MeshBlocks?
------------------------------

MeshBlocks serve three related purposes:

- **Parallelism.** MeshBlocks are distributed across MPI ranks (and mapped to GPUs/threads via
  Kokkos), so the number and size of blocks controls load balance. As a rule of thumb you want
  at least as many blocks as ranks, and usually several per rank.
- **Refinement.** Static and adaptive mesh refinement operate at the MeshBlock level: a block
  flagged for refinement is replaced by finer child blocks. Block size therefore sets how
  precisely refinement can track a feature.
- **Performance.** Very large blocks reduce ghost-cell overhead but coarsen load balance and
  refinement; very small blocks do the opposite. A few tens of cells per side (e.g. 16–64) is
  a typical sweet spot.

Validation rules to remember
----------------------------

- ``meshblock/nx*`` must evenly divide the corresponding ``mesh/nx*``.
- Active-dimension sizes must be at least 4 cells.
- 2D layouts must be in the ``x1``–``x2`` plane: ``nx2 = 1`` with ``nx3 > 1`` is invalid.
- ``nghost >= 2`` globally, and ``nghost`` must be even when SMR/AMR is used.
- If a direction is periodic, both of its boundaries must be ``periodic``.

Next steps
----------

Once the root mesh and MeshBlock decomposition are set, you can add refinement on top of it:

- :doc:`smr` — fixed, geometrically-specified refined regions.
- :doc:`amr` — refinement that adapts to the solution at run time.

The initial state on this mesh is set by a :doc:`problem generator <problem_generators>`.
