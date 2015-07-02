### `pdsh`
#### What is `pdsh`
`pdsh` runs commands on remote systems in parallel, thereby allowing a sysadmin
to execute a command on multiple slaves without having to `ssh` to each one
individually.  `pdsh` is used to run commands remotely, so it is not used in
running parallel jobs or with MPI, etc.

#### Usage
Run `pdsh [command]` to run `[command]` on all remote systems.  If you press `^c`,
`pdsh` will print out the status of current threads.  If you press `^c` again
within one second, a SIGINT will be sent and the job will be terminated.

If you don't specify a command, commands will be run interactively.
