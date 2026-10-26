Numerical Relativity
====================

Introduction
------------

AthenaK includes a Z4c numerical relativity module for evolving dynamical spacetimes. This
page describes how to enable the Z4c solver and run a binary black hole (BBH) problem.
For GRMHD in dynamical spacetimes, see :doc:`dyngrmhd`.

For details on the Z4c formalism as used in AthenaK, please refer to
`arXiv:2101.08289 <https://arxiv.org/abs/2101.08289>`_ and
`arXiv:2409.10383 <https://arxiv.org/abs/2409.10383>`_. The description is quite lengthy,
so it will not be included here.

Enabling the Z4c solver
-----------------------

To enable Z4c, add a ``<z4c>`` block to the input file. ``<z4c>`` currently takes the
following parameters to control the Z4c equations:

- ``chi_psi_power``: Sets the exponent in :math:`\psi^4 = \chi^{4/p}` (default: ``-4``)

- ``chi_div_floor``: Minimum value of :math:`\chi` allowed inside division (default:
  ``-1000.0``))

- ``chi_min_floor``: Minimum value of :math:`\chi` when ``floor_chi`` is enabled (default:
  ``1e-12``)

- ``floor_chi``: Force :math:`\chi` to stay above ``chi_min_floor`` (default: ``false``)

- ``diss``: Strength of Kreiss-Oliger dissipation (default: ``0.0``)

- ``damp_kappa1``: Constraint-damping parameter :math:`\kappa_1` (default: ``0.0``)

- ``damp_kappa2``: Constraint-damping parameter :math:`\kappa_2` (default: ``0.0``)

- ``use_z4c``: Whether or not to use Z4c; setting this to false forces :math:`\Theta = 0`,
  which effectively reduces the equations to the BSSN system instead (default: ``true``)

Spatial order
~~~~~~~~~~~~~

The ``spatial_order`` parameter in ``<z4c>`` selects second-, fourth-, or sixth-order
spatial derivatives (``2``, ``4``, or ``6``). This can be set independently of the
number of ghost cells allocated by ``mesh/nghost``. Supported ghost widths are ``2``
through ``4``, with at least ``spatial_order/2 + 1`` ghost cells. For example,

.. code-block:: text

   <mesh>
   nghost = 4

   <z4c>
   spatial_order = 4

uses fourth-order derivatives with four allocated ghost cells. If ``spatial_order`` is
omitted, the order defaults to ``2*(nghost - 1)``.

The selection applies to Z4c derivatives and dissipation, ADM conversion and
constraints, Weyl scalars, curvature diagnostics, and FastFlow derivatives. Sommerfeld
boundaries still use second-order derivatives. This parameter does not change the fluid
reconstruction or time integration order.

Lapse and shift conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters control the standard lapse condition:

- ``lapse_harmonicf``: Enables the :math:`\alpha` term (default: ``1.0``)

- ``lapse_harmonic``: Enable the :math:`\alpha^2` term (default: ``0.0``)

- ``lapse_oplog``: Controls the weight of the :math:`\alpha` term (default: ``2.0``)

- ``lapse_advect``: Enable the advection/Lie derivative term (default:
  ``1.0``)

AthenaK also supports a slow-start lapse (see
`arXiv:2404.01137 <https://arxiv.org/abs/2404.01137>`_) controlled with the following
parameters:

- ``slow_start_lapse``: Enable SSL (default: ``false``)

- ``ssl_damping_amp``: The strength of the gauge-damping (default: ``0.6``)

- ``ssl_damping_time``: The characteristic decay time for the gauge-damping (default:
  ``20.0``)

- ``ssl_damping_index``: The power scaling for the :math:`W = \chi^{1/2}` factor (default:
  ``1.0``)

An additional telegraph lapse term can be enabled with the following parameters:

- ``telegraph_lapse``: Enable the auxiliary lapse fields (default: ``false``)

