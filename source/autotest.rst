Automatic Testing
=================

Purpose
-------

An extensive set of automatic tests is provided in the ``/tst`` directory. They check that
basic features (such as AMR) and all the physics modules implemented in the code are
functioning correctly by running, e.g. convergence tests of linear waves, shock tube tests,
or comparisons to specific known analytic solutions (e.g. Bondi flows).

These tests are useful for developers to check that any changes they make do not negatively
impact the rest of the code. All tests are run for every merge request as part of the CI
infrastructure. Users are encouraged to run the tests manually before making a merge request,
and any new substantive module added to the code should include a new automatic test for
that feature. New tests must be kept simple: to keep the full test suite manageable the total
run time for all tests on any specific hardware configuration should be less than about 10
minutes.

The tests are managed by the ``/tst/run_test_suite.py`` script. It is designed to execute
specific subsets of tests based on the hardware configuration (CPU, MPI-enabled CPU, or GPU).
It uses ``pytest`` to run tests and provides flexibility for developers to target specific
test cases.

Usage
-----

Command-line arguments
~~~~~~~~~~~~~~~~~~~~~~~~

- ``--style``: Runs style checks.
- ``--cpu``: Runs tests for CPU-only configurations.
- ``--mpicpu``: Runs tests for MPI-enabled CPU configurations.
- ``--gpu``: Runs tests for GPU configurations.
- ``--test``: Runs a specific set of test(s) by name. This accepts a space-separated list of
  test files **and/or directories**. All of the files listed and every test found by
  recursively searching the listed directories will be run, so you can select a single test
  file, a single folder (e.g. ``test_suite/nr``), or any mix of the two.

The device flags (``--cpu``, ``--mpicpu``, ``--gpu``) can be combined. For example, passing
both ``--cpu`` and ``--gpu`` runs the CPU tests and then the GPU tests sequentially.

Each device flag can be followed by extra CMake options for that build. These must be
passed as a single quoted string, e.g.
``--gpu "-DKokkos_ARCH_AMPERE80=On -DCMAKE_CXX_COMPILER=<path>/nvcc_wrapper"``; an unquoted
``-D...`` argument is rejected by the argument parser. A single option can also be passed
as ``--cpu=-DOPTION=VALUE``.

Test type selection with ``--test``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The type of each test (CPU, MPI CPU, or GPU) is inferred from its file name, which must
contain one of the following markers:

- ``_cpu`` for CPU tests.
- ``_mpicpu`` for MPI CPU tests.
- ``_gpu`` for GPU tests.

When ``--test`` is used, the behavior depends on whether any device flags are also given:

- **No device flag**: the script scans the requested files and directories, determines which
  test types are present, and runs all of them. For example,
  ``--test test_suite/chemistry`` runs every CPU, MPI CPU, and GPU test found in that folder.
- **With one or more device flags**: only the matching subset is run. For example,
  ``--test test_suite/nr test_suite/gr --cpu`` runs only the CPU tests in the ``nr`` and
  ``gr`` folders. If a requested device flag matches no tests in the given paths, the script
  raises an error.

Example commands
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run style checks
   python run_test_suite.py --style

   # Run CPU tests
   python run_test_suite.py --cpu "<cpu_flags>"

   # Run MPI+CPU tests
   python run_test_suite.py --mpicpu "<mpicpu_flags>"

   # Run GPU tests
   python run_test_suite.py --gpu "<gpu_flags>"

   # Run multiple test types at once (CPU then GPU, sequentially)
   python run_test_suite.py --gpu "<gpu_flags>" --cpu "<cpu_flags>"

   # Run a single test file
   python run_test_suite.py --test test_suite/subdirectory/test_example_cpu.py

   # Run every test in a single folder (auto-detects CPU/MPI CPU/GPU tests present)
   python run_test_suite.py --test test_suite/chemistry

   # Run several folders and/or files at once
   python run_test_suite.py --test test_suite/nr test_suite/gr

   # Run only the CPU tests found in the given folders
   python run_test_suite.py --test test_suite/nr test_suite/gr --cpu "<cpu_flags>"

   # Run the CPU and GPU tests in a folder
   python run_test_suite.py --test test_suite/subdirectory --gpu "<gpu_flags>" --cpu "<cpu_flags>"

   # Mix files and folders, restricted to CPU tests
   python run_test_suite.py --test test_suite/subdirectory/test_example_cpu.py test_suite/subdirectory_2 --cpu "<cpu_flags>"

