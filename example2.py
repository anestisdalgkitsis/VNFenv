# VNFenv Chaining Example 2
# Network Computational Resources Simulator
# Anestis Dalgkitsis ✖️

# 30 June 2020
# Project v2 started 25 September 2020

# Modules

from entities import Service, Host, Link, User, Network

# --[ VNFchain migration example code] --

# Define Network Topology
myNetwork = Network("GreekNet")
h0 = myNetwork.addHost("edgeATH_0", cpuCores=32, ram=64, storage=1000)
h1 = myNetwork.addHost("edgeSKG_1", cpuCores=16, ram=64, storage=1000)
h2 = myNetwork.addHost("edgeJTR_2", cpuCores=8, ram=8, storage=128)
l01 = myNetwork.addLink(h0, h1, bandwidth=10, delay=8)
l12 = myNetwork.addLink(h1, h2, bandwidth=10, delay=2)
l02 = myNetwork.addLink(h0, h2, bandwidth=10, delay=2)
myNetwork.printHosts()
myNetwork.printLinks()
# myNetwork.printTopology()

# Define Services (VMs/Containers/NetApps)
s0 = myNetwork.addService("web0_h", cpuCores=1, ram=2, storage=2)
s1 = myNetwork.addService("web1_h", cpuCores=2, ram=3, storage=8)
myNetwork.printServices()

# Instantiate Service in Hosts
vm0 = myNetwork.instantiateService(s0, h0)
vm1 = myNetwork.instantiateService(s0, h1)
vm2 = myNetwork.instantiateService(s0, h2)
vm3 = myNetwork.instantiateService(s1, h2)
myNetwork.printVMs()

# Define Service Chain
vmChain0 = myNetwork.addChain([vm1, vm2, vm3], bidirectional=True) # FIFO
myNetwork.printChains()

# change: define users, connect to network, assign services/servicechains
# Instantiate Users
u0 = myNetwork.addUser("+306982756492", vmChain0, bandwidth=2, sla=22)
myNetwork.printUsers()
lu00 = myNetwork.addLink(u0, h0, bandwidth=10, delay=1, loss=10)
myNetwork.printLinks()
# myNetwork.printTopology()

# Simulate Scenario
myNetwork.startTraffic(u0, vmChain0, bidirectional=False)
# print(u1.servicePing())
# print(u1.servicePerf())
# print(u1.serviceScore()) # Calculates Performance Metric Score

# myNetwork.migrateVM(vm1, h1, h2)

# myNetwork.startTraffic()
# print(u1.servicePing())
# print(u1.servicePerf())