- ``telegraph_tau``: Relaxation time, which must be finite and positive (default:
  ``0.1``)

- ``telegraph_kappa``: Coupling strength, which must be finite and nonnegative
  (default: ``0.1``)

When enabled, AthenaK evolves an auxiliary covector :math:`B_i` according to

.. math::

   (\partial_t - f_{\mathrm{adv}}\beta^j\partial_j) B_i
   = \frac{\kappa\partial_i\alpha - B_i}{\tau},

where :math:`f_{\mathrm{adv}}` is ``lapse_advect``. The term
:math:`\gamma^{ij}\partial_i B_j` is added to the lapse equation. This uses partial
derivatives, rather than a covariant divergence. The auxiliary fields start at zero and
have covector parity at reflecting boundaries. The timestep includes limits from the
relaxation time and the additional metric-dependent characteristic speed. Choose the CFL
number and check convergence for the intended problem.

The shift gauge contains both gamma-driver and harmonic gauge terms. The gamma-driver
terms are enabled by default. The parameters are as follows:

- ``shift_Gamma``: Enable the :math:`\Gamma^i` term (default: ``1.0``)

- ``shift_advect``: Enable the advection/Lie derivative term (default: ``1.0``)

- ``shift_eta``: Coefficient for decay term (default: ``2.0``)

- ``shift_alpha2Gamma``: Enable the :math:`\alpha^2 \Gamma^i` harmonic gauge term
  (default: ``0.0``)

- ``shift_H``: Enable the :math:`\alpha\chi\left(\alpha\partial_i \chi/2 - 
  \partial_i \alpha\right)\tilde{\gamma}^{ij}` harmonic gauge term (default: ``0.0``)

There are also the following miscellaneous parameters:

- ``user_Sbc``: Whether or not custom user boundaries should use a Sommerfeld condition
  (default: ``false``)

- ``excise_chi``: Excise regions where :math:`\chi` falls below this in the history
  output. This is useful for excluding punctures, which tend to dominate errors in the
  solution, from constraint violation calculations. (default: ``0.0625``)

- ``extrap_order``: The extrapolation order used for ``outflow`` boundaries (can be set
  to ``2`` for linear , ``3`` for quadratic, and ``4`` for cubic extrapolation, default:
  ``2``)

Wave extraction
---------------
AthenaK can compute the Weyl scalar :math:`\Psi_4`, which encodes the outgoing
gravitational radiation, over spherical surfaces at finite radii. This can then be used to
compute the gravitational wave strain in post-processing. Waveform extraction is
controlled by the following parameters:

- ``nrad_wave_extraction``: The number of extraction surfaces. Setting to ``0`` disables
  wave extraction (default: ``0``)

- ``extraction_nlev``: The subdivision level for the spherical surfaces used to compute
  :math:`\Psi_4` (default: ``10``)

- ``extraction_radius_?``: The extraction radius for surface ``?`` (zero-indexed)
  (default: ``10``)

- ``waveform_dt``: The time between waveform outputs in code units (default: ``1``)

Alternatively, AthenaK can also write out the data needed for Cauchy-characteristic
extraction (CCE) in the format expected by the `SpECTRE <https://spectre-code.org/>`_ CCE
module.

CCE output is enabled with a ``<cce>`` block, for example:

.. code-block:: text

   <cce>
   num_radii = 1
   rin_0 = 20.0
   rout_0 = 40.0
   num_l_modes = 16
   num_radial_modes = 7
   cce_dt = 1.0

The parameters are as follows:

- ``num_radii``: Number of extraction shells. Setting to ``0`` disables CCE output
  (default: ``0``)

- ``rin_N`` and ``rout_N``: Inner and outer radii for shell ``N``, starting at ``0``.
  The radii must satisfy :math:`0 < r_{\mathrm{in}} < r_{\mathrm{out}}` (defaults:
  ``20.0`` and ``40.0``)

- ``num_l_modes``: Largest spherical-harmonic degree :math:`\ell`, which must be
  nonnegative (default: ``16``)

