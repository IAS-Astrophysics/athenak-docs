Numerical Relativity
====================

AthenaK includes a Z4c numerical relativity module for evolving dynamical spacetimes. This
page describes how to run binary black hole (BBH) problems; for GRMHD in dynamical
spacetimes see :doc:`dyngrmhd`.

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
