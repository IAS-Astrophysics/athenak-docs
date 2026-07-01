Hydrodynamics & MHD
===================

.. note::

   Documentation for the hydrodynamics and MHD modules is under construction.

AthenaK solves the equations of non-relativistic and relativistic (special and general)
hydrodynamics and magnetohydrodynamics. Physics is selected at run time by including the
``<hydro>`` or ``<mhd>`` block in the input file; the associated parameters (equation of
state, reconstruction, Riemann solver, floors, and so on) are read from that block. See
:doc:`input_file` for the general input-file structure and :doc:`faq` for the primitive and
conserved variable conventions.