- ``num_radial_modes``: Number of radial samples, which must be at least ``1``
  (default: ``7``)

- ``cce_dt``: Time between CCE outputs in code units (default: ``1.0``)

The shells are centered at the coordinate origin and must lie within the computational
domain. Each shell samples the lapse, three shift components, and six spatial metric
components. Angular sampling uses a Gauss-Legendre grid with
:math:`n_\theta = \ell_{\max}+1` and :math:`n_\phi = 2n_\theta`. For ``N`` radial
samples, the radii are

.. math::

   r_k = \frac{r_{\mathrm{in}}+r_{\mathrm{out}}}{2}
       - \frac{r_{\mathrm{out}}-r_{\mathrm{in}}}{2}
         \cos\left(\frac{(k+1)\pi}{N+1}\right),
   \qquad k=0,\ldots,N-1.

These are the roots of the second-kind Chebyshev polynomial mapped to the shell.
Spherical-harmonic coefficients use the complex conjugate of :math:`Y_{\ell m}` in
the projection.

Files are written to ``cce/cce_<time>.bin`` for shell ``0`` and
``cce/cce_shellN_<time>.bin`` for subsequent shells. Times use full-precision scientific
notation. Each file begins with two integers (the number of radial samples and
:math:`\ell_{\max}`), followed by three ``Real`` values (time, inner radius, and outer
radius). The real coefficient array is followed by the imaginary coefficient array.
Each array has shape ``[num_radial_modes, 10, (num_l_modes + 1)**2]`` in C order, with
angular index :math:`\ell^2+\ell+m`. The ten fields are ordered as lapse, shift
:math:`(x,y,z)`, and metric :math:`(xx,xy,xz,yy,yz,zz)`. ``Real`` is double precision
unless AthenaK is built with single precision.

.. note::

   The radial nodes and imaginary coefficient signs correct the earlier CCE output
   convention. Post-processing tools should use the nodes and conjugated projection
   described above when reading new output.

Horizon data dumps
------------------

AthenaK can interpolate the lapse, shift, spatial metric, and extrinsic curvature onto a
Cartesian grid around a tracked compact object for external horizon analysis. For
example,

.. code-block:: text

   <z4c>
   co_0_type = BH
   co_0_x = 0.0
   co_0_y = 0.0
   co_0_z = 0.0
   dump_horizon_0 = true
   co_0_dump_radius = 2.0
   horizon_0_Nx = 32
   horizon_dt = 1.0
   co_0_dump_cheb = false
   horizon_0_rn = 0

A dump requires a matching compact-object tracker. Trackers and enabled dumps are
numbered consecutively from ``0``. The parameters in ``<z4c>`` are:

- ``dump_horizon_N``: Enable a dump for tracker ``N`` (default: ``false``)

- ``co_N_dump_radius``: Half-width of the Cartesian grid (default: ``2.0``)

- ``horizon_N_Nx``: Number of points per axis, including endpoints; must be at least
  ``2`` (default: ``10``)

- ``horizon_dt``: Time between dumps in code units (default: ``1.0``)

- ``co_N_dump_cheb``: Use Chebyshev-Lobatto points instead of uniformly spaced points
  (default: ``false``)

- ``horizon_N_rn``: Nonnegative integer power :math:`n` for radial regularization.
  The interpolator applies the stencil to :math:`r^n f` and divides the result by
  :math:`r^n`, with radius measured from the grid center. At the center it uses the
  ordinary stencil to avoid division by zero (default: ``0``, disabled)

- ``horizonNr_guess``: Initial radius guess used in the generated Einstein Toolkit
  parameter file, e.g., ``horizon0r_guess`` (default: ``0.5``)

