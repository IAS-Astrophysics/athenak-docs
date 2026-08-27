Cyclic Zoom
===========

Cyclic zoom is an AMR method for evolving systems that span a large range of spatial and
temporal scales. The mesh cycles between zooming in (refining a central region) and zooming
out (coarsening it), storing fine-grid fluid variables in a mask so that small-scale
structure can be restored on the next zoom-in. The method is described in `Guo et al., ApJ
987, 202 (2025)
<https://ui.adsabs.harvard.edu/abs/2025ApJ...987..202G/abstract>`_.

Enabling cyclic zoom
--------------------

Cyclic zoom requires adaptive mesh refinement (see :doc:`amr`). Set
``refinement = adaptive`` in ``<mesh_refinement>``, seed the finest level with a
``<refined_region#>`` block, and add an ``<amr_criterion#>`` block with
``method = cyclic_zoom``:

.. code-block:: text

   <mesh_refinement>
   refinement          = adaptive
   num_levels          = 16
   refinement_interval = 1
   max_nmb_per_rank    = 960

   <refined_region1>
   level = 15
   x1min = -1.0
   x1max =  1.0
   x2min = -1.0
   x2max =  1.0
   x3min = -1.0
   x3max =  1.0

   <amr_criterion1>
   method     = cyclic_zoom
   nlevels    = 8
   r_0        = 1.0
   trun_fac   = 10.0
   trun_pow   = 1.5
   trun_fac_0 = 100.0
   trun_fac_1 = 0.0
   trun_fac_2 = 0.0

   <cyclic_zoom>
   verbose = true

The ``<refined_region#>`` block only sets the *initial* mesh. After that, cyclic zoom
controls refinement and derefinement; unlike standard AMR criteria it is meant to replace
slope or density triggers rather than run alongside them.

A ``<cyclic_zoom>`` block is optional and holds flags that are not part of the AMR
criterion itself (verbosity, restart, memory caps). Most zoom parameters are read from
the ``<amr_criterion#>`` block that has ``method = cyclic_zoom``.

How it works
------------

The mesh is organized into *zones*. Zone 0 is the finest active configuration (AMR level
``max_level``). Increasing the zone number coarsens the central region by one AMR level.
The zoom radius and dwell time at zone :math:`n` are

.. math::

   R_n = r_0\, 2^{n}, \qquad
   t_{\mathrm{run},n} = \min\!\bigl(\mathtt{trun\_fac\_}n \cdot R_n^{\mathtt{trun\_pow}},
   \mathtt{trun\_max}\bigr).

When the simulation time reaches the next scheduled zoom, the criterion either coarsens
(``direction = +1``) or refines (``direction = -1``) MeshBlocks that overlap a spherical
refinement region of radius :math:`f_{\mathrm{ref}} R_n`. Fine-grid conserved variables
(and, for MHD, electric fields) inside the zoom sphere are stored before coarsening and
reapplied as a mask when the mesh zooms back in. For MHD, a constrained-transport
correction applies a :math:`\Delta E` source term so that :math:`\nabla\cdot B = 0` is
preserved across the zoom.

Setting ``trun_fac_n = 0`` makes the dwell time at that zone vanish, so the mesh passes
through it on the next AMR check. The Bondi and monopole examples use this to spend
essentially all of the runtime at zone 0 and a few coarse zones.

``<amr_criterion#>`` parameters
-------------------------------

Zoom AMR and timing

- ``nlevels`` (default ``2``): number of zoom zones. The coarsest zoom level is
  ``max_level - nlevels + 1``. This is independent of ``<mesh_refinement>/num_levels``,
  which still sets the full AMR hierarchy.
- ``r_0`` (default ``1.0``): zoom-sphere radius at zone 0.
- ``x1c``, ``x2c``, ``x3c`` (default ``0``): center of the zoom sphere.
- ``trun_fac`` (default ``1.0``): default dwell-time factor, used for any zone that does
  not set ``trun_fac_n``.
- ``trun_fac_n``: dwell-time factor for zone ``n`` (``n = 0 \ldots nlevels-1``).
- ``trun_pow`` (default ``0``): power of the zoom radius in the dwell-time formula.
- ``trun_max`` (default ``FLT_MAX``): cap on the dwell time.
- ``zone`` (default ``0``) and ``direction`` (default ``1``): initial zoom state. Leave
  these at the defaults for a new run; they are restored from the restart file.

