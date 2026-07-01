Build
=====

Configure and compile AthenaK in an out-of-source build directory.

Standard CPU build
------------------

From the repository root:

.. code-block:: bash

   cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
   cmake --build build -j

This project forbids in-source builds, so always use ``-B build`` (or another
separate build directory).

CPU architecture tuning
-----------------------

For CPU builds, Kokkos can optimize for the host architecture:

.. code-block:: bash

   cmake -S . -B build \
     -DCMAKE_BUILD_TYPE=Release \
     -DKokkos_ARCH_NATIVE=ON
   cmake --build build -j

You can also set explicit architecture keywords (for example ``Kokkos_ARCH_SKX``)
when targeting known hardware.

GPU builds
----------

Before configuring GPU builds, ensure vendor toolkits and compilers are loaded in
your shell environment.

NVIDIA V100 example:

.. code-block:: bash

   cmake -S . -B build \
     -DCMAKE_BUILD_TYPE=Release \
     -DKokkos_ENABLE_CUDA=ON \
     -DKokkos_ARCH_VOLTA70=ON \
     -DCMAKE_CXX_COMPILER=$PWD/kokkos/bin/nvcc_wrapper
   cmake --build build -j

NVIDIA A100 example:

.. code-block:: bash

   cmake -S . -B build \
     -DCMAKE_BUILD_TYPE=Release \
     -DKokkos_ENABLE_CUDA=ON \
     -DKokkos_ARCH_AMPERE80=ON \
     -DCMAKE_CXX_COMPILER=$PWD/kokkos/bin/nvcc_wrapper
   cmake --build build -j

AMD MI250X example:

.. code-block:: bash

   cmake -S . -B build \
     -DCMAKE_BUILD_TYPE=Release \
     -DKokkos_ENABLE_HIP=ON \
     -DKokkos_ARCH_ZEN3=ON \
     -DKokkos_ARCH_VEGA90A=ON \
     -DCMAKE_CXX_COMPILER=CC \
     -DCMAKE_EXE_LINKER_FLAGS="-L${ROCM_PATH}/lib -lamdhip64" \
     -DCMAKE_CXX_FLAGS="-I${ROCM_PATH}/include"
   cmake --build build -j

Common configure options
------------------------

Use these CMake options as needed:

- ``-DAthena_ENABLE_MPI=ON``: enable MPI parallelism
- ``-DAthena_ENABLE_OPENMP=ON``: enable OpenMP parallelism
- ``-DAthena_SINGLE_PRECISION=ON``: build in single precision
- ``-DAthena_ENABLE_RNS=ON``: enable RNS (rotating neutron star) support
- ``-DPROBLEM=<name>``: select a custom problem generator in ``src/pgen/``
  (defaults to ``built_in_pgens``)
- ``-DCMAKE_CXX_FLAGS="..."``: append custom compiler flags

Example with MPI + OpenMP:

.. code-block:: bash

   cmake -S . -B build \
     -DCMAKE_BUILD_TYPE=Release \
     -DAthena_ENABLE_MPI=ON \
     -DAthena_ENABLE_OPENMP=ON
   cmake --build build -j

Custom problem generators
-------------------------

Use ``-DPROBLEM=<name>`` to compile a specific problem generator file from
``src/pgen/``. Built-in test problem generators in ``src/pgen/tests`` are compiled
by default.

Build outputs
-------------

- Main executable: ``build/src/athena``
- Optional install target (if desired): ``cmake --install build``

Quick verification
------------------

Check executable options:

.. code-block:: bash

   ./build/src/athena -h

Next step
---------

Continue with :doc:`quickstart` for a complete first run, or see
:doc:`running_the_code` for the full reference on running AthenaK.

References
----------

- `Kokkos configuration guide <https://kokkos.org/kokkos-core-wiki/get-started/configuration-guide.html>`_