Each dump is written in ``horizon_N/output_M/``. The binary file
``etk_output_file.dat`` begins with an integer common-horizon flag and the time as a
``Real``, followed by 16 fields in the order lapse, shift :math:`(x,y,z)`, metric
:math:`(xx,xy,xz,yy,yz,zz)`, and extrinsic curvature :math:`(xx,xy,xz,yy,yz,zz)`.
The field array has shape ``[16, Nx, Nx, Nx]`` in C order, with :math:`x` varying
fastest. Older dumps used a different axis order.

The accompanying ``coordinates.txt`` contains three columns giving the one-dimensional
:math:`x`, :math:`y`, and :math:`z` coordinate arrays. Uniform coordinates run from
center minus half-width to center plus half-width. Chebyshev coordinates follow
:math:`x_q = x_c + R\cos(q\pi/(N_x-1))`, and similarly for :math:`y` and :math:`z`.
Grid coordinates and interpolation weights follow the tracker and are refreshed after
AMR changes. Einstein Toolkit parameter files are generated only for uniform grids;
Chebyshev consumers must use the explicit coordinates.

Refinement
----------

The ``max_ref_lev`` parameter in ``<z4c_amr>`` limits refinement requested by the Z4c
criteria. Nonnegative values count levels above the root grid; ``0`` prevents further
Z4c refinement. The default is ``-1``, which disables the cap. For example,

.. code-block:: text

   <z4c_amr>
   method = chi
   chi_min = 0.2
   max_ref_lev = 4

applies the chi criterion up to four levels above the root grid. The cap is applied
after the chi, dchi, tracker, or radius criterion, and blocks above the cap request
derefinement. Mesh balancing and independently registered refinement criteria are still
handled by the AMR driver. See :doc:`amr` for the mesh refinement controls.

Outputs
-------

Z4c variables (included in output ``z4c``):

- :math:`\chi`: ``z4c_chi``

- :math:`\tilde{\gamma}_{ij}`: ``z4c_gxx``, ``z4c_gxy``, ``z4c_gxz``, ``z4c_gyy``,
  ``z4c_gyz``, and ``z4c_gzz``

- :math:`\hat{K}`: ``z4c_Khat``

- :math:`\tilde{A}_{ij}`: ``z4c_Axx``, ``Z4c_Axy``, ``Z4c_Axz``, ``Z4c_Ayy``, ``Z4c_Ayz``,
  ``Z4c_Azz``

- :math:`\tilde{\Gamma}^i`:  ``z4c_Gamx``, ``z4c_Gamy``, ``z4c_Gamz``

- :math:`\Theta`: ``z4c_Theta``

- :math:`\alpha`: ``z4c_alpha``

- :math:`\beta^i`: ``z4c_betax``, ``z4c_betay``, and ``z4c_betaz``

- Telegraph lapse covector :math:`B_i`: ``z4c_Bx``, ``z4c_By``, and ``z4c_Bz``

ADM constraints (included in output ``con``):

- :math:`\mathcal{C}^2`: ``con_C``

- :math:`\mathcal{H}`: ``con_H``

- :math:`\mathcal{M}_i\mathcal{M}^i`: ``con_M``

- :math:`\breve{Z}^i\breve{Z}_i`: ``con_Z``

- :math:`\mathcal{M}_i`: ``con_Mx``, ``con_My``, and ``con_Mz``

The ADM variables (included in output ``adm``):

- :math:`g_{ij}`: ``adm_gxx``, ``adm_gxy``, ``adm_gxz``, ``adm_gyy``, ``adm_gyz``, and
  ``adm_gzz``

- :math:`K_{ij}`: ``adm_Kxx``, ``adm_Kxy``, ``adm_Kxz``, ``adm_Kyy``, ``adm_Kyz``, and
  ``adm_Kzz``

- :math:`\psi^4`: ``adm_psi4``

The Weyl scalar (included in output ``weyl``):

- :math:`\mathrm{Re}(\Psi_4)`: ``weyl_rpsi4``

- :math:`\mathrm{Im}(\Psi_4)`: ``weyl_ipsi4``

