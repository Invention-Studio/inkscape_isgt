#!/usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions') # thanks to Cighir Victor

import inkex, simpletransformed, pathmodifier, cubicsuperpath, bezmisc, math

#This 2 functions are used by object arrangement algorithm
def compareX(a, b):
	return cmp(a[1], b[1])

def compareY(a, b):
	return cmp(a[2], b[2])

class PlaceOnPath(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("-d", "--detect",
				action="store", type="string", 
				dest="detect", default="left",
				help="Where to search objects from") #left right top bottom
		self.OptionParser.add_option("-p", "--placement",
				action="store", type="string", 
				dest="detect", default="center",
				help="Plcement of objects") #center above below
		self.OptionParser.add_option("-o", "--offset",
				action="store", type="float", 
				dest="offset", default=0,
				help="The distance from first node to first object")
		self.OptionParser.add_option("-e", "--degree",
				action="store", type="float", 
				dest="degree", default=0,
				help="Rotation")
		self.OptionParser.add_option("-r", "--orient",
				action="store", type="inkbool", 
				dest="orient", default=True,
				help="Orient to path")
		self.OptionParser.add_option("-t", "--placetext",
				action="store", type="inkbool", 
				dest="placetext", default=True,
				help="Place text")
		self.OptionParser.add_option("-s", "--usedistance",
				action="store", type="inkbool", 
				dest="usedistance", default=False,
				help="Specify distance?")
		self.OptionParser.add_option("-n", "--distance",
				action="store", type="float", 
				dest="distance", default=50,
				help="Distance")
		self.OptionParser.add_option("-b", "--distbetween",
				action="store", type="string", 
				dest="distbetween", default="centers",
				help="Plcement of objects") #centers bboxes
		self.OptionParser.add_option("--tab",
				action="store", type="string", 
				dest="tab", default="sampling",
				help="The selected UI-tab when OK was pressed")

	def effect(self):
		if len(self.selected)<2:
			inkex.debug("Select 2 objects or more, please.")
		else:
			self.alignAlongPath()

	def alignAlongPath(self):
		###convert object(line) to path? or determine wether object is path or not

		#This is used by object arrangement algorithm
		xNotY = True
		ascending = True
		if self.options.detect=='left':
			xNotY = True
			ascending = True
		elif self.options.detect=='right':
			xNotY = True
			ascending = False
		elif self.options.detect=='top':
			xNotY = False
			ascending = True
		elif self.options.detect=='bottom':
			xNotY = False
			ascending = False

		#Sorting selection to determine lowest (path)
		zOrderedList = pathmodifier.zSort(self.document.getroot(),self.options.ids)
		#Compute centers
		self.centers = self.computeCenters(zOrderedList[1:], self.options.placetext)
		if len(self.centers)>0:
			#Ordering objects that should be placed on path
			self.orderObjects(xNotY, ascending)
			#Computing offsets from path's  start point which are similar to distances between objects
			offsets = self.computeOffsets(self.options.usedistance, self.options.distance, self.options.distbetween)
			#Computing where objects should be placed
			orderedObjListPositions = self.computePointsXY(zOrderedList[0], offsets, self.options.offset)
			#Traslating and rotating objects
			if orderedObjListPositions:
				self.translateObjects(orderedObjListPositions, self.options.orient)
			else:
				inkex.debug("Nothing was changed.")

	def translateObjects(self, coordinates, transformRotate=True):
		alphaWA = self.options.degree*math.pi/180
		for i in xrange(len(coordinates)): #for every offset determine x,y and alpha for object
			center = self.centers[i]
			x1 = center[1]
			y1 = center[2]
			x2 = coordinates[i][0]
			y2 = coordinates[i][1]
			x = x2 - x1
			y = y2 - y1
			alpha = coordinates[i][2] + self.options.degree*math.pi/180

			#Alpha interpretation workaround (without it 180 deg flips occur)
			if abs(alpha-alphaWA)>math.pi/2:
				alpha = alpha - math.pi
			alphaWA = alpha

			#Rotate
			if transformRotate:
				matrix=[[1.0, 0.0, -x1], [0.0, 1.0, -y1]]
				simpletransformed.applyTransformToNode(matrix, self.selected[center[0]])
				matrix=[[math.cos(alpha),-math.sin(alpha),0],[math.sin(alpha),math.cos(alpha),0]]
				simpletransformed.applyTransformToNode(matrix, self.selected[center[0]])
				matrix=[[1.0, 0.0, x1], [0.0, 1.0, y1]]
				simpletransformed.applyTransformToNode(matrix, self.selected[center[0]])
				#stupid?

			#Translate
			matrix=[[1.0, 0.0, x], [0.0, 1.0, y]]
			simpletransformed.applyTransformToNode(matrix, self.selected[center[0]])

	def computePointsXY(self, pathId, offsets, globalOffset=0.0):
		#offsets.sort() if they have random order, but objects should be sorted respectively to them
		if self.selected[pathId].get('d'):  #determine path parameters and transform it
			mat=[[1,0,0],[0,1,0]]
			m = simpletransformed.parseTransform(self.selected[pathId].get('transform'))
			m = simpletransformed.composeTransform(mat,m)
			csp=cubicsuperpath.parsePath(self.selected[pathId].get('d')) 
			simpletransformed.applyTransformToPath(m,csp)
		else:
			inkex.debug("Only paths are supported as a guide. Make sure your path is in back of other objects.")
			return None
		retval = []
		offsetP = 0
		curveLengths = []
		totalLength = 0.0
		last_subpath = 0
		for csp_i in xrange(len(csp)):
			last_subpath = csp_i
			for i in xrange(len(csp[csp_i])-1): #For every segment of a path
				#determine its length
				curveLengths.append(bezmisc.bezierlength((csp[csp_i][i][1],csp[csp_i][i][2],csp[csp_i][i+1][0],csp[csp_i][i+1][1])))
				#Compute total lenth of a path by sum of each part
				totalLength = totalLength + curveLengths[-1]
				if totalLength>=(offsets[offsetP] + globalOffset): #If offset belongs to current path's part
					while (offsets[offsetP] + globalOffset)<=totalLength: #for all offsets that belong to current path's part
						dlength = totalLength - (offsets[offsetP] + globalOffset) #distance between part start and offset
						t = 1 - dlength/curveLengths[-1] #I don't understand bezier basics... seems that this is right
						#Compute x,y and alpha as atan(slope)
						x,y = bezmisc.bezierpointatt((csp[csp_i][i][1],csp[csp_i][i][2],csp[csp_i][i+1][0],csp[csp_i][i+1][1]),t)
						dx,dy = bezmisc.bezierslopeatt((csp[csp_i][i][1],csp[csp_i][i][2],csp[csp_i][i+1][0],csp[csp_i][i+1][1]),t)
						try:
							alpha = math.atan(dy/dx)#FIXME: divsion by zero on straight lines and 90deg. rotation
						except:
							alpha = 0.0
						retval.append([x,y,alpha]) #Append to result 
						offsetP = offsetP + 1
						if offsetP>(len(offsets)-1): #If no more offsets return value
							return retval

		#If total sum of distances between objects are greater than curve length,
		# then put one more object that beyond the curve in last valid position
		# and others left in their places
		if len(retval)<len(offsets):
			#for i in xrange(len(retval),len(offsets)):  #to place all reminded objects
			x,y = bezmisc.bezierpointatt((csp[last_subpath][-2][1],csp[last_subpath][-2][2],csp[last_subpath][-1][0],csp[last_subpath][-1][1]),1.0)
			retval.append([x,y,0.0])
		
		return retval


	def orderObjects(self, XnotYaxis=True, ascending=True):
		if XnotYaxis:
			self.centers.sort(compareX)
		else:
			self.centers.sort(compareY)

		if not ascending:
			self.centers.reverse()

	def computeCenters(self, idList, placetext=True): #in absolute coordinates
		retval = []
		for Id in idList:
			if not (self.selected[Id].tag==inkex.addNS('text','svg') or self.selected[Id].tag=='text') or (placetext and (self.selected[Id].tag==inkex.addNS('text','svg') or self.selected[Id].tag=='text')):
				bbox = simpletransformed.computeBBox([self.selected[Id]]) #compute bounding box if possible
				if bbox:
					x = (bbox[1]+bbox[0])/2
					y = (bbox[3]+bbox[2])/2
					retval.append([Id, x, y])
				else:
					inkex.debug(("Object "+Id+" cannot be placed on curve. Try convert it to path."))
		return retval

	def computeOffsets(self, usedistance=False, distance=50.0, distbetween='centers'): #as distances from 0.0, 'centers bboxes'
		retval = []
		centers = self.centers
		retval.append(0.0)
		for i in xrange(len(centers)-1):
			retval.append((bezmisc.pointdistance((centers[i+1][1],centers[i+1][2]),(centers[i][1],centers[i][2])) + retval[-1]))
		return retval

if __name__ == '__main__':
	e = PlaceOnPath()
	e.affect()
