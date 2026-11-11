Static Mesh Refinement
======================

AthenaK supports both static and adaptive mesh refinement through the
``<mesh_refinement>`` block. This page covers the shared refinement controls and static
mesh refinement (SMR); see :doc:`amr` for adaptive refinement.

Shared controls in ``<mesh_refinement>``
----------------------------------------

- ``refinement``: ``static`` or ``adaptive``
- ``num_levels``: maximum number of levels including the root grid (``num_levels = 1``
  means no refinement); read only for adaptive refinement
- ``max_nmb_per_rank``: cap on the number of MeshBlocks per MPI rank; required for adaptive
  refinement, not used for SMR

For adaptive runs, ``refinement_interval`` additionally controls the AMR regrid cadence
in cycles (see :doc:`amr`).

Configuring SMR
---------------

Static mesh refinement uses fixed geometric regions that stay refined for the entire
run. To enable it, set:

.. code-block:: text

   <mesh_refinement>
   refinement = static

Then add one or more ``<refined_regionN>`` blocks (numbered from 1) that specify the
extent and level of each refined region:

.. code-block:: text

   <refined_region1>
   level = 1
   x1min = 1.2
   x1max = 1.8
   x2min = 0.7
   x2max = 0.8
   x3min = 0.7
   x3max = 0.8

Representative input
--------------------

- ``inputs/tests/linear_wave_hydro_smr.athinput``

Setup checklist
---------------

- Ensure refined regions stay inside the root mesh bounds.
- Keep region dimensions aligned with your mesh/MeshBlock decomposition.
- Start with a single region and validate the output before stacking multiple regions.