As discussed in :doc:`dyngrmhd`, the ADM variables can exist independently of Z4c. In this
case, they will also include :math:`\alpha` and :math:`\beta^i`.

The history output (``jobname.z4c.user.hst``) will output 2-norms of various constraints:
:math:`||\mathrm{C}||_2`, :math:`||\mathrm{H}||_2`,
:math:`||\sqrt{\mathcal{M}_i\mathcal{M}^i}||_2`, :math:`||\mathcal{M_i}||_2`, and
:math:`||\Theta||_2`. The history output will also contain the total integrated spatial
volume :math:`\int_\Omega \sqrt{\gamma} dx dy dz`.

Curvature diagnostics
~~~~~~~~~~~~~~~~~~~~~

The output ``variable = z4c_diag`` contains 17 vacuum curvature diagnostics. Each field
can also be selected individually:

- Electric Weyl tensor :math:`E_{ij}`: ``z4c_Exx``, ``z4c_Exy``, ``z4c_Exz``,
  ``z4c_Eyy``, ``z4c_Eyz``, and ``z4c_Ezz``

- Magnetic Weyl tensor :math:`B_{ij}`: ``z4c_Bxx``, ``z4c_Bxy``, ``z4c_Bxz``,
  ``z4c_Byy``, ``z4c_Byz``, and ``z4c_Bzz``

- Super-Poynting vector :math:`P^i`: ``z4c_Px``, ``z4c_Py``, and ``z4c_Pz``

- Physical norm :math:`\sqrt{\gamma_{ij}P^iP^j}`: ``z4c_Pnorm``

- Vacuum Kretschmann scalar :math:`8(E_{ij}E^{ij}-B_{ij}B^{ij})`:
  ``z4c_Kretschmann``

For example, a full diagnostic dump can be enabled with:

.. code-block:: text

   <output1>
   file_type = bin
   variable = z4c_diag
   dt = 1.0

The electric and magnetic tensors are symmetric and trace-free in the physical spatial
metric, as measured by an Eulerian observer. The orientation is
:math:`\epsilon^{123}=1/\sqrt{\det\gamma}`, and the super-Poynting convention is
:math:`P^i=-\epsilon^{ijk}E_{jl}B_k{}^l`. The norm uses the physical metric.
``z4c_Bxx`` and the other magnetic curvature components are distinct from the telegraph
lapse fields ``z4c_Bx``, ``z4c_By``, and ``z4c_Bz``.

These diagnostics require Z4c and reject runs with matter. Identifying the reported
Kretschmann expression with the spacetime curvature invariant assumes the vacuum field
equations; constraint violations can affect that interpretation. Cells with a nonfinite
or nonpositive metric determinant produce NaN diagnostics.

Restarts
--------

Z4c checkpoints preserve the telegraph lapse fields, horizon dump counters and cadence,
CCE cadence, and the drift controller's position, velocity, error, integral, observer,
and control-budget history. Checkpoint parameters retain full floating-point precision,
and tracker and controller logs append when a run resumes. Both shared checkpoints and
one file per MPI rank are supported; see :doc:`outputs` for restart commands.

.. warning::

   The three auxiliary lapse fields increase the Z4c restart state from 22 to 25
   fields, even when ``telegraph_lapse = false``. Earlier 22-field Z4c checkpoints
   are rejected by the size check. There is no automatic conversion.

Example: Single puncture black hole
-----------------------------------

The puncture problem initializes a Schwarzschild black hole in isotropic coordinates with
a "pre-collapsed" lapse and allows it to evolve in the puncture gauge. After some initial
gauge dynamics, it should relax to a steady-state. There is an included input file for a
puncture problem in ``inputs/z4c/onepuncture/z4c_onepuncture.athinput`` that can be used.

1. **Build**. The single puncture problem is described by the pgen
``z4c/z4c_one_puncture.cpp``:

.. code-block:: bash

  cmake -DPROBLEM=z4c/z4c_one_puncture -B build
  cmake --build build -j

