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

Running binary black holes
--------------------------

AthenaK requires external modules to provide Cauchy initial data for the binary black hole
problems. Currently, we can read in initial data from the ``TwoPunctures`` and SpECTRE codes.
The ``TwoPunctures`` initial data is calculated on the fly at the start of the evolution,
while SpECTRE initial data needs to be pre-computed. Below is a tutorial for evolving the
``TwoPunctures`` initial data.

TwoPunctures initial data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two external libraries are required for building the ``z4c_two_puncture`` problem, namely
``gsl`` and the ``twopuncturesc`` initial data solver (in this order).

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

Then build ``twopuncturesc``:

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
   cmake ../ -DPROBLEM=z4c_two_puncture

.. note::

   A tutorial for using SpECTRE initial data is forthcoming.
