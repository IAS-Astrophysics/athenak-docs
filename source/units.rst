Units
=====

AthenaK code units are dimensionless. The ``<units>`` infrastructure is designed to convert
physical variables to an equivalent dimensionless quantity in code by a scaling factor, and
vice versa. For any variable :math:`u`, we denote its units as :math:`u_0`, its value in code
units as :math:`u_\mathrm{code}`, and its value in physical units (e.g., cgs units) as
:math:`u_\mathrm{phy}`. Then we have

.. math::

   u_\mathrm{code} = u_\mathrm{phy}/u_0 \Longleftrightarrow u_\mathrm{phy} = u_\mathrm{code}\,u_0

For a unit system, the basic units include:

- length unit, :math:`l_0`
- time unit, :math:`t_0`
- mass unit, :math:`m_0`

Then, other units can be derived from these three units, e.g., velocity unit
:math:`v_0 = l_0/t_0`, density unit :math:`\rho_0 = m_0/l_0^3`, energy unit
:math:`e_0 = m_0 v_0^2`, and pressure unit :math:`P_0 = e_0/l_0^3`. As an option, mean
molecular weight, :math:`\mu`, can also be included in the units system to determine the
temperature unit. The temperature unit is given by

.. math::

   T_0 = P_0 \mu m_\mathrm{H}/(\rho_0 k_\mathrm{B}) = v_0^2 \mu m_\mathrm{H}/k_\mathrm{B},

where :math:`k_\mathrm{B}` is the Boltzmann constant and :math:`m_\mathrm{H}` is the atomic
mass unit. In this way, we have :math:`P_\mathrm{code} = \rho_\mathrm{code} T_\mathrm{code}`
in code.

The units system is initialized by the ``<units>`` block in the input file, including
length, ``length_cgs``, mass, ``mass_cgs``, and time, ``time_cgs``. As an option, mean
molecular weight can also be initialized by ``mu``. Default units are cgs units with
:math:`\mu = 1` if the ``<units>`` block is added.

As an example, for simulations of the interstellar medium, a useful unit system is

.. code-block:: text

   <units>
   length_cgs  = 3.0856775809623245e+18  # length is 1 pc
   mass_cgs    = 6.195900228622575e+31   # number density is 1 cm^-3
   time_cgs    = 3.15576e+13             # time is 1 Myr
   mu          = 1.27                    # mean molecular weight

General relativity
------------------

In General Relativistic (Magneto)hydrodynamics, the system of equations is scale invariant.
In this way, there exists freedom in manipulating, in any one simulation, (1) the density
scale :math:`\rho_0` to set the density, internal energy, and magnetic field strength in
physical units and (2) the black hole mass :math:`M` to set the physical length scale
:math:`l_0 = G M/c^2` (and hence timescale :math:`t_0 = l_0/c`) where :math:`G` is the
gravitational constant and :math:`c` is the speed of light (see `Wong et al. 2022
<https://arxiv.org/abs/2202.11721>`_ for a nice discussion).

In General Relativistic Radiation (Magneto)hydrodynamics (see :doc:`radiation`), however,
the system of equations is no longer scale invariant. Thus, one must specify the relevant
physical scales in the problem. Rather than specifying a length unit :math:`l_0`, mass unit
:math:`m_0`, and time unit :math:`t_0`, as described at the top, it is often easier to
specify a black hole mass :math:`M` and density unit :math:`\rho_0`. Given the gravitational
constant :math:`G`, speed of light :math:`c`, and the black hole mass :math:`M`, one can
derive the length scale :math:`l_0` and time scale :math:`t_0` in cgs units. Combined with a
density unit :math:`\rho_0`, the mass scale :math:`m_0` can then be derived. Finally, given
the mean molecular weight :math:`\mu` (same as above), one can infer the temperature unit
:math:`T_0`. Therefore, when working with General Relativistic Radiation
(Magneto)hydrodynamics, we enable the user to specify

.. code-block:: text

   <units>
   density_cgs = 1.0e-2  # density unit in g/cm3
   bhmass_msun = 10.0    # black hole mass in solar masses
   mu          = 0.5     # mean molecular weight (in amu)

.. note::

   In the above, the black hole mass **must be specified in solar masses**. The conversion
   of the black hole mass to cgs units is handled by the ``Units`` API.

In the codebase, one will notice that no ``Units`` member enters in the case of General
Relativistic (Magneto)hydrodynamics (which makes sense given the scale invariance). However,
in the case of General Relativistic Radiation (Magneto)hydrodynamics, if the ``<units>``
block is specified, units are heavily used in the radiation source term (see the **Coupling**
section of :doc:`radiation`).
