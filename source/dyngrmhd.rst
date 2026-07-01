GRMHD in Dynamical Spacetimes
=============================

Introduction
------------

There are two flux-conservative formulations of GRMHD in common use: a form derived from a
simple expansion of the divergence-free condition of the stress-energy tensor (sometimes
called the "HARM-like" formulation because of its use in the classic HARM code), and a form
derived from a 3+1 expansion of the same divergence-free condition (called the "3+1
formulation" or "Valencia formulation" because it was employed in early GR(M)HD papers by the
Valencia numerical relativity group). Both forms are physically identical, but they differ in
how they define the energy term. The HARM-like formulation can conserve energy perfectly to
machine precision in a stationary spacetime, while the Valencia formulation is more suitable
for dynamical spacetimes because it does not require explicit time derivatives of metric
quantities. AthenaK makes both forms available, but only the Valencia solver can be used in
generic spacetimes.

The 3+1 split is defined by a projection operator
:math:`\gamma_{\mu\nu} = g_{\mu\nu} + n_\mu n_\nu`, where :math:`n^\mu` is a unit time-like
normal vector with respect to a spatial slice (a three-dimensional spacelike hypersurface) of
spacetime. If we define :math:`n^\mu = (-1/\alpha, \beta^i/\alpha)` for a lapse function
:math:`\alpha` and shift vector :math:`\beta^i`, we can decompose the metric as follows:

.. math::

   g_{\mu\nu} dx^\mu dx^\nu = -\alpha^2 dt^2
     + \gamma_{ij}\left(\beta^i dt + dx^i\right)\left(\beta^j dt + dx^j\right),

where the spatial components of the projection operator, :math:`\gamma_{ij}`, are
collectively referred to as the "spatial metric". We can use this decomposition to rewrite
the GRMHD equations in a form more amenable for numerical relativity.

Consider a set of primitive variables :math:`\rho`, :math:`v^i`, and :math:`P`, which are the
rest-mass density, the three-velocity, and pressure, respectively. We can define a set of
conserved variables

.. math::
   :nowrap:

   \begin{align}
   D &= \rho W, \\
   S_i &= (\rho h W^2 + B^2)v_i - (B^j v_j) B_i, \\
   \tau &= \rho h W^2 + B^2 - P
     - \frac{1}{2}\left[\frac{B^2}{W^2} + (B^j v_j)^2\right] - D,
   \end{align}

where :math:`W = (1 - v^2)^{-1/2}` is the Lorentz factor,
:math:`h = 1 + \epsilon + P/\rho` is the total specific enthalpy (:math:`\epsilon` is the
specific internal energy), and :math:`B^i` is the magnetic field as measured by a normal
observer in the lab frame (i.e., :math:`B^i = n_\mu \left(\ast F\right)^{\mu i}`). The evolved
equations then take the form

.. math::
   :nowrap:

   \begin{align}
   \partial_t\left(\tilde{D}\right)
     + \partial_j\left(\alpha\tilde{D}\hat{v}^j\right) &= 0, \\
   \partial_t\left(\tilde{S}_i\right)
     + \partial_j\left[\alpha \tilde{S}_i\hat{v}^j - \alpha b_i \frac{B^j}{W}
     + \alpha\sqrt{\gamma}\left(P+\frac{b^2}{2}\right)\delta^j_i\right]
     &= \frac{1}{2}\alpha\tilde{S}^{jk}\partial_i\gamma_{jk}
     + \tilde{S}_j\partial_i\beta^j - \tilde{E}\partial_i\alpha, \\
   \partial_t\left(\tilde{\tau}\right)
     + \partial_j\left[\alpha\tilde{\tau}\hat{v}^j - \alpha^2 b^0\frac{\tilde{B}^j}{W}
     + \alpha\sqrt{\gamma}\left(P+\frac{b^2}{2}\right)\right]
     &= \alpha K_{ij}\tilde{S}^{ij} - \tilde{S}^i\partial_i\alpha, \\
   \partial_t\left(\tilde{B}^i\right)
     + \partial_j\left(\alpha\left[\tilde{B}^i \hat{v}^j
     - \tilde{B}^j \hat{v}^i\right]\right) &= 0,
   \end{align}