2. **Input file**. The provided input file should have the following parameters:

.. code-block::

  <z4c>
  diss = 1    # Add Kreiss-Oliger dissipation

  <problem>
  punc_ADM_mass = 1.  # ADM mass of black hole

The resolution in this input file is insufficient and will cause the puncture to
disintegrate. Let's modify the input file to something more reasonable:

.. code-block::

  <mesh>
  ...
  nx1 = 64
  ...
  nx2 = 64
  ...
  nx3 = 64
  ...

  <meshblock>
  nx1 = 16
  nx2 = 16
  nx3 = 16

  <mesh_refinement>
  refinement = static
  
  # Add four levels of refinement around the region +/- 1
  <refined_region1>
  x1min = -1.0
  x1max =  1.0
  x2min = -1.0
  x2max =  1.0
  x3min = -1.0
  x3max =  1.0
  level = 4

  <time>
  ...
  nlim = -1
  tlim = 1.0
  ...

  ...

  <output3>
  ...
  slice_x2 = 0
  slice_x3 = 0

Note that we also change the time limit and the slice location for one of the outputs.

3. **Run and visualize**

.. code-block::bash

  ./build/src/athena -i inputs/z4c/onepuncture/z4c_onepuncture.athinput -d run
  python3 vis/python/plot_tab.py -i run/tab/z4c.z4c.00010.tab -v z4c_alpha

This should produce a simple plot of the lapse along the :math:`x` axis like the
following:

.. image:: /_static/one_puncture.png
   :alt: Single puncture lapse
   :align: center
   :width: 70%

Superposed boosted punctures
----------------------------

The built-in problem ``z4c_superposed_punctures`` initializes two analytic punctures
with independent signed velocities along :math:`x_1`. It is available in the default
build and requires a three-dimensional mesh with Z4c enabled. Add the following to a
Z4c input file:

.. code-block:: text

   <problem>
   pgen_name = z4c_superposed_punctures
   punc_1_rest_mass = 1.0
   punc_1_velocity_x1 = 0.1
   punc_1_center_x1 = -2.0
   punc_2_rest_mass = 1.0
   punc_2_velocity_x1 = -0.1
   punc_2_center_x1 = 2.0
   puncture_radius_floor = 1e-8

For puncture ``N = 1, 2``, the parameters are:

- ``punc_N_rest_mass``: Positive rest mass (default: ``1.0``)

- ``punc_N_velocity_x1``: Signed boost velocity with magnitude less than ``1``
  (default: ``0.0``)

- ``punc_N_center_x1``, ``punc_N_center_x2``, and ``punc_N_center_x3``: Puncture
  center (defaults: ``(-2, 0, 0)`` for puncture ``1`` and ``(2, 0, 0)`` for puncture
  ``2``)

- ``puncture_radius_floor``: Positive minimum radius for evaluating the puncture
  fields (default: ``1e-8``)

All parameters must be finite. The initial lapse is pre-collapsed and the shift is zero.

.. note::

   Superposition provides approximate binary initial data; it does not solve the binary
   constraint equations. Check the constraints before using these data for a physical
   calculation.

Importing Cartesian initial data
--------------------------------

The ``id_solve`` problem generator reads the spatial metric and extrinsic curvature from
an HDF5 file. It requires the HDF5 C development library and a three-dimensional Z4c
mesh. Configure a separate build with:

.. code-block:: bash

   cmake -B build-id -DPROBLEM=z4c/id_solve
   cmake --build build-id -j

Then specify the file in the input:

.. code-block:: text

   <problem>
   id_filename = initial_data.h5
   id_source_nghost = 0

The file must contain the following datasets:

- ``metric`` and ``extrin``: Arrays with shape ``[6, block, z, y, x]`` containing
  :math:`\gamma_{ij}` and :math:`K_{ij}`. The six components are ordered
  :math:`(xx,xy,xz,yy,yz,zz)`.

