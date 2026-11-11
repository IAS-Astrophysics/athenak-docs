Requirements
============

AthenaK is designed to keep external dependencies minimal ("hermetic builds").
The **core requirements** are:

- Kokkos Core library
- CMake (3.16 or later, as required by the bundled Kokkos)
- C++17 (or later) compliant compiler

Kokkos is included as a git submodule in this repository, so a recursive clone is
the standard way to obtain all required source dependencies.

Additional platform requirements
--------------------------------

Building on heterogeneous architectures (especially GPUs) can require vendor
toolkits and environment modules in addition to the core requirements:

- NVIDIA GPUs: CUDA toolkit and compatible host compiler
- AMD GPUs: ROCm/HIP toolchain

Optional requirements
---------------------

- MPI library for distributed-memory parallelism
- Device-aware MPI (required for GPU-aware MPI workflows)
- Python 3 for many analysis scripts

Related pages
-------------

- :doc:`download`
- :doc:`build`
