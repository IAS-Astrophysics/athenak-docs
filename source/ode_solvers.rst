ODE Solvers
===========

*NOTE: This is still an area of active development and as such is
subject to change. If you see any discrepancies please open an issue.*

AthenaK provides ODE solvers for solving systems of ODEs. This is still
a work in progress and more ODE solvers will be added.

These ODE solvers require that the ODEs they're solving have a
consistent interface. This is discussed in more detail in the `Developer
Documentation <#developer-documentation>`__

Input File
----------

ODE solvers are chosen and initialized in the module that they are used
and so the parameters for them should be defined within the block of a
specific physics module. This is to accommodate using different ODE
solvers with different settings in the various modules in AthenaK. For
example, to use the forward euler solver in the chemistry module and in
another module those sections of your input file might look like this:

::

   <chemistry>
   network    = H2            # Chemistry network to be used
   ode_solver = forward_euler # ODE solver to be used
   fe_cfl     = 0.02          # The CFL number for the forward euler ODE solver

   <other physics module>
   ode_solver        = forward_euler # ODE solver to be used
   fe_n_subcycle_max = 1e7           # maximum number of substeps for the forward euler ODE solver

Available ODE Solvers
---------------------

Forward Euler
~~~~~~~~~~~~~

The simple forward Euler solver uses the explicit first-order
differentiation formula to solve the ODEs by sub-cycling. Since this is
an explicit method it may not be suitable for stiff ODEs. This solver is
primarily intended for testing due to its simplicity and isn't
necessarily expected to be performant or highly accurate.

Runtime Parameters:

This ODE solver can be selected with ``ode_system = forward_euler``

+-------------------+------+-----------+----------------------------------------------------+
| Option            | Type | Default   | Description                                        |
+===================+======+===========+====================================================+
| fe_cfl            | Real | 0.1       | cfl number for subcycling                          |
+-------------------+------+-----------+----------------------------------------------------+
| fe_n_subcycle_max | int  | 1e5       | maximum number of substeps                         |
+-------------------+------+-----------+----------------------------------------------------+
| fe_yfloor         | Real | 1e-12     | y value floor for calculating subcycling timescale |
+-------------------+------+-----------+----------------------------------------------------+

*"fe" stands for Forward Euler.*

Kokkos Kernels BDF
~~~~~~~~~~~~~~~~~~

AthenaK provides a wrapper around the ``KokkosODE::Experimental::BDFSolve``
function in Kokkos Kernels. This solver requires both the ``evaluate_function``
and ``evaluate_jacobian`` functions to be defined.

Runtime Parameters:

This ODE solver can be selected with ``ode_system = kokkos_BDF``

Developer Documentation
-----------------------

To facilitate easy swapping between different ODE solvers both the solvers and
ODE system classes must have a very strict APIs. The API presented here is
intended to work well with the Kokkos Kernels ODE solvers but, with a proper
wrapper, will hopefully work well with any ODE solver. The forward euler solver
in `forward_euler.hpp
<https://github.com/IAS-Astrophysics/athenak/blob/master/src/ode_solvers/forward_euler.hpp>`__
and H2 network in `H2.hpp
<https://github.com/IAS-Astrophysics/athenak/blob/master/src/chemistry/network/H2.hpp>`__
can serve as a templates but here's a description of the APIs in more detail.

ODE Solver API
~~~~~~~~~~~~~~

The ODE solvers should be contained in a class that is templated on the
ODE system they're solving. This enables inlining which should provide a
significant performance boost on GPUs. The ODE solver's interface
consists of three methods:

- A ``static`` ``GetSettings`` method that is called from the host to
  get any parameters needed from the input file. This should return a
  struct that contains all the runtime parameters for the ODE solver
- A constructor with the following signature
  ``ODESolverName(ODESettings const settings, T& ode_system, Real const t_start, Real const dt)``

  - ``ODESettings const settings``: the struct that contains the runtime
    parameters for the solver
  - ``ode_t& ode_system``: The ODE object to evolve
  - ``Real const t_start``: The start time
  - ``Real const dt``: How much time to evolve the ODEs

- A ``SolveODE()`` method that evolves the system of ODEs by time ``dt``

ODE System API
~~~~~~~~~~~~~~

The ODE system should be contained in a class with at minimum the
following members:

- A ``neqs`` variable that contains the total number of equations in the
  system. This should probably be declared as ``static constexpr int``
  since it's used to define loop limits
- A ``y`` member variable. It should be an array of type ``Real`` with
  length ``neqs`` that contains the current state of the values being
  updated by the solver. This must support accesses ``operator()`` and
  ``operator[]``, the ``RegisterArray`` class provides this syntax if a
  Kokkos View doesn't work.
- A ``y_new`` member variable. It should be an array of type ``Real`` with
  length ``neqs`` that contains the result of evaluating the ODE
- An ``evaluate_function()`` method that computes new values of ``y_new``
  from the values of ``y`` and has the following signature:

  .. code:: cpp

    template <class vec_type1, class vec_type2>
    KOKKOS_FUNCTION void evaluate_function(const Real /*t*/, 
                                           const Real /*dt*/, 
                                           const vec_type1& y_in, 
                                           vec_type2& f) const

