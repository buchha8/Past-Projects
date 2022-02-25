README
--------------------------------------------------------------------------------------
Both PingClient.java and rPingClient.java were tested under the following conditions:
	-AVERAGE_DELAY of 0, 100, 300, 1000 and 2000
	-LOSS_RATE of 0, 0.3, 0.75 and 1.0
	-Different port numbers between client and server (all packets lost)
	-All tests were performed locally and remotely


Some notes:
	-I used to delay the packets by 1000-rtt, but I felt that it didn't make sense in the context of the problem so I changed it to a flat 1000
	-The 1000ms delay is not included in rPingClient.java because it did not make sense in the context of the problem
	-Timestamp is not actually used to calculate RTT because it is not needed; the client knows when the packet is sent and when the server sends it back, so start and end times are known locally
	-RTT (intentionally) does not include time spent on LOST packets
	-Large amount of empty space on server's command line because the server allocates too much space for packets (1024)