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

- ``user_Sbc``: Whether or not to apply a Sommerfeld radiation condition at the boundary
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

.. note::

  Instructions on performing CCE output are forthcoming.

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
