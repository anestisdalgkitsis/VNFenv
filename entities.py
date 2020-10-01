# Entities | Version 2.0.2
# VNFenv Network Entities
# Anestis Dalgkitsis ✖️
#
# Project v0 started 29 March 2020
# Project v1 started 30 June 2020
# Project v2 started 25 September 2020

# Modules

import os
import networkx as nx
import matplotlib.pyplot as plt

from microlog import Microlog

# Microlog Init

m = Microlog(path=os.path.join('./logs', 'VNFenvLog.log'), date=True)

# Entities

class ServiceChain:
	def __init__(self, uid, servicelist, bidirectional=True):

		self.uid = uid
		self.chain = servicelist # DATA FLOW -> FROM FIRST TO LAST
		self.bidirectionalTraffic = bidirectional

	def destination(self):
		return self.chain[len(self.chain)-1].host.uid
		# print(self.chain[len(self.chain)-1].host.uid)
		# exit()

class Service:
	def __init__(self, uid, title="Untitled_service", cpuCores=1, ram=1, storage=1):

		self.name = title
		self.uid = uid

		self.CPUrequirements = cpuCores
		self.RAMrequirements = ram
		self.StorageRequirements = storage

class VM:
	def __init__(self, uid, title, serviceImage, hostObject, status): # title="Untitled_VM"

		self.name = title
		self.uid = uid

		self.status = status # True means running, False means not running.
		self.host = hostObject

class Link:
	def __init__(self, uid, sourceObject, destinationObject, throughput=1, latency=0.01, isBidirectional=True):
		"""Throughput is measured in Gbps"""
		
		self.uid = uid

		self.throughputCap = throughput
		self.latency = latency
		self.bidirectional = isBidirectional

		self.source = sourceObject
		self.destination = destinationObject

		# Threshold of 1 means no threshold (DEPRECATED | REMOVE IN NEXT VERSION)
		self.throughputThreshold = 1
		self.throughputUtil = 0

		self.runningConnections = []

	def establishConnection(self, serviceObject):
		"""return 0 means ok, 1 means can not be hosted"""

		# BIDIRECTIONAL NEEDS MORE CODE + DOUBLE THE THROUGHPUT (DEPRECATED | REMOVE IN NEXT VERSION)

		if self.bidirectional:
			if (self.throughputCap * self.throughputThreshold) < (self.throughputUtil + (serviceObject.throughputRequirements * 2)):
				m.printl("[linkALERT] full capacity reached on: " + str(self.uid) + " | Top: " + str(self.top()))
				return 1
		else:
			if (self.throughputCap * self.throughputThreshold) < (self.throughputUtil + serviceObject.throughputRequirements):
				m.printl("[linkALERT] full capacity reached on: " + str(self.uid) + " | Top: " + str(self.top()))
				return 1

		if self.bidirectional:
			self.throughputUtil += serviceObject.throughputRequirements * 2
			self.runningConnections.append(serviceObject)
		else:
			self.throughputUtil += serviceObject.throughputRequirements
			self.runningConnections.append(serviceObject)

		return 0

	def closeConnection(self, serviceObject):
		""" return 0 means closed, 1 means the connection does not exist """

		for service in range(len(self.runningConnections)):
			if serviceObject.id == self.runningConnections[service].id:
				self.throughputUtil -= self.runningConnections[service].throughputRequirements
				del self.runningConnections[service]
				return 0

		print("Connection to kill does not exist: " + str(self.top()))
		return 1

	def top(self):
		"""returns a list with the IDs of all running connections"""
		topConnectionsID = []
		for connection in range(len(self.runningConnections)):
			topConnectionsID.append(self.runningConnections[connection].id)
		return topConnectionsID

	def activity(self):
		return (self.throughputUtil/self.throughputCap)/100

