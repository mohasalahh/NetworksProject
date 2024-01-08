#
#  LoadTestingResults.py
#  NetworksProject

#  Created by Mohamed Salah on 08/01/2024.
#  Copyright © 2024 Mohamed Salah. All rights reserved.
#


file1 = open('load_testing.log', 'r')
count = 0

total = float(0)

peak_peer = float(0)
peak_peer_op = ""
total_peer = float(0)
count_peer = 0

peak_server = float(0)
peak_server_op = ""
total_server = float(0)
count_server = 0

while True:
    count += 1

    # Get next line from file
    line = file1.readline()

    # if line is empty
    # end of file is reached
    if not line:
        break

    line = line.split("::")
    time = float(line[3])
    if line[0] == "Peer":
        if time > peak_peer:
            peak_peer = time
            peak_peer_op = line[2]
        total_peer += time
        count_peer += 1
    elif line[0] == "CentralizedServer":
        if time > peak_server:
            peak_server = time
            peak_server_op = line[2]
        total_server += time
        count_server += 1

    total += time

file1.close()

print(f"Average Response Time: {(total / count)}ms")
print(f"Average Peer Response Time: {(total_peer / count_peer)}ms")
print(f"Average CentralizedServer Response Time: {(total_server / count_server)}ms")

print("\n")
print(f"Peak Peer Response Time: {peak_peer}ms while sending: {peak_peer_op}")
print(f"Peak CentralizedServer Response Time: {peak_server}ms while sending: {peak_peer_op}")

