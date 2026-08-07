Running AthenaK
===============

After building the code, an executable named ``athena`` will be created in the
``build/src`` subdirectory. To run it, an input file must also be specified on the
command line, e.g.

.. code-block:: bash

   athena -i example.athinput

Examples of input files can be found in the ``inputs/`` subdirectory. Input files that
work with the built-in test problems can be found in ``inputs/tests``.

When the code runs, all output files are created in the current working directory by
default. The code will output simulation progress and some diagnosis messages to
stdout.

Command-line options
--------------------

A variety of command-line options have been implemented in AthenaK. The list of the
options as well as the code configuration is given by the ``-h`` switch:

.. code-block:: text

   $ athena -h
   Athena v0.1
   Usage: athena [options] [block/par=value ...]
   Options:
     -i <file>       specify input file [athinput]
     -r <file>       restart with this file
     -d <directory>  specify run dir [current dir]
     -n              parse input file and quit
     -c              show configuration and quit
     -m              output mesh structure and quit
     -v              validate input parameters and quit
     -t hh:mm:ss     wall time limit for final output
     -w ss           watchdog timeout in seconds
     -h              this help

Validating an input file
------------------------

The ``-v`` switch builds a real ``Mesh``, ``ProblemGenerator``, and all requested
physics modules from the input file -- exercising every parameter read, the
initial-data setup, and (if used) the EOS table -- and then exits before the evolution
loop starts. To keep this cheap, the root grid is collapsed to a single MeshBlock and
mesh refinement is disabled, regardless of what the input file specifies. This makes it
a fast way to catch problems in an input file (missing parameters, bad values, EOS
table issues, etc.) before submitting a full job to a cluster:

.. code-block:: bash

   athena -v -i example.athinput

On every run, not just under ``-v``, AthenaK also checks (from rank 0, after all
classes have been constructed) whether every parameter present in the input file was
actually read by the code, and prints a warning to stderr for each one that was not,
e.g.

.. code-block:: text

   ### WARNING in parameter_input.cpp: input parameter <hydro>/reconstuct = plm was not used by the code (check for a typo)

This is a good way to catch typos in optional parameter names, which would otherwise be
silently ignored. Note that under ``-v`` this check skips mesh-refinement-related
blocks (``mesh_refinement``, ``refined_region``, ``amr_criterion``, ``z4c_amr``), since
refinement is disabled in validation mode and those parameters are never read; use a
full run to confirm refinement parameters are being consumed.

Watchdog for hung jobs
----------------------

The ``-w ss`` switch starts a background "WatchDog" thread with a timeout of ``ss``
seconds (a port of the WatchDog from the `Einstein Toolkit
<https://bitbucket.org/cactuscode/cactusutils/src/master/WatchDog/>`_):

.. code-block:: bash

   athena -w 300 -i example.athinput

Once the evolution loop starts, the watchdog checks for progress once per cycle. If a
full timeout interval elapses without a cycle completing, it prints a message to stderr
and aborts the run. This is useful for catching simulations that hang on a cluster
(e.g., a deadlocked MPI collective): a hard abort lets a batch script or scheduler
detect the failure and react (for example, resubmit), rather than the job silently
idling until it exhausts its walltime allocation. Choose a timeout comfortably larger
than the time needed for one cycle, accounting for occasional slower cycles such as
those that write restart files or trigger AMR regridding, to avoid false positives.

Overriding parameters in the input file
---------------------------------------

Some parameter values specified in the input file can be overridden by specifying new
values on the command line using the following format:
``<parameter_block>/<parameter>=<value>``. For example, if you want to extend the
simulation time limit when restarting,

.. code-block:: bash

   athena -r example.00010.rst time/tlim=100

Some parameters, such as the sizes of the Mesh and MeshBlock, cannot be changed in this
way.

Resuming cluster jobs from the latest restart file
--------------------------------------------------

Large jobs on clusters often require submitting requests to continue from a checkpoint.
The following snippet can help in making a submission script (e.g. for Slurm) that does
this automatically. This uses ``$input_dir/$name.athinput`` but overrides the
``job/basename`` field to be ``$name``. Only the ``# Parameters`` section needs to be
modified from job to job, and generally at most the ``tlim`` entry needs to be modified
with each restart. Additional command-line overrides can be specified with additional
lines to the ``arguments`` variable.

.. code-block:: bash

   # Parameters
   name=<name of job and input file>
   bin_name=<name of executable>
   input_dir=<path to directory containing input file>
   data_dir=<path to directory for writing outputs>
   arguments="\
     time/tlim=<tlim> \
   "

   # Check for restart file
   test_file=$(find $data_dir/rst -maxdepth 1 -name "$name.*.rst" -print -quit)
   if [ -n "$test_file" ]; then
     restart_files=$(ls -t $data_dir/rst/$name.*.rst)
     restart_file=(${restart_files[0]})
     restart_line="-r $restart_file"
     printf "\nrestarting from $restart_file\n\n"
   else
     restart_line="-i $input_dir/$name.athinput job/basename=$name"
     printf "\nstarting from beginning\n\n"
   fi

   # Run code
   <srun or equivalent> <options> $bin_name -d $data_dir $restart_line $arguments