# class Host(Entity):
class Host:
	def __init__(self, uid, name="Untitled_host", cpuCores=4, ram=8, storage=128):
		# super().__init__(name)
		self.name = name
		self.uid = uid

		self.CPUcap = cpuCores
		self.RAMcap = ram
		self.StorageCap = storage

		self.CPUUtil = 0
		self.RAMUtil = 0
		self.StorageUtil = 0

		self.runningServices = []

	def instantiateService(self, serviceObject):
		""" return 0 means hosted ok, return 1 means that it can not be hosted """

		if self.CPUcap < (self.CPUUtil + serviceObject.CPUrequirements):
			m.printl("[hALRT] full CPU on: " + str(self.uid) + " | Top: " + str(self.top()))
			return 1
		if self.RAMcap < (self.RAMUtil + serviceObject.RAMrequirements):
			m.printl("[hALRT] full RAM on: " + str(self.uid) + " | Top: " + str(self.top()))
			return 1
		if self.StorageCap < (self.StorageUtil + serviceObject.StorageRequirements):
			m.printl("[hALRT] full Storage on: " + str(self.uid) + " | Top: " + str(self.top()))
			return 1

		self.CPUUtil += serviceObject.CPUrequirements
		self.RAMUtil += serviceObject.RAMrequirements
		self.StorageUtil += serviceObject.StorageRequirements

		self.runningServices.append(serviceObject)

		return 0

	def killService(self, serviceObject):
		""" return 0 means killed ok, return 1 means that the service does not run in this host """

		for service in range(len(self.runningServices)):
			if serviceObject.id == self.runningServices[service].uid:

				self.CPUUtil -= self.runningServices[service].CPUrequirements
				self.RAMUtil -= self.runningServices[service].RAMrequirements
				self.StorageUtil -= self.runningServices[service].StorageRequirements

				del self.runningServices[service]

				return 0
		print("Service to kill does not exist: " + str(self.top()))
		return 1

	def top(self):
		"""returns a list with the IDs of all running services"""
		topServicesID = []
		for service in range(len(self.runningServices)):
			topServicesID.append(self.runningServices[service].uid)
		return topServicesID

	def activity(self):
		return (self.CPUUtil/self.CPUcap)/100, (self.RAMUtil/self.RAMcap)/100, (self.StorageUtil/self.StorageCap)/100

# class User(Entity):
class User:
	def __init__(self, uid, name, VMChain, bandwidth, sla):
		# super().__init__(name)

		self.uid = uid
		self.name = name

		self.userServiceChain = VMChain # One service for every user
		self.bandwidth = bandwidth
		self.sla = sla

