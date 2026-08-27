Adaptive Mesh Refinement
========================

Adaptive mesh refinement (AMR) dynamically refines or derefines MeshBlocks based on
criteria evaluated during the run. AMR shares the ``<mesh_refinement>`` controls
described in :doc:`smr`.

Configuring AMR
---------------

Set ``refinement = adaptive`` in ``<mesh_refinement>`` and choose the number of levels,
regrid cadence, and per-rank block cap:

.. code-block:: text

   <mesh_refinement>
   refinement          = adaptive
   num_levels          = 2
   refinement_interval = 3
   max_nmb_per_rank    = 1024

Then add one or more ``<amr_criterionN>`` blocks (numbered from 0), for example:

.. code-block:: text

   <amr_criterion0>
   # Refine on slopes of the rest-mass density > 0.1
   method    = slope
   variable  = hydro_w_d
   value_max = 0.1

   <amr_criterion1>
   # Refine where the lab-frame density is < 1e-6
   method    = min_max
   variable  = hydro_u_d
   value_min = 1e-6

   <amr_criterion2>
   # Refine a cube with half-width 5 around the origin
   method       = location
   location_x1  = 0.0
   location_x2  = 0.0
   location_x3  = 0.0
   location_rad = 5.0

.. note::

   The ``<refined_regionN>`` blocks used for SMR can be used to seed the mesh with an
   initial refinement structure. However, the AMR criteria will **not** preserve these
   structures on the next refinement cycle. If parts of your mesh need to remain refined
   no matter what, use the ``location`` criterion instead.

AMR criterion methods
---------------------

The ``method`` parameter can take the following arguments:

- ``min_max``: refine based on the minimum or maximum of ``variable``.
- ``slope``: refine based on the slope of ``variable``.
- ``second_deriv``: refine based on the second derivative of ``variable``.
- ``location``: refine a cube centered on the specified location with a given side
  half-length. This is useful if part of the mesh should always be refined independent
  of the refinement criteria.
- ``cyclic_zoom``: cycle between refining and coarsening a spherical region, storing
  fine-grid data so small-scale structure can be restored on zoom-in. See
  :doc:`cyclic_zoom`.
- ``user``: refine based on a user-specified refinement criterion in the problem
  generator (see :ref:`custom-refinement-criteria`).

Known criterion variables
-------------------------

Presently the only supported refinement variables for ``min_max``, ``slope``, or
``second_deriv`` are:

- ``hydro_w_d``, ``hydro_u_d``
- ``mhd_w_d``, ``mhd_u_d``
- ``rad_coord_e``

See `issue #658 <https://github.com/IAS-Astrophysics/athenak/issues/658>`_. If an
unknown variable is requested in ``<amr_criterionN>``, AthenaK aborts.

.. _custom-refinement-criteria:

Custom refinement criteria
--------------------------

If ``method = user``, you must supply a custom refinement function inside the problem
generator. We use the Z4c linear wave test problem
(``src/pgen/tests/z4c_linear_wave.cpp``) as an example.

First, the refinement function must be a ``void`` function that takes a pointer to the
``MeshBlockPack`` as a parameter, e.g.:

.. code-block:: c++

   void RefinementCondition(MeshBlockPack* pmbp);

The ``ProblemGenerator`` class has a member variable, ``user_ref_func``, which is a
function pointer to the refinement function. The problem generator therefore must assign
this function:

.. code-block:: c++

   void ProblemGenerator::Z4cLinearWave(ParameterInput* pin, const bool restart) {
     ...
     user_ref_func = RefinementCondition;
     ...
   }

The refinement function then loops over all MeshBlocks and sets their refinement flag
(``refine_flag.d_view(m)``) to refine (``1``), coarsen (``-1``), or do nothing (``0``).
For example, the Z4c linear wave criterion marks a block for refinement if the metric
component :math:`\gamma_{xy}` is positive at any point, otherwise it marks it to be
coarsened:

.. code-block:: c++

   void RefinementCondition(MeshBlockPack* pmbp) {
     auto &refine_flag = pmbp->pmesh->pmr->refine_flag;
     int I_Z4C_GXY  = pmbp->pz4c->I_Z4C_GXY;
     int nmb           = pmbp->nmb_thispack;
     auto &indcs       = pmbp->pmesh->mb_indcs;
     int &is = indcs.is, nx1 = indcs.nx1;
     int &js = indcs.js, nx2 = indcs.nx2;
     int &ks = indcs.ks, nx3 = indcs.nx3;
     const int nkji = nx3 * nx2 * nx1;
     const int nji  = nx2 * nx1;
     int mbs           = pmbp->pmesh->gids_eachrank[global_variable::my_rank];
     auto &u0       = pmbp->pz4c->u0;

     par_for_outer("Z4c_AMR::GXYMAX", DevExeSpace(), 0, 0, 0, (nmb - 1),
     KOKKOS_LAMBDA(TeamMember_t tmember, const int m) {
       Real team_dmax;
       Kokkos::parallel_reduce(
         Kokkos::TeamThreadRange(tmember, nkji),
         [=](const int idx, Real &dmax) {
           int k = (idx) / nji;
           int j = (idx - k * nji) / nx1;
           int i = (idx - k * nji - j * nx1) + is;
           j += js;
           k += ks;
           dmax = fmax(u0(m, I_Z4C_GXY, k, j, i), dmax);
         },
         Kokkos::Max<Real>(team_dmax));

       if (team_dmax > 0) {
         refine_flag.d_view(m + mbs) = 1;
       } else {
         refine_flag.d_view(m + mbs) = -1;
       }
     });

     // sync host and device
     refine_flag.template modify<DevExeSpace>();
     refine_flag.template sync<HostMemSpace>();
   }

Refinement recipes
------------------

Blast wave with AMR
^^^^^^^^^^^^^^^^^^^

Input baseline: ``inputs/hydro/blast_hydro_amr.athinput``

.. code-block:: bash

   ./build/src/athena \
     -i inputs/hydro/blast_hydro_amr.athinput \
     job/basename=blast_amr \
     mesh_refinement/num_levels=2

MHD blast with AMR
^^^^^^^^^^^^^^^^^^

Input baseline: ``inputs/mhd/blast_mhd_amr.athinput``

.. code-block:: bash

   ./build/src/athena \
     -i inputs/mhd/blast_mhd_amr.athinput \
     job/basename=mhd_blast_amr

Z4c with AMR
^^^^^^^^^^^^

Input baselines:

- ``inputs/z4c/onepuncture/z4c_onepuncture_amr.athinput``
- ``inputs/z4c/twopuncture/z4c_twopuncture_amr_criterion.athinput``

.. code-block:: bash

   ./build/src/athena \
     -i inputs/z4c/onepuncture/z4c_onepuncture_amr.athinput \
     job/basename=z4c_amr_smoke \
     time/tlim=5.0

Cyclic zoom
^^^^^^^^^^^

Input baselines:

- ``inputs/zoom/zoom_bondi.athinput``
- ``inputs/zoom/zoom_monopole.athinput``

See :doc:`cyclic_zoom` for parameters, supported physics, and limitations.

.. code-block:: bash

   ./build/src/athena \
     -i inputs/zoom/zoom_bondi.athinput \
     job/basename=zoom_bondi \
     time/tlim=100.0

Tuning checklist
----------------

- Start with a conservative ``num_levels`` (1--2).
- Set ``max_nmb_per_rank`` to avoid runaway block counts.
- Tune ``value_max`` / ``value_min`` in small steps.
- Use short runs first (``time/tlim`` and ``time/nlim`` overrides).

Representative AMR inputs
-------------------------

- ``inputs/tests/linear_wave_hydro_amr.athinput``
- ``inputs/hydro/blast_hydro_amr.athinput``
- ``inputs/mhd/blast_mhd_amr.athinput``
- ``inputs/zoom/zoom_bondi.athinput``
- ``inputs/zoom/zoom_monopole.athinput``
