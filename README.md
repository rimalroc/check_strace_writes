# check_strace_writes

A program to monitor the system write calls of a program using strace.

usage: check_strace_writes.py [-h] [--alarm ALARM] [--nokill] TO CMD

It simply expands to: 
    timeout TO strace -f -e write CMD
- replace CMD by -p PID, to attach to a running process, 
- add --nokill to not kill that process

Refer to strace documentation for more details

Ths script simply counts the write operations and add all of the bytes reported by write.
If the written bytes are more than the alarm value, it returns 1. otherwise it returns 0.

Meant to be used in CIs as an additional check.

Note: if the CMD contains arguments, wrap it in "quotes".

Example1:
```
$ ./check_strace_writes.py --alarm 100 20 "./write_to_disk.py"
Process 0 called 11 writes operations, writing 2000.037109375 kB
Process wrote more than alarm kB, exiting with code 1
$ echo $?
1
```
The CI will fail on `./check_strace_writes.py --alarm 100 20 "./write_to_disk.py"`

Example2:
```
$ ./check_strace_writes.py --alarm 100 20 "./write_to_disk.py" & 
[1] 31671
$ CHECK_PID=$!
$ # do whatever thing
$ wait $CHECK_PID
$ echo $?
```
The CI will fail on `wait $CHECK_PID`