where :math:`\gamma = \det(\gamma_{ij})`, :math:`\tilde{A} = \sqrt{\gamma} A`,
:math:`\hat{v}^i = v^i - \beta^i/\alpha`, :math:`b^\mu = u_\nu\left(\ast F\right)^{\nu\mu}` is
the magnetic field in the fluid frame, and :math:`E = \tau + D`. Note that though these
equations appear to be different than those used in the typical HARM-like formulation, the
only truly different equation is the energy equation: :math:`\tilde{D}=\sqrt{-g}\rho u^0`,
:math:`\tilde{S}_i = \sqrt{-g}T^0_i`, and :math:`\tilde{B}^i = \sqrt{-g}\bar{B}^i`, where
:math:`\bar{B}^i` is the magnetic field in the coordinate frame as used in HARM-like
formulations.

The energy equation is derived by performing a 3+1 decomposition on
:math:`\nabla_\nu\left(n_\mu T^{\mu\nu}\right) = T^{\mu\nu}\nabla_\nu n_\mu`.

Enabling the Valencia solver
----------------------------

The Valencia solver can be enabled by starting with a standard GRMHD parfile and adding an
``<adm>`` or ``<z4c>`` block. There are a few new ``<mhd>`` parameters available for the
Valencia solver:

- ``mhd/dyn_eos``: the PrimitiveSolver EOS (currently supports ``ideal`` for an ideal gas,
  ``piecewise_poly`` for piecewise polytropes, and ``hybrid`` or ``eos_compose`` for a
  tabulated EOS in the PyCompOSE format). See :doc:`dyngrmhd_eos` for more information. Note
  that ``mhd/eos`` must still be defined as ``ideal`` no matter what ``dyn_eos`` is; this
  inconvenience is for historical reasons and will hopefully be patched in a future update.
- ``mhd/dyn_error``: the error policy used by PrimitiveSolver. Currently ``reset_floor`` is
  the only supported option.
- ``mhd/tfloor``: set an atmosphere for temperature (``mhd/pfloor`` is unused by the Valencia
  solver).
- ``mhd/s<n>_atmosphere``: set the atmosphere for scalar #``<n>``. Scalars are not directly
  floored (though a limiter defined by the EOS is applied during the conservative-to-primitive
  inversion), so this is a true atmosphere value and not a floor.
- ``mhd/dthreshold``: set the floor thresholding coefficient :math:`f_\mathrm{thr}` such that
  the density is reset to atmosphere when :math:`\rho < f_\mathrm{thr}\rho_\mathrm{atmo}`.
  Default is 1.0.
- ``mhd/enforce_maximum``: use FOFC to enforce a relaxed discrete maximum principle (see
  `arXiv:2409.10384 <https://arxiv.org/abs/2409.10384>`_). Not usually necessary, but can
  improve stability in some circumstances.
- ``mhd/dmp_M``: the constant :math:`M \ge 1` for the relaxed DMP above; this sets the
  permitted range without enabling FOFC to :math:`A\in [A_\mathrm{min}/M, M A_\mathrm{max}]`,
  where :math:`A\in\{\tilde{D},\tilde{\tau}\}`.

If only the ``<adm>`` block is present, the Valencia GRMHD solver is enabled but the spacetime
is not evolved, making it possible to do GRMHD in a fixed but otherwise generic spacetime as
defined by the problem generator. However, for all non-Minkowski spacetimes, the problem
generator must set ``ADM::SetADMVariables`` to a function pointer which can update the metric
in order to be compatible with AMR. This same functionality can also be used for analytic or
semi-analytic time-dependent metrics (e.g., FLRW), which can be enabled in the parameter file
with ``adm/dynamic = true``.

Evolution and output details
----------------------------

- Reconstruction is performed on :math:`\rho`, :math:`W v^i`, :math:`P`, scalar fractions
  :math:`Y^i`, and :math:`\tilde{B}^i`.
- Conserved variables are stored densitized by the volume form, e.g., :math:`\tilde{D}` is
  stored, not :math:`D`.
- There is support for the LLF (``mhd/rsolver = llf``) and HLLE (``mhd/rsolver = hlle``)
  approximate Riemann solvers.
- The conserved-to-primitive inversion is based off the `PrimitiveSolver
  <https://github.com/jfields7/primitive-solver>`_ library, which implements a slightly
  modified version of the `RePrimAnd <https://github.com/wokast/RePrimAnd>`_ algorithm (see
  `arXiv:2005.01821 <https://arxiv.org/abs/2005.01821>`_).
- Primitive variable output (``mhd_w_bcc``) contains :math:`\rho`, :math:`W v^i`, :math:`P`,
  :math:`Y^i`, temperature :math:`T`, and :math:`\tilde{B}^i`.
