###Compact Cori

Currently, the installation of Compact Cori at CRT requires that two scripts be
run to start the simulation.  One of the nodes (`CompactCori16`) is currently
being used as the visualization node (running Ubuntu instead of Debian).

To run the simulation:

1. Ensure the simulation is running on the master node (`CompactCori1`) by
   verifying that the LEDs are flashing with each timestep.  If not, use
   `run_md_simulation`.
2. Start the visualization server on the visualization node.  Run the script on
   the desktop to start the visualization server.
3. Point Firefox to `localhost:8081` to view the simulation
