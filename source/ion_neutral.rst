Ion-Neutral Fluids
==================

Introduction
------------

The ion–neutral module evolves a partially ionized plasma as **two coupled fluids**: a
magnetized ion fluid (solved with the MHD solver) and a neutral fluid (solved with the hydro
solver). The two fluids exchange momentum through a collisional drag term and, optionally,
mass through ionization and recombination. Because the drag can be stiff, the coupling is
integrated implicitly using an ImEx (implicit–explicit) Runge–Kutta scheme, while the fluxes
of each fluid are still handled explicitly.

The physical model for the momentum and mass exchange is

.. math::

   \mathbf{F} = -\gamma \rho_i \rho_n (\mathbf{u}_i - \mathbf{u}_n)
     + \xi \rho_n \mathbf{u}_n - \alpha \rho_i^2 \mathbf{u}_i,
   \qquad
   G = \xi \rho_n - \alpha \rho_i^2,

where subscripts :math:`i` and :math:`n` denote the ion and neutral fluids, :math:`\gamma` is
the drag coefficient, :math:`\xi` the ionization rate, and :math:`\alpha` the recombination
rate.

Inputs
------

Ion–neutral runs require **three** blocks in the input file:

- ``<hydro>`` — configures the **neutral** fluid (see :doc:`hydro`);
- ``<mhd>`` — configures the **ion** fluid (see :doc:`mhd`);
- ``<ion-neutral>`` — configures the coupling (note the hyphen in the block name).

The ``<ion-neutral>`` block has three parameters:

- ``drag_coeff`` (**mandatory**): the ion–neutral drag coupling coefficient :math:`\gamma`.
- ``ionization_coeff`` (default ``0.0``): the ionization rate :math:`\xi`.
- ``recombination_coeff`` (default ``0.0``): the recombination rate :math:`\alpha`.

.. note::

   - Whenever both ``<hydro>`` and ``<mhd>`` are present, the ``<ion-neutral>`` block is
     **required** (and vice versa) — a single run cannot otherwise contain both fluids.
   - The time integrator **must** be an ImEx scheme: set ``<time>/integrator`` to ``imex2``,
     ``imex2+``, or ``imex3``. Explicit integrators (``rk1``–``rk4``) will abort.

Outputs
-------

There are no ion-neutral-specific output variables. Instead, write the two fluids using their
respective standard variables (see :doc:`hydro`, :doc:`mhd`, and :doc:`outputs`):

- the **neutral** fluid via ``hydro_w`` (or ``hydro_u``, individual components, etc.);
- the **ion** fluid via ``mhd_w_bcc`` (primitives plus the cell-centered magnetic field).

Example: a perpendicular C-shock
--------------------------------

A C-shock (continuous shock) is a steady, magnetically moderated shock structure that arises
in weakly ionized media when the neutrals stream through the magnetized ions. AthenaK provides
a 1D test at ``inputs/ion-neutral/perp_cshock.athinput`` using the built-in ``cshock`` problem
generator.

**1. Build** (the ``cshock`` generator is built in, so the default build suffices):

.. code-block:: bash

   cmake -B build
   cmake --build build -j

**2. Note the setup.** The input file couples an isothermal ion (MHD) and neutral (hydro)
fluid with an ImEx integrator and a unit drag coefficient:

.. code-block:: text

   <time>
   integrator = imex3      # ImEx integrator is required

   <ion-neutral>
   drag_coeff = 1.0

   <hydro>
   eos             = isothermal
   iso_sound_speed = 1.0

   <mhd>
   eos             = isothermal
   iso_sound_speed = 1.0

**3. Slightly modify it.** The shipped file writes ``.tab`` line-outs; to make the drag
coupling more visible you can raise the drag coefficient, which compresses the shock front:

.. code-block:: text

   <ion-neutral>
   drag_coeff = 2.0

**4. Run and visualize.** For 1D runs the ``.tab`` text output is convenient. Each line-out
file (named ``<basename>.<variable>.<number>.tab``) has columns ``gid i x1v dens velx vely
velz``, so the neutral density profile can be plotted directly:

.. code-block:: bash

   ./build/src/athena -i inputs/ion-neutral/perp_cshock.athinput -d run

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt

   d = np.loadtxt("run/tab/cshock.hydro_w.00040.tab")   # columns: gid i x1v dens velx ...
   x, dens, velx = d[:, 2], d[:, 3], d[:, 4]

   fig, ax = plt.subplots()
   ax.plot(x, dens, label="neutral density")
   ax.set_xlabel("x"); ax.set_ylabel("density")
   fig.savefig("cshock_dens.png", dpi=150)

The neutral density rises smoothly across the C-shock rather than through a sharp
discontinuity (shown here together with the neutral velocity):

.. image:: /_static/cshock.png
   :alt: Neutral density profile across a perpendicular C-shock
   :align: center
   :width: 75%

Overlaying the ion density (from the ``mhd_w_bcc`` output) shows how the two fluids decouple
in the shock front, with the separation set by ``drag_coeff``.
