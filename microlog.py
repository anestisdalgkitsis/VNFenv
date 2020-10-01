# Project Microlog Version 2.1.2
# By Anestis Dalgkitsis ✖️
# Active GitHub: https://github.com/anestisdalgkitsis/microlog
#
# Started 24 January 2020

# Modules

from datetime import datetime

# Class

class Microlog:

	def __init__(self, path = "unnamed.log", date = False, overwrite = True):
		""" Create a new object that creates a file. """

		self.path = path
		self.printDate = date
		self.overwrite = overwrite

		if self.overwrite is True:
			type = "w+"
		else:
			type = "a+"

		with open(self.path, type) as file:
			file.write("")

	# Basic

	def printl(self, payload, flairs = []):
		""" Print any string to the file of this object, like you would with default print(). """

		prefix = ""

		if self.printDate == True:
			dateTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			prefix += "[" + dateTime + "]"

		for flair in flairs:
			prefix += "[" + str(flair) + "]"

		with open(self.path, "a") as file:
			file.write(prefix + " " + str(payload) + "\n")
