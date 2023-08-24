# reliableDataTransfer
Portfolio project from Intro to Networks

The purpose of this project was to implement a method of transferring data reliably over an unreliable network.
We were to use as our basis the Reliable Data Transfer 3.0, as described in Computer Networking: A Topdown Approach by James F. Kurose;
however, the specific implementation was left to us.

The unreliable network that we had to get data across reliably has the following problems:
1. Data delivered out of order
2. Packets of data dropped
3. Packets of data delayed and showing up later in stream
4. Error introduced into data delivered

These conditions were introduced using flags in rdt_main.py:
![image](https://github.com/sethstephanz/reliableDataTransfer/assets/24879754/05716d6b-c390-4bb5-8cb0-cf94d5011009)

The client sending the data and the server receiving the data are different instances of the same code, the main difference being that the client has data to send initially. The client sends data in small packets in bundles of predetermined size: DATA_LENGTH determines how many characters are sent as part of one packet and FLOW_CONTROL_WIN_SIZE determines how many characters are sent in one bundle of packets. The default was 4 and 15 by default, which meant that 3 packets of 4 characters were sending each "round" (15 // 4 = 3).

The general approach I took to this project was having both client and server first send the appropriate data and then immediately enter a 'wait and see' state. First, the server would send its data. Then, it would wait for the appropriate acknowledgement (ack) packet to arrive from the server, indicating that data had been received and there were no errors. If no ack packet was received, it would continue to send that same bundle. The server worked similarly; for a while, I was working with explicit "ack-of-ack" packets sent back from the client to the server, but realized that that information was implicit in receiving the next batch of information from the client, so simplified.