Behavior
--------

The ``run_test_suite.py`` script performs the following actions based on the provided
arguments:

#. **No target device specified**: If no arguments are provided, the script prints an error
   message and displays the help menu using ``parser.format_help()``. The script then exits
   with ``sys.exit(1)``.

#. **Style checks**: If the ``--style`` argument is provided, the script runs style checks
   using ``pytest`` on the ``test_suite/style`` directory.

#. **CPU tests**: If the ``--cpu`` argument is provided, the script calls
   ``testutils.clean_make()`` to clean and build the project with CPU-specific flags, then
   runs all tests in the ``test_suite`` directory that contain ``_cpu`` in their name using
   ``pytest``.

#. **MPI CPU tests**: If the ``--mpicpu`` argument is provided, the script calls
   ``testutils.clean_make()`` to clean and build the project with MPI-enabled CPU flags
   (``Athena_ENABLE_MPI=ON``), then runs all tests in the ``test_suite`` directory that
   contain ``_mpicpu`` in their name using ``pytest``.

#. **GPU tests**: If the ``--gpu`` argument is provided, the script calls
   ``testutils.clean_make()`` to clean and build the project with GPU-specific flags
   (``Kokkos_ENABLE_CUDA=On``), then runs all tests in the ``test_suite`` directory that
   contain ``_gpu`` in their name using ``pytest``.

#. **Subset of tests execution**: If the ``--test`` argument is provided, the script expands
   the requested paths, treating each entry as either a test file or a directory that is
   searched recursively for ``*.py`` files. It then inspects the resulting file names to
   determine which test types (CPU, MPI CPU, GPU) are present.

   - If no device flag is given, the script runs every test type it found in the requested
     paths.
   - If one or more of ``--cpu``, ``--mpicpu``, or ``--gpu`` are given, only the matching
     tests are run. If a requested device flag matches no tests in the given paths, the
     script raises a ``RuntimeError``.
   - If the requested paths contain no valid test files at all, the script raises a
     ``RuntimeError``.

   Paths must be given relative to the ``/tst`` directory, e.g.
   ``test_suite/subdirectory/testname.py`` for a file or ``test_suite/subdirectory`` for a
   folder.

#. **Log file management**: At the beginning of the script, the log file (``test_log.txt``)
   is removed if it exists to ensure a fresh log file is created during the script's
   execution.

Adding tests to ``test_suite``
------------------------------

Test naming convention
~~~~~~~~~~~~~~~~~~~~~~~~

To ensure your test is executed by the script, name your test files appropriately:

- Use ``_cpu`` in the filename for CPU tests.
- Use ``_mpicpu`` in the filename for MPI CPU tests.
- Use ``_gpu`` in the filename for GPU tests.

For example:

- ``test_example_cpu.py`` for CPU tests.
- ``test_example_mpicpu.py`` for MPI CPU tests.
- ``test_example_gpu.py`` for GPU tests.

Test file location
~~~~~~~~~~~~~~~~~~~

Place your test files in a new subdirectory inside the ``/tst/test_suite`` directory. The new
directory also must contain an ``__init__.py`` file. Any script that follows the above naming
convention and is located in a subdirectory with an ``__init__.py`` will be run automatically
by the ``run_test_suite.py`` script.

Writing tests
~~~~~~~~~~~~~~

It is best to use one of the existing test scripts as a template for writing new tests. New
tests must follow ``pytest`` conventions, for example the name of the function that runs the
test must begin with ``test_``. Tests that compare to known analytic solutions, or check
convergence of solutions, are preferred to regression tests that compare to pre-computed
solutions.
