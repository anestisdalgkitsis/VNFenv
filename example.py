# VNFenv Example
# Network Computational Resources Simulator
# Anestis Dalgkitsis ✖️
# 30 June 2020

# Modules

from entities import Service, Host, Link, User, Network
from vnfenv import VNFenv

# --[ VNFchain migration example code] --

# Instantiate Network
myNetwork = Network("GreekNet", routing='dijkstra')
h1 = myNetwork.addHost("edgeATH", cpuCores=8, cpuFrequency='2.0GHz', ram='8GB', storage='32GB')
h2 = myNetwork.addHost("edgeSKG", cpuCores=8, cpuFrequency='2.0GHz', ram='8GB', storage='32GB')
l12 = myNetwork.addLink(h1, h2, bandwidth='10Mbps', delay='5ms', loss='10%')

# Instantiate VNFchains
vm1 = h1.instantiateService("web1", cpuCores=1, ram='2GB', storage='2GB')
vm2 = h2.instantiateService("web2", cpuCores=1, ram='2GB', storage='2GB')
vm3 = h2.instantiateService("web2", cpuCores=2, ram='3GB', storage='8GB')
vmChain1 = myNetwork.addChain([vm1, vm2, vm3], bidirectional=True) # FIFO

# Instantiate Users
u1 = myNetwork.addUser(vmChain1)
lu11 = myNetwork.addLink(u1, h1, bandwidth='10Mbps', delay='1ms', loss='10%')

# Simulate Scenario
VNFenv.run(myNetwork)

u1.startTraffic()
print(u1.servicePing())
print(u1.servicePerf())

VNFenv.migrateVM(vm1, h1, h2)

u1.startTraffic()
print(u1.servicePing())
print(u1.servicePerf())

VNFenv.stop()