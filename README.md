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
