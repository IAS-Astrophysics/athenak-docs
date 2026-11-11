Problem Generators
==================

A *problem generator* (pgen) sets up the initial conditions and any problem-specific
runtime behavior for a simulation. AthenaK decides which problem generator to run either
at build time (for custom problems) or at runtime through the input file (for the
built-in test problems).

Selecting a problem generator
-----------------------------

There are two ways to choose a problem generator.

1. **Built-in problem generator, selected at runtime.** When AthenaK is built without a
   custom problem, the ``pgen_name`` parameter in the ``<problem>`` block selects one of
   the problem generators that ship with the code:

   .. code-block:: text

      <problem>
      pgen_name = linear_wave

2. **Custom problem generator, selected at build time.** Compile a specific problem
   generator source file from ``src/pgen/`` (or your own) with the ``PROBLEM`` option:

   .. code-block:: bash

      cmake -B build -D PROBLEM=my_problem_file
      cmake --build build -j

   This compiles ``src/pgen/my_problem_file.cpp`` and wires it in through the
   user-problem hook. A build configured this way always runs that problem generator and
   ignores ``pgen_name``.

If ``pgen_name`` is not recognized and no custom ``-D PROBLEM=...`` build was used,
AthenaK aborts with a fatal error.

Built-in ``pgen_name`` values
-----------------------------

The problem generators dispatched in ``src/pgen/pgen.cpp`` are:

- ``advection``
- ``cpaw``
- ``gr_bondi``
- ``cshock``
- ``divb_amr``
- ``diffusion``
- ``linear_wave``
- ``implode``
- ``gr_monopole``
- ``mri3d``
- ``orszag_tang``
- ``rad_linear_wave``
- ``rad_beam``
- ``shock_tube``
- ``shwave``
- ``z4c_boosted_puncture``
- ``z4c_linear_wave``
- ``gravity``
- ``binary_gravity``
- ``be_collapse``

In addition, two pre-defined unit-test problem generators are built in by default:

- ``eos_compose`` — exercises the tabulated (CompOSE) equation-of-state machinery.
- ``gauss_legendre`` — exercises the Gauss–Legendre quadrature used for spherical
  grids and surface integrals.

Where to find existing examples
-------------------------------

- Core pgen sources: ``src/pgen/``
- Test-oriented pgens: ``src/pgen/tests/``
- Ready-to-run input files: ``inputs/`` and ``inputs/tests/``

Common workflow
---------------

.. code-block:: bash

   # Build (default built-in pgens)
   cmake -B build
   cmake --build build -j

   # Validate the input file and the chosen pgen
   ./build/src/athena -i inputs/tests/linear_wave_hydro.athinput -v

   # Run
   ./build/src/athena -i inputs/tests/linear_wave_hydro.athinput

Tips for custom pgens
---------------------

- Start from a nearby file in ``src/pgen/`` or ``src/pgen/tests/``.
- Keep all run-time knobs in the ``<problem>`` block so users can override them easily.
- Validate with ``-v`` before launching long runs (``-n`` only parses the input file and
  does not construct the problem generator).
