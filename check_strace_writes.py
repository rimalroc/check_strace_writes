#!/usr/bin/env python3

import subprocess
import argparse
from argparse import RawTextHelpFormatter
import sys

parser = argparse.ArgumentParser(description=
'''
A program to monitor the system write calls of a program
It expands to: 
    timeout TO strace -f -e write CMD
- replace CMD by -p PID, to attach to a running process, 
- add --nokill to not kill that process

Example:
$ ./check_strace_writes.py --alarm 100 13 "./write_to_disk.py"
Process 0 called 11 writes operations, writing 2000.037109375 kB
Process wrote more than alarm kB, exiting with code 1
$ echo $?
1
''', 
formatter_class=RawTextHelpFormatter)
parser.add_argument('--alarm', type=int, help='exit with error if the process wrote more than alarm kB')
parser.add_argument('--nokill',help="don't kill after timeout", action='store_true')
parser.add_argument('TO', type=int, help='Timeout')
parser.add_argument('CMD', type=str, help='command, wrap in quotes')

# Parse the arguments
args = parser.parse_args()

def execute_command(timeout, command):
    try:
        # Execute the command with a timeout
        process = subprocess.Popen(['timeout', str(timeout), 'strace', '-f',  '-e',  'write'] + command.split(),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Count the number of lines starting with 'write' and sum up the numbers at the end
        lines = error.decode().split('\n')
        write_lines = []
        for line in error.splitlines():
            if b"write(" in line:
                if b"=" not in line:
                    # Concatenate with the next line
                    next_line = next(lines, "")
                    line += next_line
                write_lines.append(line)
        total = sum(int(str(line).split('=')[-1].strip().replace("'","")) for line in write_lines)
        n_writes = len(write_lines)

        # Find the PID of the running process
        pid_line = [line for line in lines if line.startswith('strace: Process')]
        if len(pid_line) > 0:
            pid = int(pid_line[-1].split()[2])
        else:
            pid = 0 

        return total, pid, n_writes
    except subprocess.TimeoutExpired:
        print("Command execution timed out.")
        process.kill()
        
timeout = args.TO
command = args.CMD
total_writes, process_pid, nwrites = execute_command(timeout, command)

print(f"Process {process_pid} called {nwrites} writes operations, writing {total_writes/1024} kB")

# Kill the process if it's still running
if not args.nokill:
    try:
        if process_pid > 0:
            process = subprocess.Popen(['kill', str(process_pid)])
            process.wait()
    except subprocess.CalledProcessError:
        print(f"Process with PID {process_pid} is no longer running.")
    
if args.alarm:
    if total_writes / 1024 > args.alarm:
        print("Process wrote more than alarm kB, exiting with code 1")
        sys.exit(1)
        
