### Running IO Performance Tests
#### Using `dd`
`dd` is a utility that allows you to convert and copy a file given parameters.
Syntax is:
```
dd if=[input file] of=[output file] [args]
```
For example, to write a 5 GiB file from `/dev/zero`, run
```
dd if=/dev/zero of=filename bs=5G count=1
```

#### The `time` command
To see how long a command takes to run, use the `time` command.  Run `time
[command you want to run]` and when the command exits, time stats will be
printed to STDOUT.  For example:
```
❱ time dd if=/dev/zero of=large bs=2G count=1

0+1 records in
0+1 records out
2147479552 bytes (2.1 GB) copied, 11.6774 s, 184 MB/s

real    0m11.734s
user    0m0.000s
sys 0m2.660s

```