- Some ODE solvers require the Jacobian of the system as well in the form of a
  ``evaluate_jacobian()`` method that computes the Jacobian. If your ODE systems
  doesn't have an analytical Jacobian then the ``chemistry::numerical_jacobian``
  function can compute a numerical Jacobian for you. The function signature
  should be:

  .. code:: cpp

    template <class vec_type, class mat_type>
    KOKKOS_FUNCTION void evaluate_jacobian(const Real t, 
                                           const Real dt,
                                           const vec_type& y_in,
                                           const mat_type& jac) const 

Specific ODE solvers might require other methods and they are noted
in their sections above.

Code Example
~~~~~~~~~~~~

See the ``Chemistry::UpdateChemistryTask`` and
``Chemistry::UpdateChemistry`` methods in
`chemistry.cpp <https://github.com/IAS-Astrophysics/athenak/blob/master/src/chemistry/chemistry.cpp>`__ for a
complete in example. A simpliefied version of the most salient sections
is below.

.. code:: cpp

    // First we select which ODE system to use (the H2 network) and which ODE solver
    // to use (forward euler)
    TaskStatus Chemistry::UpdateChemistryTask(Driver* d, int stage) {
      const std::string network = my_pin->GetString("chemistry", "network");
      const std::string ode_solver = my_pin->GetString("chemistry", "ode_solver");

      if (network == "H2") {
        if (ode_solver == "forward_euler") {
          UpdateChemistry<ode_solvers::ForwardEuler, H2Network>();
        } else if (ode_solver == "kokkos_BDF") {
          UpdateChemistry<ode_solvers::KokkosBDF, H2Network>();
        }
      }

      return TaskStatus::complete;
    }

    // Now we actually use the solver in a kernel to solve the system of ODEs
    template <template <typename> class ODE_Solver_t, typename Network_t>
    void Chemistry::UpdateChemistry() {
      // ------ Collect variables that we'll need -----
      // The primitive grid
      auto w0 = GetW0();
      // The time at the beginning of this timestep
      Real const t_start = pmy_pack->pmesh->time;
      // The timestep
      Real const dt = pmy_pack->pmesh->dt;

      // ----- Get the unit conversions and constants we'll need -----
      Real const time_cgs = pmy_pack->punit->time_cgs();
      Real const energy_density_cgs = pmy_pack->punit->pressure_cgs();
      Real const density_cgs = pmy_pack->punit->density_cgs();
      Real const hydrogen_mass_cgs = pmy_pack->punit->hydrogen_mass_cgs;
      Real const gamma = pmy_pack->phydro->peos->eos_data.gamma;
      Real const mu_H_local = mu_H;

      // ----- Load network and ODE solver settings -----
      auto const ode_settings = ODE_Solver_t<Network_t>::GetSettings(my_pin, "chemistry");
      auto const network_settings = Network_t::GetSettings(my_pin);

      // ----- Get all the loop limits and generate the parallel policy ------
      // NOLINTNEXTLINE(whitespace/braces)
      auto const [start_limit, end_limit] = LoopLimitsAllCells();
      int const species_start_idx = chemistry_scalars_first_idx;
      auto const policy = Kokkos::MDRangePolicy<Kokkos::Rank<4>>(
          DevExeSpace(), start_limit, end_limit);

      Kokkos::parallel_for(
          "Chemistry_ODE_Solve", policy,
          KOKKOS_LAMBDA(const int& mb_idx, const int& k, const int& j,
                        const int& i) {
            // Create the chemisty object
            Network_t chem_net(network_settings, w0(mb_idx, IDN, k, j, i),
                              density_cgs, mu_H_local, gamma, hydrogen_mass_cgs,
                              time_cgs, energy_density_cgs);

            // ------ Load cell values ------
            // Chemistry scalars. The loop is based off of the chemical
            // network's number of equations since that's known at compile time,
            // enabling more loop optimizations. The minus 1 is because internal
            // energy occupies the last slot in the array
            int grid_idx = species_start_idx;
            for (int s_idx = 0; s_idx < Network_t::neqs - 1; s_idx++) {
              chem_net.y(s_idx) = w0(mb_idx, grid_idx, k, j, i);
              grid_idx += 1;
            }

            // Load internal energy
            chem_net.y(Network_t::IIE) = w0(mb_idx, IEN, k, j, i);

            // ------ Solve the ODEs ------
            ODE_Solver_t ode_solver(ode_settings, chem_net, t_start, dt);
            // ode_solvers::KokkosBDF solver(chem_net, t_start, dt);
            ode_solver.SolveODE();

            // ------ Write cell values back out ------
            // Chemistry scalars
            grid_idx = species_start_idx;
            for (int s_idx = 0; s_idx < Network_t::neqs - 1; s_idx++) {
              w0(mb_idx, grid_idx, k, j, i) = chem_net.y(s_idx);
              grid_idx += 1;
            }

            // Write internal energy
            w0(mb_idx, IEN, k, j, i) = chem_net.y(Network_t::IIE);
          });
      }