Region scales (each is :math:`\min(f R_n, r_{\max})`)

- ``f_ref`` (default ``1.0``), ``r_ref_max``: radius used to mark MeshBlocks for
  refinement or derefinement.
- ``f_exc`` (default ``0.4``), ``r_exc_max`` (default ``8``): when GR excision is enabled,
  the excision and flux-excision radii are raised to at least this value. This keeps the
  inner boundary inside the zoom mask as the mesh coarsens.
- ``f_cut`` (default ``0``), ``r_cut_max``: if set, zeros velocity inside this radius
  when the zoom mask is applied.
- ``f_flx`` (default ``0``), ``r_flx_max``: if set, zeros electric fields inside this
  radius.

MHD electric-field correction

- ``add_emf`` (default ``true``): apply the :math:`\Delta E` constrained-transport
  correction. Ignored for hydro.
- ``emf_fmax`` (default ``1.0``): clip :math:`|\Delta E|` to this factor times the
  maximum :math:`|E|` in the zoom region.
- ``emf_zmax`` (default ``nlevels``): maximum zone at which the EMF correction is applied.

First zoom-in fill (used only if stored zoom data are missing)

- ``d_zoom``, ``p_zoom`` (default ``FLT_MIN``): uniform density and pressure written into
  the zoom region.

``<cyclic_zoom>`` parameters
----------------------------

- ``verbose`` (default ``false``): print zoom diagnostics (zone, radii, dwell time).
- ``read_rst`` / ``write_rst`` (default ``true``): include zoom state and stored zoom
  MeshBlock data in restart files.
- ``max_nzmb_per_dvce`` / ``max_nzmb_per_host`` (default ``max_nmb_per_rank``): memory
  caps on stored zoom MeshBlocks. Neither may exceed ``max_nmb_per_rank``.

Supported physics
-----------------

Cyclic zoom works with a 3D mesh and hydro, MHD, and/or radiation. Regression tests
cover:

- GR hydrodynamics (Bondi accretion)
- GR MHD (monopole), including the EMF :math:`\Delta E` correction

Newtonian and special-relativistic hydro/MHD use the same store/mask path. Radiation
intensity ``i0`` is stored, coarsened, and restored with the zoom mask. There is no
radiation-zoom test in the CI suite.

The constructor requires a 3D mesh and hydro, MHD, and/or radiation. It aborts if cyclic
zoom is combined with:

- ion–neutral (two-fluid) MHD
- particles
- self-gravity
- turbulence driving
- Z4c / ADM / dynamical GRMHD
- the shearing box

Only one ``method = cyclic_zoom`` criterion is supported. Do not combine it with
``min_max``, ``slope``, or ``location`` criteria in the same run.

Example inputs and tests
------------------------

Input files:

- ``inputs/zoom/zoom_bondi.athinput`` — GR Bondi accretion (hydro)
- ``inputs/zoom/zoom_monopole.athinput`` — GR magnetic monopole (MHD)
- ``inputs/zoom/zoom_torus.athinput`` — Fishbone–Moncrief torus (MHD; science example)

Regression tests live in ``tst/test_suite/zoom/``:

- ``test_zoom_bondi_mpicpu.py``
- ``test_zoom_monopole_gpu.py``

.. code-block:: bash

   ./build/src/athena \
     -i inputs/zoom/zoom_bondi.athinput \
     job/basename=zoom_bondi \
     time/tlim=100.0

Known limitations
-----------------

These are areas that may change as cyclic zoom is used for more applications:

- The zoom region is a sphere. A box-shaped region is not implemented.
- Restart files restore the zoom state and stored data, but a restarted run is not
  bitwise identical to a run without restart.
- The MHD correction maintains :math:`\nabla\cdot B = 0` via a :math:`\Delta E` source
  term, not a full constrained-transport rewrite of the zoom. ``emf_fmax`` and
  ``emf_zmax`` are the knobs for that correction.
- The first zoom-in of a run that starts at a coarse zone can fall back to a uniform
  ``d_zoom`` / ``p_zoom`` fill if no stored zoom mesh exists yet.
- Passive scalars are packed with the fluid variables but have not been tested.
- Radiation intensity is treated as a cell-centered field (same-level copy / coarse
  restriction). Coupled radiation-MHD science applications are less tested than
  hydro or MHD zoom.
