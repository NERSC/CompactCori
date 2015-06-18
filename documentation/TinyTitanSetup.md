#### Tiny Titan Setup
1. Install Rasbian on each node
1. On all nodes except the master, download the `pi_setup.sh` file from ORNL's
   GitHub repo: `https://raw.github.com/TinyTitan/TinySetup/master/pi_setup.sh`
1. In the `pi_setup.sh` script, change the `apt-get upgrade` to `apt-get
   dist-upgrade`
1. Make `pi_setup.sh` executable by running `chmod u+x pi_setup.sh`
1. Run the script with `./pi_setup.sh`
1. On the master node, clone the setup GitHub repo: `git clone
   https://github.com/TinyTitan/TinySetup.git`
1. `cd` to the `TinySetup` directory and make `pi_setup.sh` and
   `pi_post_setup.sh` executable: `chmod u+x pi_setup.sh; chmod u+x
   pi_post_setup.sh`.  Then run both scripts

####Install SPH
1. Clone the SPH repository hosted on the [TinyTitan GitHub Project
   Page](https://github.com/TinyTitan/SPH).
1. `cd` into the SPH directory and run `make` followed by `make run`
1. Copy the `sph.out` file to your `$HOME` directory.  This is necessary because
   running `make run` copies `sph.out` to the `$HOME` directory of each Pi, and
   running the simulation looks for the `sph.out` file in the same location as
   where it is on the master node, so it's easier to move the file on the master
   node rather than all the slave nodes.

#### Run SPH
1. Make a directory called `scripts` in the master node's `$HOME` directory
1. Create a file called `xboxlaunch.sh` in the `scripts` directory.  Edit it to
   read:
   ```
   sudo rmmod xpad
   sudo xboxdrv --config ~/SPH/controller_1.cnf --silent &
   ```
1. Set up a cron job that runs at reboot.  Run `crontab -e` and add `@reboot
   /home/pi/scripts/xboxlaunch.sh`
1. Start SPH automatically at boot by editing `~/.config/autostart/xbox.desktop`
   to include:
   ```
   [Desktop Entry]

   Type=Application

   Exec=/home/pi/TinySetup/startsph
   ```
1. Run the `startsph` script in the `TinySetup` directory to run the simulation

