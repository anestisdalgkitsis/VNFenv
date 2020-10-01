# VNFenv | Version 0.3
# Network Computational Resources Simulator OpenAI Gym
# Anestis Dalgkitsis ✖️
#
# Project v0 started 29 March 2020
# Project v1 started 30 June 2020

# Modules

import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

from entities import Service, Host, Link, User

# Environmet Class

class VNFenv():
	def __init__(self, services = 8, mecs = 4):

		self.services = services
		self.mecs = mecs

		# ML stuff here

		self.action_space = self.mecs+1 # We take the service placement
		self.observation_space = np.arange(self.mecs*3) # give a snapshot of the system

		# Simulator Parameters

		self.linkdelay = 0.1 #ms
		self.switchdelay = 0.1 #ms
		self.transportNetworkDelay = 22 #ms

		# Environment Entities

		self.simulationUsers = []
		self.simulationServices = []
		self.simulationMecs = []
		self.simulationCells = []

		self.SERVICEPLACEMENT = [] # SERVICE [MEC]
		self.userPlacement = [] # USER [MEC]

		# Generate Environment

		for h in range(mecs):
			self.mecObject = Host(h, isEdgeIdentifier=True, CPUcap=8, RAMcap=8, StorageCap=32)
			self.simulationMecs.append(self.mecObject)

		self.cloudObject = Host(-1, isEdgeIdentifier=False)

		for s in range(services):
			self.serviceObject = Service(s, CPU = 1, memory = 1, storage = 1)
			self.simulationServices.append(self.serviceObject)

		for u in range(services):
			self.userPlacement.append(random.choice(self.simulationMecs)) #100% random RAN assignment

		m.printl("[#VNFenv] INIT: OK")

		# UI

		self.skip = 0
		rplot = plt.figure(1)
		plt.ion()
		rplot.show()

		# Stats

		self.reward = [] # per step
		# self.avgLatency = [] # per step
		# self.avgSLA = [] # per step
		# self.avgRejections = [] # per step

		self.resetTime = 0
		self.stepTime = 0

	def migrateService(self, serviceObject, sourceHost, destinationHost):
		if sourceHost.id == destinationHost.id:
			# m.printl("[mig] Already in same host. Skipping action.")
			return 0
		# m.printl("[mig] $: " + str(serviceObject.id) + " Sh: " + str(sourceHost.id) + " -> Dh: " + str(destinationHost.id))
		code = destinationHost.instantiateService(serviceObject)
		if code == 1:
			# m.printl("[mig] Could not instantiate service " + str(serviceObject.id) + " at destination host " + str(destinationHost.id) + " during migration")
			return 1
		code = sourceHost.killService(serviceObject)
		if code == 1:
			# m.printl("[mig] Could not kill service " + str(serviceObject.id) + " at source host " + str(sourceHost.id) + " during migration")
			return 1
		self.SERVICEPLACEMENT[serviceObject.id] = destinationHost
		m.printl("[mig] $: " + str(serviceObject.id) + " Sh: " + str(sourceHost.id) + " -> Dh: " + str(self.SERVICEPLACEMENT[serviceObject.id].id) + " [VERIFIED]")
		return 0

	def reset(self):

		# kill all running service IF ANY

		for mecObject in self.SERVICEPLACEMENT:
			self.SERVICEPLACEMENT.remove(mecObject)

		# Instantiate services in cloud

		for serviceObject in self.simulationServices:
			self.cloudObject.instantiateService(serviceObject)
			self.SERVICEPLACEMENT.append(self.cloudObject)

		observation = []
		for hosts in range(self.mecs * 3):
			observation.append(0)

		self.resetTime += 1
		self.stepTime = 0
		m.printl("[#VNFenv] RESET R:" + str(self.resetTime))

		return observation # observation

	def step(self, action):

		m.printl("[#VNFenv] STEP START")

		r, done, info = 0, 0, 0
		lat, sla, rej = 0, 0, 0

		# Placement

		for service in range(len(self.simulationServices)):
			destination = 0
			if action < len(self.simulationMecs):
				destination = self.simulationMecs[action]
			else:
				destination = self.cloudObject
			code = self.migrateService(self.simulationServices[service], self.SERVICEPLACEMENT[service], destination)
			if code == 1:
				# m.printl("Error during migration")
				code = self.migrateService(self.simulationServices[service], self.SERVICEPLACEMENT[service], self.cloudObject)
				if code == 1:
					print("COULD NOT MIGRATE TO CLOUD TOP + EXIT")
					print(self.cloudObject.top())
					exit()
				# else:
					# m.printl("Went to cloud.")
			# else:
				# m.printl("[#VNFenv] Service "+str(self.simulationServices[service].id)+" migrated from "+str(self.SERVICEPLACEMENT[service].id)+" to "+str(action))

		# Generate Observation

		observation = []
		for host in self.simulationMecs:
			cpu, ram, storage = host.activity()
			observation.append(cpu)
			observation.append(ram)
			observation.append(storage)

		# Generate Reward 

		print("-")
		for i in range(len(self.userPlacement)):
			print(self.userPlacement[i].id)
		# exit()

		FronthaulLinkDelay = 0.4 #ms | fD
		BackhaulLinkDelay = 0.6 #ms | bH
		CloudLinkDelay = 9 #ms | cD
		switchDelay = 0.05 #ms | swcD

		totalServiceDelay = 0

		m.printl("|-[ USER/PLACEMENT DELAYS ]")
		latency = 0
		rej = 0
		for host in range(len(self.SERVICEPLACEMENT)):
			# if host.isEdge == True:
			# print(str(self.userPlacement[host].id) + " " + str(self.userPlacement[host].isEdge))
			# print(self.SERVICEPLACEMENT[host].id + " " + str(self.SERVICEPLACEMENT[host].isEdge))
			if self.userPlacement[host].id == self.SERVICEPLACEMENT[host].id:
				r += 10
				totalServiceDelay = FronthaulLinkDelay
				latency += totalServiceDelay
				m.printl("|- Local edge node " + str(totalServiceDelay))
			elif self.SERVICEPLACEMENT[host].id == self.cloudObject.id:
				r -= 2
				totalServiceDelay = FronthaulLinkDelay + BackhaulLinkDelay + switchDelay + CloudLinkDelay
				latency += totalServiceDelay
				rej += 1
				m.printl("|- CLOUD " + str(totalServiceDelay))
			else:
				r -= 1
				totalServiceDelay = FronthaulLinkDelay + 2 * BackhaulLinkDelay + switchDelay
				latency += totalServiceDelay
				m.printl("|- Other edge node " + str(totalServiceDelay))
		self.reward.append(r)
		rewlog.printl(r)
		latlog.printl(latency/len(self.SERVICEPLACEMENT))
		rejlog.printl(rej)
		# print(self.SERVICEPLACEMENT)
		m.printl("|!! >>> R = "+str(r))
		# if (len(self.reward)-1) >= 2:
		# 	print(self.reward[len(self.reward)-1])

		done = False
		info = {} # dict()

		self.stepTime += 1
		m.printl("[#VNFenv] STEP END R:" + str(self.resetTime) + " S:" + str(self.stepTime))

		# self.avgLatency.append(lat)
		# self.avgSLA.append(sla)
		# self.avgRejections.append(rej)

		# Autostop Training

		window = 250
		if len(self.reward) > window:
			cr = 0
			for i in range(window):
				cr += self.reward[len(self.reward)-i-1]
			# if (cr/window) == max(self.reward[len(self.reward)-window:len(self.reward)]):
			# if (cr/window) == 3:
			m.printl("[#VNFenv] Auto end: " + str(cr/window) + "/" + str(max(self.reward)) + ".0")
			if (cr/window) == max(self.reward):
				print("\nDone with r_max="+str(max(self.reward))+"|r_low="+str(min(self.reward))+".")
				if self.skip > 0:
					input("Press Return to exit.")
				exit()

		return observation, r, done, info

	def render(self, mode):
		if self.skip % 128 == 0:
			plt.ion()
			plt.plot(range(len(self.reward)), self.reward, color="#CA1551")
			plt.draw()
			plt.pause(0.001)
		self.skip += 1
