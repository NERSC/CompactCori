### COMPACT CORI (UBUNTU SETUP)
To run the simple molecular dynamics simulation:
1. cd /home/ccori/CompactCori/app/particle
2. ./run_md_ubuntu_1604 <num_nodes> <num_particles>

### SETUP
1. let N be the number of nodes in your Compact Cori cluster
2. for every node (node #1 thru node #N):
    1. ensure blink(1) is not plugged
    2. perform "STEP 1 PART B" as shown below
    3. execute "setup_script_common" in the terminal
    4. plug in blink(1)
    5. ensure it remains powered on
    6. ensure it is connected to the network switch
3. for the master node (node #1 only):
    1. ensure it has internet access
    2. ensure it is connected to the network switch
    3. execute "setup_script_master"

### STEP 1 PART B
1. power off Intel NUC
2. ensure there is internet access
3. insert USB flash drive containing Ubuntu 16.10.2
4. power on Intel NUC
5. press F10
6. choose USB boot device containing Ubuntu 16.10.2

1. wait for installation window to show
2. if using wired connection for internet access, then wait for "You may wish to read the release notes." to show up in installation window; otherwise, just skip the above

1. click "Install Ubuntu"
2. if using wifi for internet access, then click "Connect to this network" for internet access when installing, then double click the appropriate network for internet access, then click "Continue"; otherwise, just skip the above

1. check box "Download updates while installing Ubuntu"
2. check box "Install third-party software for graphics and Wi-Fi hardware, Flash, MP3 and other media"
3. click "Continue"

1. click "Erase disk and install Ubuntu"
2. uncheck box "Encrypt the new Ubuntu installation for security"
3. uncheck box "Use LVM with the new Ubuntu installation"
4. click "Install Now"
5. click "Continue"

1. choose the appropriate location
2. click "Continue" to "Where are you?"
3. choose the appropriate keyboard layout
4. click "Continue" to "Keyboard layout"

1. enter name # this is optional
2. enter computer name # this is required, and follow the pattern as shown below:
    1. CompactCori1 will be the computer name for the master node
    2. CompactCori2 will be the computer name for the first slave node
    3. CompactCori3 will be the computer name for the second slave node
    4. ... ... ...
    5. CompactCoriN will be the computer name for the last slave node
3. ccori # this will the username
4. enter password # this is required, and use the same password for every slave node
5. click "Log in automatically"
6. click "Continue"

1. wait for installation to complete

1. click "Restart Now"
2. remove USB flash drive as requested by Ubuntu
3. press ENTER

1. wait for node to restart