- ``x1v``, ``x2v``, and ``x3v``: Coordinate arrays with shape ``[block, n_axis]``.
  Each axis must contain at least five finite, strictly increasing samples per block.
  Axis lengths may differ, so source blocks need not be cubic.

The reader uses five-point tensor-product Lagrange interpolation. It first chooses a
block whose active coordinates cover the destination, preferring the finer block when
several overlap. Source ghost coverage is used only if no active block covers the point.
``id_source_nghost`` is the number of padding samples on each source axis (default:
``0``); it is independent of the simulation's ``mesh/nghost``. The source coordinates
must cover all destination cells, including ghost cells. Nonfinite interpolated values
and spatial metrics that are not positive definite are rejected. The initial shift is
zero and the lapse is pre-collapsed from the imported metric.

An optional interior fill is controlled by the following ``<z4c>`` parameters:

- ``r_fill``: Radius within which to blend toward an analytic puncture metric. ``0``
  disables filling (default: ``0.0``).

- ``M_fill_0`` and ``M_fill_1``: Nonnegative puncture masses for the fill (default:
  ``0.5`` each).

- ``co_0_x``, ``co_0_y``, ``co_0_z`` and ``co_1_x``, ``co_1_y``, ``co_1_z``: Fill
  centers (default: ``0.0`` for each coordinate).

Inside ``r_fill`` of the nearer center, a quintic smoothstep blends the imported
metric to :math:`\psi^4\delta_{ij}`, with
:math:`\psi=1+M_0/(2r_0)+M_1/(2r_1)`, and the extrinsic curvature to zero. The radii
are bounded below by ``problem/puncture_radius_floor`` (default: ``1e-8``). Filling
modifies the initial data and does not solve the constraints.

Running binary black holes
--------------------------

.. warning::
  This tutorial is deprecated.

AthenaK requires external modules to provide Cauchy initial data for the binary black hole
problems. Currently, we can read in initial data from the `TwoPunctures
<https://github.com/computationalrelativity/TwoPuncturesC>`_ and
`SpECTRE <https://spectre-code.org/>`_ codes. The TwoPunctures initial data is calculated
on the fly at the start of the evolution, while SpECTRE initial data needs to be
pre-computed. Below is a tutorial for evolving the TwoPunctures initial data.

TwoPunctures initial data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two external libraries are required for building the ``z4c_two_puncture`` problem, namely
GSL and the TwoPunctures initial data solver. GSL should be discoverable by CMake.
TwoPunctures needs to be compiled and linked separately. Because many external initial
data libraries do not have CMake linkages, the preferred method in AthenaK for linking
most of these libraries is by cloning and compiling the library separately, then providing
a symbolic link to the library's base directory directly in the AthenaK base directory.
For TwoPunctures, this looks like the following:

..
  .. code-block:: bash

   cd $HOME && mkdir -p usr/gsl && mkdir codes && cd codes
   # grab source
   wget ftp://ftp.gnu.org/gnu/gsl/gsl-2.5.tar.gz

   # extract and configure for local install
   tar -zxvf gsl-2.5.tar.gz
   cd gsl-2.5
   ./configure --prefix=$HOME/usr/gsl
   make -j8
   # make check
   make install

   # link gsl into athenak
   ln -s $HOME/usr/gsl ${path_to_athenak}

.. code-block:: bash

   cd $HOME && cd usr
   git clone https://github.com/computationalrelativity/TwoPuncturesC.git
   cd TwoPuncturesC
   make -j8

   # link twopuncturesc into athenak
   ln -s $HOME/usr/TwoPuncturesC ${path_to_athenak}

Now create a build directory, then configure and build AthenaK with CMake:

.. code-block:: bash

   mkdir build_z4c_twopunc && cd build_z4c_twopunc
   cmake ../ -DPROBLEM=z4c/two_punctures/z4c_two_puncture

.. note::

   A tutorial for using SpECTRE initial data is forthcoming.
