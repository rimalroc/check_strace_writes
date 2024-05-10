#!/usr/bin/env python3
'''
write x00 to a output.bin file in current directory
'''
import time

def write_to_disk(kilobytes_per_second, duration_seconds):
    # Calculate the number of bytes to write per second
    bytes_per_second = kilobytes_per_second * 1024 

    # Calculate the total number of bytes to write
    total_bytes = bytes_per_second * duration_seconds

    # Open a file for writing in binary mode
    with open('output.bin', 'wb') as file:
        start_time = time.time()
        bytes_written = 0

        while bytes_written < total_bytes:
            # Write bytes to the file
            file.write(b'\x00' * bytes_per_second)
            file.flush()
            # Update the number of bytes written
            bytes_written += bytes_per_second

            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            # Sleep for the remaining time if needed
            if elapsed_time < duration_seconds:
                time.sleep(duration_seconds - elapsed_time)

    print(f"Finished writing {total_bytes / (1024 * 1024)} MB to disk.")

# Example usage: write 200 kB per second for 10 seconds
write_to_disk(200, 10)