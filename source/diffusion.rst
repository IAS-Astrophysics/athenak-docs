Explicit Dissipation
====================

Diffusion processes implemented in AthenaK include:

- Hydrodynamic diffusion: fluid viscosity and thermal conduction
- Field diffusion: Ohmic diffusion

Input file
----------

Diffusive physics such as viscosity and/or thermal conduction can be constructed in
``<hydro>`` or ``<mhd>``. Ohmic diffusion is constructed in the ``<mhd>`` block. They are
enrolled in the corresponding block in the input file:

.. code-block:: text

   <hydro>
   viscosity    = 1.0e-3   # coefficient of isotropic shear viscosity
   conductivity = 1.0e-3   # coefficient of isotropic thermal conduction

or

.. code-block:: text

   <mhd>
   viscosity         = 1.0e-3   # coefficient of isotropic shear viscosity
   conductivity      = 1.0e-3   # coefficient of isotropic thermal conduction
   ohmic_resistivity = 0.01     # coefficient of Ohmic resistivity

Thermal conduction
------------------

The heat flux :math:`\boldsymbol{Q}` is defined by

.. math::

   \boldsymbol{Q} = -\mathcal{K}\nabla T,

where the coefficient :math:`\mathcal{K}` is the conductivity. The current implementation
uses a dimensionless system of units (see :doc:`units`) in that the factor
:math:`(\bar{m}/k_{\rm B})` is not included in calculating the temperature. Instead,
:math:`T = P/\rho` is adopted. Users must use dimensionless conductivity as the input
parameter.

.. note::

   The coefficient :math:`\mathcal{K}` corresponds to conductivity, **not** a diffusivity.
   This is different from the coefficient used in Athena++.