- Conserved variable output (``mhd_u_bcc``) contains :math:`\tilde{D}`, :math:`\tilde{S}_i`,
  :math:`\tilde{\tau}`, :math:`\tilde{D}Y^i`, and :math:`\tilde{B}^i`.

TOV problems
------------

A standard TOV neutron star (in either Cartesian Schwarzschild or isotropic coordinates) with
an optional poloidal magnetic field is available via the problem generator
``-DPROBLEM=dyngr_tov``. The solver uses the shooting method with an RK4 integrator to solve
the TOV equations assuming a barotropic EOS based on the EOS defined by ``mhd/dyn_eos``. The
parameters under ``<problem>`` are as follows.

Integration parameters
~~~~~~~~~~~~~~~~~~~~~~~~

- ``rhoc``: central density of the TOV
- ``npoints``: buffer size for TOV integration
- ``dr``: radial step for the RK4 integrator
- ``rho_cut``: density floor for determining the stopping condition during integration. This
  is particularly useful for tabulated equations of state. By default, it is set to
  :math:`10^{-10}\rho_c`.

EOS parameters
~~~~~~~~~~~~~~~

- ``kappa``: if ``mhd/dyn_eos = ideal``, the corresponding polytropic constant for an EOS of
  the form :math:`P = K\rho^\Gamma`, where :math:`\Gamma` is defined by ``mhd/gamma``.
- ``table``: if using ``mhd/dyn_eos = eos_compose``, an appropriate 1D slice in the
  `PyCompOSE <https://github.com/computationalrelativity/PyCompOSE>`_ format stored in a
  ``.athtab`` binary table.

No additional parameters are necessary for piecewise polytropes, which use the same parameters
as those specified in ``mhd/dyn_eos``.

Other parameters and physics options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``isotropic``: whether to use isotropic coordinates (``true``) or Cartesian Schwarzschild
  (``false``, default).
- ``minkowski``: solve the correct TOV equations but initialize the metric with Minkowski
  space instead (``false``). This can be useful for debugging.
- ``v_pert``: magnitude :math:`U` of a velocity perturbation of the form
  :math:`Wv^r = \frac{1}{2} U (3(r/R_\ast) - (r/R_\ast)^3)`, where :math:`R_\ast` is the TOV
  radius in the appropriate coordinates.
- ``p_pert``: magnitude :math:`P_\mathrm{pert}` of a random perturbation to the pressure.
- ``b_norm``: magnitude of a poloidal magnetic field initialized with the vector potential
  :math:`A_\phi = \max\{P-P_\mathrm{cut},0\}\times(1-\rho/\rho_c)^m`.
- ``pcut``: pressure cutoff :math:`P_\mathrm{cut}` for the magnetic field.
- ``use_pcut_rel``: whether :math:`P_\mathrm{cut}` is an absolute cutoff (``false``, default)
  or relative to the central pressure :math:`P_c`.
- ``magindex``: exponent :math:`m` for the magnetic field.

The TOV solver is independent of the problem generator and available via
``utils/tov/tov.hpp``, so it is also possible to write your own problem generator using the
TOV solver. See ``pgen/dyngr_tov.cpp`` for an example on how to use it.

BNS problems
------------

AthenaK currently supports binary neutron star initial data made with `LORENE
<https://lorene.obspm.fr/>`_, `sgrid <https://github.com/sgridsource/sgrid>`_, and `Elliptica
<https://github.com/rashti-alireza/Elliptica_ID_Reader>`_. To compile, configure AthenaK
appropriately for your system and set ``-DPROBLEM`` to ``lorene_bns``, ``sgrid_bns``, or
``elliptica_bns``. To link against the correct initial data library, create a symbolic link
(``ln -s <target> <link_name>``) in the repository base directory of AthenaK to the base
directory for the initial data library and title it ``Lorene``, ``sgrid``, or
``Elliptica_ID_Reader``. CMake will automatically configure AthenaK to look for the correct
headers and libraries inside these directories.

Both ``lorene_bns`` and ``elliptica_bns`` expect a single parameter,
``problem/initial_data_file``, which is the filename for the initial data.

To use the compact object trackers with neutron stars, add the following lines to the
parameter file under ``<z4c>``:

.. code-block:: text

   nco = 2
   co_0_type = NS
   co_0_x = <x position of first star>
   co_0_y = <y position of first star>
   co_0_radius = <radius of first star>
   co_1_type = NS
   co_1_x = <x position of second star>
   co_1_y = <y position of second star>
   co_1_radius = <radius of second star>

If AMR is enabled, it can follow the trackers by setting ``z4c_amr/method = tracker``.
