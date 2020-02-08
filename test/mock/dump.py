#!/usr/bin/python3
from tinyblend import BlenderFile
from sys import argv

blend = BlenderFile(argv[1])
for i in blend.list_structures():
	try:
		print(i + " " + str(len(blend.list(i))))
		#for j in blend.list(i):
		#	print(j)
	except:
		print(i)