class Network:
	def __init__(self, title):

		# Network Graph
		self.topologyGraph = nx.Graph()

		# Network Entities
		self.networkHosts = []
		self.networkUsers = []
		self.networkLinks = []
		self.networkServices = []
		self.networkVMs = []
		self.networkChains = []

		# Network Initi Sequence
		m.printl("Net init OK")

	# Network Management

	def addHost(self, hostname, cpuCores, ram, storage):

		uid = len(self.networkHosts)+len(self.networkUsers)
		self.hostObject = Host(uid, hostname, cpuCores, ram, storage)
		self.networkHosts.append(self.hostObject)

		self.topologyGraph.add_node(uid)
		m.printl("Host added")

		return self.hostObject

	def addUser(self, name, VMchain, bandwidth=1, sla=10): #MOVE VMCHAIN ASSIGNMENT TO SEPARATE FUNCTION!!!

		uid = len(self.networkHosts)+len(self.networkUsers)
		self.userObject = User(uid, name, VMchain, bandwidth, sla) # Add name, SLA, chainlists and more...
		self.networkUsers.append(self.userObject)

		self.topologyGraph.add_node(uid) # add it in a list so we can color differently
		m.printl("User added")

		return self.userObject

	def addLink(self, sourceHostObject, destinationHostObject, bandwidth=10, delay=5, loss=10):

		uid = len(self.networkLinks)
		self.linkObject = Link(uid, sourceHostObject, destinationHostObject, throughput=bandwidth, latency=delay, isBidirectional=True)
		self.networkLinks.append(self.linkObject)

		self.topologyGraph.add_edge(sourceHostObject.uid, destinationHostObject.uid, delay=delay, throughput=bandwidth, loss=loss)
		m.printl("Link added")

		return self.linkObject

	def addService(self, title, cpuCores=2, ram=3, storage=8):

		uid = len(self.networkServices)
		self.serviceObject = Service(uid, title, cpuCores=cpuCores, ram=ram, storage=storage)
		self.networkServices.append(self.serviceObject)

		m.printl("Service added")

		return self.serviceObject

	def addChain(self, serviceObjectList, bidirectional=True):

		uid = len(self.networkChains)
		self.chainObject = ServiceChain(uid, servicelist=serviceObjectList, bidirectional=bidirectional)
		self.networkChains.append(self.chainObject)
		m.printl("Service Chain added")

		return self.chainObject

	def findShortestPlath(self):

		print("error")
		
		return 0

	# Services Management

	def instantiateService(self, serviceObject, hostObject):

		uid = len(self.networkVMs)
		title2 = serviceObject.name+str(uid)
		self.VMObject = VM(uid, title2, serviceObject, hostObject, status=True)
		self.networkVMs.append(self.VMObject)
		m.printl("Service VM Instantiated")
		
		error = hostObject.instantiateService(serviceObject)
		if (error):
			m.printl("Error Instantiating Service VM in Host, check logfile")

		return self.VMObject

	# User Activity

	def startTraffic(self, userObject, chainObject, bidirectional=False):

		# print(nx.dijkstra_path(self.topologyGraph, userObject.uid, chainObject.destination())) # NEEDS THE common uid fix to work
		pathWeight, nodePath = nx.single_source_dijkstra(self.topologyGraph, userObject.uid, chainObject.destination())
		# print(pathWeight)
		print(nodePath)

		# print(self.topologyGraph.edges.data())
		# print(self.topologyGraph.edges([0, 1]))

		# print(self.topologyGraph.get_edge_data(nodePath[0],nodePath[1]))

		for edge in range(len(nodePath)-1):
			# read node uid
			if bidirectional:
				# get attributes
				# calculate free or utilized bandwidth twice and store in a variable
				pass
			else:
				# get attributes
				# calculate free or utilized bandwidth and store in a variable
				pass
			self.topologyGraph.edges([nodePath[edge+1], nodePath[edge]]).set_edge_attributes()
			# reserve bandwidth resources

	# Interactive Shell

	def printTopology(self):

		pos = nx.spring_layout(self.topologyGraph)  # positions for all nodes
		nx.draw_networkx_nodes(self.topologyGraph, pos, node_size=700)
		nx.draw_networkx_edges(self.topologyGraph, pos, edgelist=self.topologyGraph.edges, width=6)
		nx.draw_networkx_labels(self.topologyGraph, pos, font_size=20, font_family='sans-serif')

		plt.axis('off')
		plt.show()

	def printHosts(self):
		# print(self.networkHosts)
		print("[Network Hosts]")
		for h in range(len(self.networkHosts)):
			print(" |- uid: " + str(self.networkHosts[h].uid) + ", title: " + str(self.networkHosts[h].name))
		print("[Hosts in Network: "+str(len(self.networkHosts))+"]")

	def printLinks(self):
		# print(self.networkLinks)
		print("[Network Links]")
		for l in range(len(self.networkLinks)):
			print(" |- uid: "+str(self.networkLinks[l].uid)+", sc: "+str(self.networkLinks[l].source.uid)+", ds: "+str(self.networkLinks[l].destination.uid)+", bw: "+str(self.networkLinks[l].throughputCap)+", lat: "+str(self.networkLinks[l].latency))
		print("[Links in Network: "+str(len(self.networkLinks))+"]")

	def printServices(self):
		# print(self.networkServices)
		print("[Network Services]")
		for s in range(len(self.networkServices)):
			print(" |- uid: " + str(self.networkServices[s].uid))
		print("[Services in Network: "+str(len(self.networkServices))+"]")

	def printChains(self):
		# print(self.networkChains)
		print("[Network Chains]")
		for c in range(len(self.networkChains)):
			print(" |- uid: " + str(self.networkChains[c].uid) + ", chainflow: " + str(self.networkChains[c].chain))
		print("[Chains in Network: "+str(len(self.networkChains))+"]")

	def printVMs(self):
		# print(self.networkVMs)
		print("[Network VMs]")
		for v in range(len(self.networkVMs)):
			print(" |- uid: "+str(self.networkVMs[v].uid)+", title: "+str(self.networkVMs[v].name)+", host: "+str(self.networkVMs[v].host)+", status: "+str(self.networkVMs[v].status))
		print("[VMs in Network: "+str(len(self.networkVMs))+"]")

	def printUsers(self):
		# print(self.networkUsers)
		print("[Network Users]")
		for u in range(len(self.networkUsers)):
			print(" |- uid: "+str(self.networkUsers[u].uid)+", name: "+str(self.networkUsers[u].name)) #+", chain: "+str(self.networkUsers[v].userServiceChain)
		print("[Users in Network: "+str(len(self.networkUsers))+"]")