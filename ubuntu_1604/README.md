### Compact Cori

To run the simple molecular dynamics simulation:
  step 1: cd /home/ccori/CompactCori/app/particle
  step 2: ./run_md_ubuntu_1604 <num_nodes> <num_particles>
  step 3: go to https://localhost:8080/api/get_particles in any web browser and add or accept a security exception
  step 4: go to https://playcanv.as/p/RfDIHpmZ/ in any web browser

### SETUP BEGIN
step 0:
  let N be the number of nodes in your Compact Cori cluster

step 1:
  for every node (node #1 thru node #N):
    part a: ensure blink(1) is not plugged
    part b: perform "STEP 1 PART B" as shown below
    part c: execute "setup_script_common" in the terminal
    part d: plug in blink(1)
    part e: ensure it remains powered on
    part f: ensure it is connected to the network switch

step 2:
  for the master node (node #1 only):
    part a: ensure it has internet access
    part b: ensure it is connected to the network switch
    part c: execute "setup_script_master"
### SETUP END

### STEP 1 PART B BEGIN
power off Intel NUC
ensure there is internet access
insert USB flash drive containing Ubuntu 16.10.2
power on Intel NUC
press F10
choose USB boot device containing Ubuntu 16.10.2

wait for installation window to show
if using wired connection for internet access, then:
  wait for "You may wish to read the release notes." to show up in installation window
otherwise, just skip the above

click "Install Ubuntu"
if using wifi for internet access, then:
  click "Connect to this network" for internet access when installing
  double click the appropriate network for internet access
  click "Continue"
otherwise, just skip the above

check box "Download updates while installing Ubuntu"
check box "Install third-party software for graphics and Wi-Fi hardware, Flash, MP3 and other media"
click "Continue"

click "Erase disk and install Ubuntu"
uncheck box "Encrypt the new Ubuntu installation for security"
uncheck box "Use LVM with the new Ubuntu installation"
click "Install Now"
click "Continue"

choose the appropriate location
click "Continue" to "Where are you?"
choose the appropriate keyboard layout
click "Continue" to "Keyboard layout"

enter name # this is optional
enter computer name # this is required, and follow the pattern as shown below:
  CompactCori1 will be the computer name for the master node
  CompactCori2 will be the computer name for the first slave node
  CompactCori3 will be the computer name for the second slave node
  ... ... ...
  CompactCoriN will be the computer name for the last slave node
ccori # this will the username
enter password # this is required, and use the same password for every slave node
click "Log in automatically"
click "Continue"

wait for installation to complete

click "Restart Now"
remove USB flash drive as requested by Ubuntu
press ENTER

wait for node to restart
### STEP 1 PART B END
