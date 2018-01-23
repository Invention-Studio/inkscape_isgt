#!/usr/bin/env python

# Author: ugajin **at** zoho.com
# Date: June 22 - 24, 2016
# v1.1

from math import *
import inkex
inkex.localize()
from simpletransform import *

debug = False
# debug = True


# -------------------------------
# From Guides creator...

def deleteAllGuides(document):
    # getting the parent tag of the guides
    namedView = document.xpath(
                '/svg:svg/sodipodi:namedview',
                namespaces = inkex.NSS)[0]

    # getting all the guides
    children = document.xpath(
               '/svg:svg/sodipodi:namedview/sodipodi:guide',
               namespaces = inkex.NSS)

    # removing each guides
    for element in children:
        namedView.remove(element)

def createGuide(position, orientation, parent):
        # Create a sodipodi:guide node
        # (look into inkex's namespaces to find 'sodipodi' value in order to make a "sodipodi:guide" tag)
        # see NSS array in file inkex.py for the other namespaces
        guide = inkex.etree.SubElement(
                parent,
                '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}guide',
                {'position':position, 'orientation':orientation} )
        # Edited function - to add a return value - ugajin 2016
        return guide

# --------------------------------


class AddObjects(inkex.Effect):
    # Inkscape effect extension

    def __init__(self):
		# Constructor.
		# Defines the param option.

		# Call the base class constructor.
		inkex.Effect.__init__(self)

		# Define options
        # -------------- MODE ----------------
		self.OptionParser.add_option('--myMode',
            action = 'store', type = 'string', dest = 'myMode',
            default = 'target_guides', help = 'Select mode')

        # -------------- TARGET ----------------
		self.OptionParser.add_option('--horGuides',
            action = 'store', type = 'int', dest = 'horGuides',
            default = '1', help = 'Number of horizontal guides')

		self.OptionParser.add_option('--verGuides',
            action = 'store', type = 'int', dest = 'vGuides',
            default = '1', help = 'Number of vertical guides')

		self.OptionParser.add_option('--delete_target_guides',
            action = 'store', type = 'inkbool', dest = 'delete_target_guides',
            default = 'FALSE', help = 'True/False')

        # -------------- CUSTOM ----------------
		self.OptionParser.add_option('-x', '--xPos',
            action = 'store', type = 'float', dest = 'xPos',
            default = '0.0', help = 'xPosition')

		self.OptionParser.add_option('-y', '--yPos',
            action = 'store', type = 'float', dest = 'yPos',
            default = '0.0', help = 'yPosition')

		self.OptionParser.add_option('-a', '--angle',
            action = 'store', type = 'float', dest = 'angle',
            default = '0.0', help = 'angle')

		self.OptionParser.add_option('--nSteps',
            action = 'store', type = 'int', dest = 'nSteps',
            default = '1', help = 'Number of guides')

		self.OptionParser.add_option('--xStep',
            action = 'store', type = 'float', dest = 'xStep',
            default = '0.0', help = 'x offset')

		self.OptionParser.add_option('--yStep',
            action = 'store', type = 'float', dest = 'yStep',
            default = '0.0', help = 'y offset')

		self.OptionParser.add_option('--rStep',
            action = 'store', type = 'float', dest = 'rStep',
            default = '0.0', help = 'r offset')

		self.OptionParser.add_option('--delete_custom_guides',
            action = 'store', type = 'inkbool', dest = 'delete_custom_guides',
            default = 'FALSE', help = 'True/False')

        # -------------- VECTOR ----------------
		self.OptionParser.add_option('--rightGuide',
            action = 'store', type = 'inkbool', dest = 'rightGuide',
            default = 'FALSE', help = 'True/False')

		self.OptionParser.add_option('--rightGuideNormals',
            action = 'store', type = 'int', dest = 'rightGuideNormals',
            default = '1', help = 'Number of vertical guides')

		self.OptionParser.add_option('--leftGuide',
            action = 'store', type = 'inkbool', dest = 'leftGuide',
            default = 'FALSE', help = 'True/False')

		self.OptionParser.add_option('--leftGuideNormals',
            action = 'store', type = 'int', dest = 'leftGuideNormals',
            default = '1', help = 'Number of vertical guides')

		self.OptionParser.add_option('--delete_vector_guides',
            action = 'store', type = 'inkbool', dest = 'delete_vector_guides',
            default = 'FALSE', help = 'True/False')

    def effect(self):
        # -------------- MODE ----------------
        myMode     = self.options.myMode

        # -------------- TARGET ----------------
        horGuides  = self.options.horGuides
        verGuides  = self.options.vGuides

        svgRoot    = self.document.getroot()
        pageWidth  = self.unittouu(svgRoot.get('width'))
        pageHeight = self.unittouu(svgRoot.attrib['height'])

        namedView  = self.document.find(inkex.addNS('namedview', 'sodipodi'))

        delete_target_guides = self.options.delete_target_guides

        # -------------- CUSTOM ----------------
        xPos    = self.options.xPos
        yPos    = self.options.yPos
        angle   = self.options.angle

        nSteps  = self.options.nSteps
        xStep   = self.options.xStep
        yStep   = self.options.yStep
        rStep   = self.options.rStep

        delete_custom_guides = self.options.delete_custom_guides

        # -------------- VECTOR ----------------
        rightGuideNormals = self.options.rightGuideNormals
        rightGuide        = self.options.rightGuide

        leftGuideNormals  = self.options.leftGuideNormals
        leftGuide         = self.options.leftGuide

        delete_vector_guides = self.options.delete_vector_guides


        # -------------- MODE ----------------
        if myMode == 'remove_guides':
            deleteAllGuides(self.document)

        # -------------- TARGET ----------------
        if myMode == 'target_guides':
            if (delete_target_guides):
                deleteAllGuides(self.document)

            if len(self.options.ids) >= 1 :
                self.bbox = computeBBox(self.selected.values())

                x1 = self.bbox[0]
                x2 = self.bbox[1]
                y1 = self.bbox[2]
                y2 = self.bbox[3]

                if horGuides == 1:
                    xVal = x1
                    yVal = pageHeight - y1 - (y2 - y1) / 2
                    createGuide(str(xVal) + ', ' + str(yVal),
                                '0,1',
                                namedView)
                else:
                    for i in range(horGuides):
                        xVal = x1
                        yVal = pageHeight - y1 - (y2 - y1) / (horGuides -1) * i
                        createGuide(str(xVal) + ', ' + str(yVal),
                                    '0,1',
                                    namedView)

                if verGuides == 1:
                    xVal = x1 + (x2 - x1) / 2
                    yVal = pageHeight - y2
                    createGuide(str(xVal) + ', ' + str(yVal),
                                '1,0',
                                namedView)

                else:
                    for i in range(verGuides):
                        xVal = x1 + (x2 - x1) / (verGuides - 1) * i
                        yVal = pageHeight - y2
                        createGuide(str(xVal) + ', ' + str(yVal),
                                    '1,0',
                                    namedView)

            else:
                if horGuides == 1:
                    xVal = 0.0
                    yVal = pageHeight / 2
                    createGuide(str(xVal) + ', ' + str(yVal),
                                '0,1',
                                namedView)

                else:
                    for i in range(horGuides):
                        xVal = 0.0
                        yVal = pageHeight / (horGuides - 1) * i
                        createGuide(str(xVal) + ', ' + str(yVal),
                                    '0,1',
                                    namedView)

                if verGuides == 1:
                    xVal = pageWidth / 2
                    yVal = 0.0
                    createGuide(str(xVal) + ', ' + str(yVal),
                                '1,0',
                                namedView)

                else:
                    for i in range(verGuides):
                        xVal = pageWidth / (verGuides - 1) * i
                        yVal = 0.0
                        createGuide(str(xVal) + ', ' + str(yVal),
                                    '1,0',
                                    namedView)


        # -------------- CUSTOM ----------------
        if myMode == 'custom_guides':
            if (delete_custom_guides):
                deleteAllGuides(self.document)

            for i in range(nSteps):
                xVal = xPos + (i * xStep)
                yVal = yPos + (i * yStep)
                rise = round(-sin(radians(angle + i * rStep)),10)
                run  = round(cos(radians(angle + i *  rStep)),10)
                createGuide(str(xVal) + ', ' + str(yVal),
                            str(rise) + ', ' + str(run),
                            namedView)


        # -------------- VECTOR ----------------
        if myMode == 'vector_guides':
            if (delete_vector_guides):
                deleteAllGuides(self.document)

            if len(self.options.ids) >= 1 :
                self.bbox = computeBBox(self.selected.values())

                X1 = self.bbox[0]
                X2 = self.bbox[1]
                Y1 = self.bbox[2]
                Y2 = self.bbox[3]

                if (X2 - X1 == 0) or (Y2 - Y1 == 0):
                    inkex.errormsg(_(
                        "To draw perpendicular \n"
                        "(horizontal and/or vertical) \n"
                        "guides, use Target mode."
                        ))
                    exit()

            # -------------- X VECTOR ----------------
                rightSlope = (Y2 - Y1) / (X1 - X2)
                rightRadianAngle = atan(rightSlope)
                rightGuideString = str(
                                       round(sin(rightRadianAngle),10)
                                       ) + ', ' + str(
                                       round(cos(rightRadianAngle),10)
                                       )

                if rightGuide:
                    createGuide(str(X2) + ', ' +
                                str(pageHeight - Y1),
                                rightGuideString,
                                namedView)

            # -------------- X NORMALS ----------------

                rightVectorWidth  = X2 - X1
                rightVectorHeight = Y2 - Y1

                rightRadianAngleNormal = rightRadianAngle + (pi / 2)
                # angle (+ 90) in radians
                # Define normal angles as slope to 10 decimal places
                rightNormalString = str(
                                        round(sin(rightRadianAngleNormal),10)
                                        ) + ',' + str(
                                        round(cos(rightRadianAngleNormal),10)
                                        )

                # rightGuideNormals = number of Normal guides
                # Draw guides on normal orientation
                if rightGuideNormals > 1:
                    for i in range(rightGuideNormals):
                        xAdj = (
                            (rightVectorWidth / (rightGuideNormals - 1)) * i)
                        yAdj = (
                            (rightVectorHeight / (rightGuideNormals - 1)) * i)

                        createGuide(str(X1 + xAdj) + ', ' +
                                    str((pageHeight - Y2) + yAdj ),
                                    rightNormalString,
                                    namedView)
                else:
                    if rightGuideNormals == 1:
                        createGuide(str(X1 + (
                                    rightVectorWidth) / 2) + ', ' +
                                    str(pageHeight - Y1 -
                                    (rightVectorHeight / 2)),
                                    rightNormalString,
                                    namedView)

            # -------------- Y VECTOR ----------------
                leftSlope = (Y1 - Y2) / (X1 - X2)
                leftRadianAngle = atan(leftSlope)  # angle in radians
                leftGuideString = str(
                                      round(sin(leftRadianAngle),10)
                                      ) + ',' + str(
                                      round(cos(leftRadianAngle),10)
                                      )

                if leftGuide:
                    createGuide(str(X1) + ', ' +
                                str(pageHeight - Y1),
                                leftGuideString,
                                namedView)

            # -------------- Y NORMALS ----------------
                leftVectorWidth  = X2 - X1
                leftVectorHeight = Y1 - Y2

                leftRadianAngleNormal = leftRadianAngle - (pi / 2)
                # angle (+ 90) in radians
                # Define normal angles as slope to 10 decimal places
                leftNormalString = str(
                                       round(sin(leftRadianAngleNormal),10)
                                       ) + ',' + str(
                                       round(cos(leftRadianAngleNormal),10)
                                       )

                if leftGuideNormals > 1:
                    for i in range(leftGuideNormals):
                        xAdj = (
                            (leftVectorWidth / (leftGuideNormals - 1)) * i)
                        yAdj = (
                            (leftVectorHeight / (leftGuideNormals - 1)) * i)

                        createGuide(str(X1 + xAdj) + ', ' +
                                    str(pageHeight - Y1 + yAdj),
                                    leftNormalString,
                                    namedView)
                else:
                    if leftGuideNormals == 1:
                        createGuide(str(X1 + (leftVectorWidth) / 2) + ', ' +
                                    str(pageHeight - Y1 +
                                    (leftVectorHeight / 2)),
                                    leftNormalString, namedView)

            else:

            # -------------- X VECTOR ----------------
                rightSlope = -pageHeight / pageWidth
                rightRadianAngle = atan(rightSlope)
                rightGuideString = str(
                                       round(sin(rightRadianAngle),10)
                                       ) + ',' + str(
                                       round(cos(rightRadianAngle),10)
                                       )

                if rightGuide:
                    createGuide(str(pageWidth) + ', ' +
                                str(pageHeight),
                                rightGuideString,
                                namedView)

            # -------------- X NORMALS ----------------
                # Define vector width and height
                rightVectorWidth = pageWidth
                rightVectorHeight = pageHeight

                rightRadianAngleNormal = rightRadianAngle + (pi / 2)
                # angle (+ 90) in radians
                # Define normal angles as slope to 10 decimal places
                rightNormalString = str(
                                        round(sin(rightRadianAngleNormal),10)
                                        ) + ',' + str(
                                        round(cos(rightRadianAngleNormal),10)
                                        )

                # rightGuideNormals = number of Normal guides
                # Draw guides on normal orientation
                if rightGuideNormals > 1:
                    for i in range(rightGuideNormals):
                        xAdj = (
                            (rightVectorWidth / (rightGuideNormals - 1)) * i)
                        yAdj = (
                            (rightVectorHeight / (rightGuideNormals - 1)) * i)

                        createGuide(str(xAdj) + ', ' +
                                    str(yAdj),
                                    rightNormalString,
                                    namedView)

                if rightGuideNormals == 1:
                    createGuide(str((rightVectorWidth) / 2) + ', ' +
                                str( (rightVectorHeight) / 2),
                                rightNormalString, namedView)

            # -------------- Y VECTOR ----------------
                leftSlope = pageWidth / pageHeight
                leftRadianAngle = -atan(leftSlope) + (pi / 2)
                leftGuideString = str(
                                      round(sin(leftRadianAngle),10)
                                      ) + ',' + str(
                                      round(cos(leftRadianAngle),10)
                                      )

                if leftGuide:
                    createGuide(str(0.0) + ', ' +
                                str(pageHeight),
                                leftGuideString,
                                namedView)

            # -------------- Y NORMALS ----------------
                leftVectorWidth = pageWidth
                leftVectorHeight = pageHeight

                leftRadianAngleNormal = leftRadianAngle - (pi / 2)
                # angle (+ 90) in radians
                # Define angles as slope to 10 decimal places
                leftNormalString = str(
                                       round(sin(leftRadianAngleNormal),10)
                                       ) + ',' + str(
                                       round(cos(leftRadianAngleNormal),10)
                                       )

                # leftGuideNormals = number of Normal guides
                # Draw guides on normal orientation
                if leftGuideNormals > 1:
                    for i in range(leftGuideNormals):
                        xAdj = (
                            (leftVectorWidth / (leftGuideNormals - 1)) * i)
                        yAdj = (
                            (leftVectorHeight / (leftGuideNormals - 1)) * i)

                        createGuide(str(xAdj) + ', ' +
                                    str(pageHeight - yAdj),
                                    leftNormalString,
                                    namedView)

                if leftGuideNormals == 1:
                    createGuide(
                                str(leftVectorWidth/2
                                ) + ', ' +
                                str(pageHeight -  (leftVectorHeight/2)),
                                leftNormalString,
                                namedView)

        # -------------- DEBUGGER ----------------
        if debug:
            # message = 'some message'
            inkex.debug(message)


# Create effect instance and apply it.
effect = AddObjects()
effect.affect()
