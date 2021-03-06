#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
LJay
v0.7.0

LICENCE : CC
Sam Neurohack, Loloster, 

set0 collect code examples to make your own generators that use LJay Laser management.

Curve 0 : Mapping introduce an editor mode allowing to modify all points one by one.
Curve 1 : xPLS how to have different pointlists generators
Curve 2 : Orbits
Curve 3 : Dots
Curve 4 : Sine
Curve 5 : Astro
Curve 6 : Text
Curve 7 : Pose
'''


import math
import gstt
from globalVars import *
import bhoroscp
import colorify
import numpy as np
import pdb
import time
from datetime import datetime
import settings
import font1

'''
# for Astro()
from jplephem.spk import SPK
kernel = SPK.open('de430.bsp')
jd = datetime.now()
gstt.year = jd.year
gstt.month = jd.month
gstt.day = jd.day
gstt.JulianDate = 367 * gstt.year - 7 * (gstt.year + (gstt.month + 9)/12)/4 + 275 * gstt.month/9 + gstt.day + 1721014
print ""
print "For Astro(), today : ", datetime.now().strftime('%Y-%m-%d'), "is in Julian : ", gstt.JulianDate
'''

# For Orbits()
import orbits
orbits = orbits.Orbits()

# For Mapping()
# dedicated settings handler is in settings.py
import pygame

f_sine = 0



# Curve 0
# Edit shape mode / Warp Mode

def MappingConf(section):
    global mouse_prev, sections, warpd

    gstt.EditStep = 0
    gstt.CurrentWindow = -1
    gstt.CurrentCorner = 0
    gstt.CurrentSection = section
    mouse_prev = ((405, 325), (0, 0, 0))

    # Get all shapes points (="corners") for the given section of the conf file -> gstt.Windows 
    gstt.Windows = [] 
    sections = settings.MappingSections()

    print ""
    #print "Sections : ", sections
    print "Reading Section : ", sections[gstt.CurrentSection]

    gstt.Laser = settings.MappingRead([sections[gstt.CurrentSection],'laser'])
    print "Laser : ", gstt.Laser
    gstt.simuPL = gstt.Laser
    warpd = np.array(gstt.warpdest[gstt.Laser])

    for Window in xrange(settings.Mapping(sections[gstt.CurrentSection])-1):
        if gstt.debug > 0:
            print "Reading option :  ", str(Window)
        shape = [sections[gstt.CurrentSection], str(Window)]
        WindowPoints = settings.MappingRead(shape)
        gstt.Windows.append(WindowPoints)

    print "Section points : " ,gstt.Windows



def Mapping(fwork, keystates, keystates_prev):
    global mouse_prev, sections, warpd

    PL = gstt.Laser
    dots = []


    #switch to edit mode Key E ?
    if keystates[pygame.K_e] and not keystates_prev[pygame.K_e] and gstt.EditStep == 0:
            print "Switching to Edit Mode"
            gstt.EditStep = 1
            gstt.CurrentWindow = 0
            gstt.CurrentCorner = 0

    # Back to WARP mode if ENTER key is pressed ?
    if keystates[pygame.K_RETURN] and gstt.EditStep == 1:    
            
            print "Switching to Warp Mode"
            gstt.EditStep =0
            gstt.CurrentCorner = 0




    # EDIT MODE : cycle windows if press e key to adjust corner position 
    # Escape edit mode with enter key
    if gstt.EditStep >0:

        dots = []
        CurrentWindowPoints = gstt.Windows[gstt.CurrentWindow]

        # Draw all windows points or "corners"
        for corner in xrange(len(CurrentWindowPoints)):   
            dots.append(proj(int(CurrentWindowPoints[corner][0]),int(CurrentWindowPoints[corner][1]),0))
        fwork.PolyLineOneColor( dots, c=colorify.rgb2hex(gstt.color), PL = PL, closed = False )

        # Left mouse is clicked, modify current Corner coordinate
        if gstt.mouse[1][0] == mouse_prev[1][0] and mouse_prev[1][0] == 1:
            deltax = gstt.mouse[0][0]-mouse_prev[0][0]
            deltay = gstt.mouse[0][1]-mouse_prev[0][1]
            CurrentWindowPoints[gstt.CurrentCorner][0] += (deltax *2)
            CurrentWindowPoints[gstt.CurrentCorner][1] -= (deltay * 2)

        # Change corner if Z key is pressed.
        if keystates[pygame.K_z] and not keystates_prev[pygame.K_z]:
            if gstt.CurrentCorner < settings.Mapping(sections[gstt.CurrentSection]) - 1:
                gstt.CurrentCorner += 1
                print "Corner : ", gstt.CurrentCorner

        # Press E inside Edit mode : Next window 
        if keystates[pygame.K_e] and not keystates_prev[pygame.K_e]:

            # Save current Window and switch to the next one.
            if gstt.CurrentWindow < settings.Mapping(sections[gstt.CurrentSection]) -1:
                print "saving "
                settings.MappingWrite(sections,str(gstt.CurrentWindow),CurrentWindowPoints)
                gstt.CurrentWindow += 1
                gstt.CurrentCorner = -1
                if gstt.CurrentWindow == settings.Mapping(sections[gstt.CurrentSection]) -1:
                    gstt.EditStep == 0
                    gstt.CurrentWindow = 0              
                print "Now Editing window ", gstt.CurrentWindow

        mouse_prev = gstt.mouse
        gstt.PL[PL] = fwork.LinesPL(PL)

    # Press A : Next section ?
    if keystates[pygame.K_a] and not keystates_prev[pygame.K_a]: 
            
        print "current section : ", gstt.CurrentSection
        if gstt.CurrentSection < len(sections)-1:
            gstt.CurrentSection += 1
            print "Next section name is ", sections[gstt.CurrentSection]
            if "screen" in sections[gstt.CurrentSection]:
                print ""
                print "switching to section ", gstt.CurrentSection, " ", sections[gstt.CurrentSection]
                MappingConf(gstt.CurrentSection)
        else:
             gstt.CurrentSection = -1
        



    # WARP Mode
    if gstt.EditStep == 0:
        
        #print "Warp mode"
        # Left mouse is clicked, modify current Corner coordinate
        #print gstt.mouse
        if gstt.mouse[1][0] == mouse_prev[1][0] and mouse_prev[1][0] == 1:
            deltax = gstt.mouse[0][0]-mouse_prev[0][0]
            deltay = gstt.mouse[0][1]-mouse_prev[0][1]
            
            print "Laser ", gstt.Laser, " Corner ", gstt.CurrentCorner, "deltax ", deltax, "deltay", deltay
            #int(gstt.warpdest[gstt.Laser][gstt.CurrentCorner][0]) += (deltax *20)
            #int(gstt.warpdest[gstt.Laser][gstt.CurrentCorner][1]) += (deltay * 2)
            
            print warpd

            #print int(gstt.warpdest[gstt.Laser][gstt.CurrentCorner][0]) + (deltax * 20)
        # Change corner if Z key is pressed.
        if keystates[pygame.K_z] and not keystates_prev[pygame.K_z]:
            if gstt.CurrentCorner < 4:
                gstt.CurrentCorner += 1
                print "Corner : ", gstt.CurrentCorner


        # Display all windows to current PL for display
        for Window in gstt.Windows:  

            dots = []
            for corner in xrange(len(Window)):   
                #print "Editing : ", WindowPoints[corner]
                #print Window[corner][0]
                dots.append(proj(int(Window[corner][0]),int(Window[corner][1]),0))
            
            fwork.PolyLineOneColor( dots, c=colorify.rgb2hex(gstt.color), PL = PL, closed = False  )
    
        gstt.PL[PL] = fwork.LinesPL(PL)

        mouse_prev = gstt.mouse




# Curve 1
def xPLS(fwork):
    global f_sine


    # point list "PL" 0 generator (assigned to a laser in gstt.lasersPLS) 
    # middle horizontal line

    PL = 0
    dots = []
    x = (int(screen_size[1]) / 2) - 50
    y = (int(screen_size[0])/2)
    dots.append((int(x),int(y)))
    dots.append((int((int(screen_size[1]) / 2) + 50),(int(y))))
    fwork.PolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color), PL = 0, closed = False)
    gstt.PL[PL] = fwork.LinesPL(PL)
   
    

    # PL 1 generator (assigned to a laser in gstt.lasersPLS)
    # middle vertical line

    PL = 1
    dots = []
    #pdb.set_trace()
    x = int(screen_size[1]) / 2
    y = (int(screen_size[1])/2) -50
    dots.append((int(x),int(y)))
    dots.append((int(x),(int(screen_size[1])/2)+50))
    fwork.PolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color), PL = 1, closed = False)
    gstt.PL[PL] = fwork.LinesPL(PL)
    
  

    # PL 2 generator (assigned to a laser in gstt.lasersPLS)
    PL = 2
    dots = []     
    amp = 200
    nb_point = 40
    for t in range(0, nb_point+1):
        y = 0 - amp*math.sin(2 * PI * (float(t)/float(nb_point)))
        x = 0 - amp*math.cos(2 * PI * f_sine *(float(t)/float(nb_point)))
        dots.append(proj(int(x),int(y),0))
    fwork.PolyLineOneColor ( dots, c = colorify.rgb2hex(gstt.color), PL =  2, closed = False)
    gstt.PL[PL] = fwork.LinesPL(PL)
    
    if f_sine > 24:
        f_sine = 0
    f_sine += 0.01




# Curve 2

def Orbits(fwork):
    orbits.Draw(fwork)



# Curve 3	
def Dot(fwork):

    
    PL = 0
    dots = []
    x = cc2scrX(gstt.cc[5])
    y = cc2scrY(gstt.cc[6])
    #x = xy_center[0] + gstt.cc[5]*amp    
    #y = xy_center[1] + gstt.cc[6]*amp
    #print x,y,proj(int(x),int(y),0)
    dots.append(proj(int(x),int(y),0))
    dots.append(proj(int(x)+5,int(y)+5,0))
      
    fwork.PolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color), PL = 0, closed = False)
    gstt.PL[PL] = fwork.LinesPL(PL)



# Curve 4

def Sine(fwork):
    global f_sine

    PL = 0
    dots = []
    etherlaser = 2
    amp = 200
    nb_point = 40
    for t in range(0, nb_point+1):
        y = 0 - amp*math.sin(2 * PI * (float(t)/float(nb_point)))
        x = 0 - amp*math.cos(2 * PI * f_sine *(float(t)/float(nb_point)))
        dots.append(proj(int(x),int(y),0))

    fwork.PolyLineOneColor ( dots, c = colorify.rgb2hex(gstt.color), PL =  PL, closed = False)
    
    gstt.PL[PL] = fwork.LinesPL(PL)
    
    if f_sine > 24:
        f_sine = 0
    f_sine += 0.01


# Curve 5
# imports and other init values may be commented at the beginning of this file.
# ephemerids are quite big and add other dependencies so keep commented if astro is not needed.
def Astro(fwork):

    PlanetsPositions = []
    dots = []
    amp = 0.8

    # get solar planet positions
    for planet in xrange(9):
        PlanetsPositions.append(kernel[0,planet+1].compute(gstt.JulianDate))



    # first 5 planets goes to PL 0
    PL = 0
    for planet in xrange(5):
        x,y,z = planet2screen(PlanetsPositions[planet][0], PlanetsPositions[planet][1], PlanetsPositions[planet][2])
        x,y = proj(int(x),int(y),int(z))
        x = x * amp 
        y = y * amp + 60
        #dots.append((int(x)-300,int(y)+200))
        #dots.append((int(x)-295,int(y)+205))
        fwork.Line((x,y),(x+2,y+2),  c=colorify.rgb2hex(gstt.color), PL=0 )

    gstt.PL[PL] = fwork.LinesPL(PL)


    # Last planets goes to PL 1
    PL = 1

    for planet in range(5,9):
        #print "1 ", planet
        x,y,z = planet2screen(PlanetsPositions[planet][0], PlanetsPositions[planet][1], PlanetsPositions[planet][2])
        x,y = proj(int(x),int(y),int(z))
        x = x * amp 
        y = y * amp + 60
        #dots.append((int(x)-300,int(y)+200))
        #dots.append((int(x)-295,int(y)+205))
        fwork.Line((x,y),(x+2,y+2),  c=colorify.rgb2hex(gstt.color), PL=1 )

    gstt.PL[PL] = fwork.LinesPL(PL)


    #time.sleep(0.001)
    gstt.JulianDate +=1


# Curve 6 : LaserID : cast '0' on laser 0, "1" on laser "1",...
def LaserID(fwork):
    
    # "0" on laser 0
    message = "0"

    len_message = len(message)
    i= 0
    for char in message:
        i +=1
        # x offset for each letter depends on message length
        x_offset = 26 * (- (0.9 * len_message) + 3*i)
        char_dots = font1.ASCII_GRAPHICS[ord(char) - 47]

        for dot_pl in char_dots:
            dots = []
            for dot in dot_pl:
                dots.append((x_offset+dot[0],dot[1]))

            fwork.rPolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = 200, ypos = 200, resize = 1)
   
    gstt.PL[0] = fwork.LinesPL(0)
 

     # "1" on laser 1
    message = "1"

    len_message = len(message)
    i= 0
    for char in message:
        i +=1
        # x offset for each letter depends on message length
        x_offset = 26 * (- (0.9 * len_message) + 3*i)
        char_dots = font1.ASCII_GRAPHICS[ord(char) - 47]

        for dot_pl in char_dots:
            dots = []
            for dot in dot_pl:
                dots.append((x_offset+dot[0],dot[1]))

            fwork.rPolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color),  PL = 1, closed = False, xpos = 200, ypos = 200, resize = 1)
   
    gstt.PL[1] = fwork.LinesPL(1)



    # "2" on laser 2
    message = "2"

    len_message = len(message)
    i= 0
    for char in message:
        i +=1
        # x offset for each letter depends on message length
        x_offset = 26 * (- (0.9 * len_message) + 3*i)
        char_dots = font1.ASCII_GRAPHICS[ord(char) - 47]

        for dot_pl in char_dots:
            dots = []
            for dot in dot_pl:
                dots.append((x_offset+dot[0],dot[1]))

            fwork.rPolyLineOneColor(dots, c=colorify.rgb2hex(gstt.color),  PL = 2, closed = False, xpos = 200, ypos = 200, resize = 1)
   
    gstt.PL[2] = fwork.LinesPL(2)




# Curve 7
import json
gstt.CurrentPose = 1

# get absolute body position points
def getCOCO(pose_json,pose_points, people):
    
    dots = []
    for dot in pose_points:
        if len(pose_json['part_candidates'][people][str(dot)]) != 0:
            dots.append((pose_json['part_candidates'][people][str(dot)][0], pose_json['part_candidates'][people][str(dot)][1]))
    return dots


# get relative (-1 0 1) body position points. a position -1, -1 means doesn't exist
def getBODY(pose_json,pose_points, people):

    dots = []
    for dot in pose_points:
        #print pose_points
        if len(pose_json['people'][people]['pose_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][people]['pose_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][people]['pose_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][people]['pose_keypoints_2d'][dot * 3], pose_json['people'][people]['pose_keypoints_2d'][(dot * 3)+1]))


    return dots


# get absolute face position points 
def getFACE(pose_json,pose_points, people):

    dots = []
    for dot in pose_points:

        if len(pose_json['people'][people]['face_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][people]['face_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][people]['face_keypoints_2d'][dot * 3], pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1]))
        '''
        if len(pose_json['people']) > 1:
            print len(pose_json['people']) 
            print "people 1 face ", pose_json['people'][1]['face_keypoints_2d']
        '''

    return dots


# Body parts
def bodyCOCO(pose_json, people ):
    pose_points = [10,9,8,1,11,12,13]
    return getBODY(pose_json,pose_points, people)

def armCOCO(pose_json, people):
    pose_points = [7,6,5,1,2,3,4]
    return getBODY(pose_json,pose_points, people)

def headCOCO(pose_json, people):
    pose_points = [1,0]
    return getBODY(pose_json,pose_points)


# Face keypoints
def face(pose_json, people):
    pose_points = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    return getFACE(pose_json,pose_points, people)

def browL(pose_json, people):
    pose_points = [26,25,24,23,22]
    return getFACE(pose_json,pose_points, people)

def browR(pose_json, people):
    pose_points = [21,20,19,18,17]
    return getFACE(pose_json,pose_points, people)

def eyeR(pose_json, people):
    pose_points = [36,37,38,39,40,41,36]
    return getFACE(pose_json,pose_points, people)

def eyeL(pose_json, people):
    pose_points = [42,43,44,45,46,47,42]
    return getFACE(pose_json,pose_points, people)

def nose(pose_json, people):
    pose_points = [27,28,29,30]
    return getFACE(pose_json,pose_points, people)

def mouth(pose_json, people):
    pose_points = [48,59,58,57,56,55,54,53,52,51,50,49,48,60,67,66,65,64,63,62,61,60]
    return getFACE(pose_json,pose_points, people)


# best order face : face browL browr eyeR eyeL nose mouth

import os 
anim = ['anim1',50,400,100,0,0,0,1]
# Get frame number for pose path describe in gstt.PoseDir 
def lengthPOSE(pose_dir):

    if gstt.debug > 0:
      print "Check directory ",'poses/' + pose_dir,
    gstt.numfiles = sum(1 for f in os.listdir('poses/' + pose_dir) if os.path.isfile(os.path.join('poses/' + pose_dir + '/', f)) and f[0] != '.')
    if gstt.debug > 0:
      print gstt.numfiles, "images"

#pose_dir = 'detroit1'
pose_dir = 'snap'

lengthPOSE(pose_dir)

# display the pose animation describe in gstt.PoseDir
def Pose(fwork):

    PL = 0
    dots = []
    #posename =gstt.PoseDir+'snap_000000000'+str("%03d"%gstt.CurrentPose)+'_keypoints.json'
    #pose_dir = 'detroit1'

    
    #gstt.numfiles = sum(1 for f in os.listdir('poses/' + pose_dir + '/') if os.path.isfile(os.path.join('poses/' + pose_dir + '/', f)) and f[0] != '.')
    #print "Pose : ", pose_dir, gstt.numfiles, "images"
    posename = 'poses/' + pose_dir + '/' + pose_dir +'-'+str("%05d"%gstt.CurrentPose)+'.json'

    # skip empty filed
    while os.path.getsize(posename) == 159 or os.path.getsize(posename) == 430:
        posename = 'poses/' + pose_dir + '/' + pose_dir +'-'+str("%05d"%gstt.CurrentPose)+'.json'
        if gstt.keystates[pygame.K_w]:
            gstt.CurrentPose -= 1
        if gstt.keystates[pygame.K_x]:
            gstt.CurrentPose += 1

    posefile = open(posename , 'r') 
    posedatas = posefile.read()
    pose_json = json.loads(posedatas)

    # Body
    '''
    print ""
    print "Frame : ",gstt.CurrentPose
    print "body :", bodyCOCO(pose)
    print "arm :", armCOCO(pose)
    print 'head :', headCOCO(pose) 
    print "eyeR :", eyeR(pose)
    print "eyeL :", eyeL(pose)
    print "mouth :", mouth(pose) 
    
    fwork.rPolyLineOneColor(bodyCOCO(pose_json,0), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(armCOCO(pose_json,0), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    #fwork.rPolyLineOneColor(headCOCO(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    
    # Face
    #fwork.rPolyLineOneColor(face(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(browL(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(browR(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(eyeR(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(eyeL(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    fwork.rPolyLineOneColor(nose(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)  
    fwork.rPolyLineOneColor(mouth(pose), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)

    if len(pose_json['people']) != 1:
        print "people 1 pose ", pose_json['people'][1]['pose_keypoints_2d']
        print len(pose_json['people'])
        fwork.rPolyLineOneColor(bodyCOCO(pose_json,1), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
        fwork.rPolyLineOneColor(armCOCO(pose_json,1), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 200)
    '''

    for people in range(len(pose_json['people'])):
        fwork.rPolyLineOneColor(bodyCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)
        fwork.rPolyLineOneColor(armCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)

        fwork.rPolyLineOneColor(browL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)
        fwork.rPolyLineOneColor(browR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)
        fwork.rPolyLineOneColor(eyeR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)
        fwork.rPolyLineOneColor(eyeL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)
        fwork.rPolyLineOneColor(nose(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)  
        fwork.rPolyLineOneColor(mouth(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = 200, ypos = 200, resize = 300)

    
    gstt.PL[PL] = fwork.LinesPL(PL)

    # decrease current frame 
    if gstt.keystates[pygame.K_w]: # and not gstt.keystates_prev[pygame.K_w]:
        gstt.CurrentPose -= 1
        if gstt.CurrentPose < 2:
            gstt.CurrentPose = gstt.numfiles -1
        #time.sleep(0.033) 
        print "Frame : ",gstt.CurrentPose 

    # increaser current frame
    if gstt.keystates[pygame.K_x]: # and not gstt.keystates_prev[pygame.K_x]:
        gstt.CurrentPose += 1
        if gstt.CurrentPose > gstt.numfiles -1:
            gstt.CurrentPose = 1
        #time.sleep(0.033)
        print "Frame : ",gstt.CurrentPose 





# examples to generate arrays of different types i.e for Lissajoux point lists generators.
def ssawtooth(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww])
	return samparray

def ssquare(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = signal.square(2 * np.pi * freq * t[ww])
	return samparray

def ssine(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = np.sin(2 * np.pi * freq  * t[ww])
	return samparray


# Remap values in different scales i.e CC value in screen position.
def cc2scrX(s):
    a1, a2 = 0,127  
    b1, b2 = -screen_size[0]/2, screen_size[0]/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def cc2scrY(s):
    a1, a2 = 0,127  
    b1, b2 = -screen_size[1]/2, screen_size[1]/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def cc2range(s,min,max):
    a1, a2 = 0,127  
    b1, b2 = min, max
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def extracc2scrX(s):
    a1, a2 = -66000,66000  
    b1, b2 = 0, screen_size[0]
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def extracc2scrY(s):
    a1, a2 = -66000,66000 
    b1, b2 = 0, screen_size[1]
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def extracc2range(s,min,max):
    a1, a2 = -66000,66000  
    b1, b2 = min, max
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def planet2screen(planetx, planety, planetz):
    #screen_size = [800,600]
    a1, a2 = -1e+9,1e+9  
    b1, b2 = 0, screen_size[1]
    x = b1 + ((planetx - a1) * (b2 - b1) / (a2 - a1))
    b1, b2 = 0, screen_size[1]
    y = b1 + ((planety - a1) * (b2 - b1) / (a2 - a1))
    b1, b2 = 0, screen_size[1]
    z = b1 + ((planetz - a1) * (b2 - b1) / (a2 - a1))
    return x,y,z


# 3D rotation and 2D projection for a given 3D point
def proj(x,y,z):

    # Skip trigo update if angleX didn't change 
    # TODO : gstt.prev_cc29 == -1 is useful only the first time to create cosa and sina values

    if gstt.prev_cc29 != gstt.cc[29] or gstt.prev_cc29 == -1: 
        gstt.angleX += cc2range(gstt.cc[29],0,0.1)    
        rad = gstt.angleX * PI / 180
        cosaX = math.cos(rad)
        sinaX = math.sin(rad)
        prev_cc29 = gstt.cc[29]

    y2 = y
    y = y2 * cosaX - z * sinaX
    z = y2 * sinaX + z * cosaX

    # Skip trigo update if angleY didn't change 
    if gstt.prev_cc30 != gstt.cc[30]: 
        gstt.angleY += cc2range(gstt.cc[30],0,0.1)
        rad = gstt.angleY * PI / 180
        cosaY = math.cos(rad)
        sinaY = math.sin(rad)
        prev_cc30 = gstt.cc[30]

    z2 = z
    z = z2 * cosaY - x * sinaY
    x = z2 * sinaY + x * cosaY


    # Skip trigo update if angleZ didn't change 
    if gstt.prev_cc31 != gstt.cc[31]: 
        gstt.angleZ += cc2range(gstt.cc[31],0,0.1)
        rad = gstt.angleZ * PI / 180
        cosZ = math.cos(rad)
        sinZ = math.sin(rad)
        
    x2 = x
    x = x2 * cosZ - y * sinZ
    y = x2 * sinZ + y * cosZ

    # 3D to 2D projection
    factor = 4 * gstt.cc[22] / ((gstt.cc[21] * 8) + z)
    x = x * factor + xy_center [0] 
    y = - y * factor + xy_center [1] 
    
    return x,y


def joypads():

    if gstt.Nbpads > 0:
        
        # Champi gauche
        # Move center on X axis according to pad
        if gstt.pad1.get_axis(2)<-0.1 or gstt.pad1.get_axis(2)>0.1:
            gstt.cc[1] += gstt.pad1.get_axis(2) * 2

        # Move center on Y axis according to pad
        if gstt.pad1.get_axis(3)<-0.1 or gstt.pad1.get_axis(3)>0.1:
            gstt.cc[2] += gstt.pad1.get_axis(3) * 2

        # Champi droite
        '''
        # Change FOV according to joypad
        if gstt.pad1.get_axis(0)<-0.1 or gstt.pad1.get_axis(0)>0.1:
            gstt.cc[21] += -gstt.pad1.get_axis(0) * 2

        # Change dist according to pad
        if gstt.pad1.get_axis(1)<-0.1 or gstt.pad1.get_axis(1)>0.1:
            gstt.cc[22] += gstt.pad1.get_axis(1) * 2
        ''' 
        # "1" pygame 0
        # "2" pygame 1
        # "3" pygame 2
        # "4" pygame 3
        # "L1" pygame 4
        # "L2" pygame 6
        # "R1" pygame 5
        # "R2" pygame 7
            
        # Hat gauche gstt.pad1.get_hat(0)[0] = -1
        # Hat droit  gstt.pad1.get_hat(0)[0] = 1

        # Hat bas gstt.pad1.get_hat(0)[1] = -1
        # Hat haut  gstt.pad1.get_hat(0)[1] = 1
        
                
        #Bouton "3" 1 : surprise ON
        
        if gstt.pad1.get_button(2) == 1 and gstt.surprise == 0:
            gstt.surprise = 1
            gstt.cc[21] = 21    #FOV
            gstt.cc[22] = gstt.surpriseon   #Distance
            gstt.cc[2] +=  gstt.surprisey
            gstt.cc[1] +=  gstt.surprisex
            print "Surprise ON"
        
        #Bouton "3" 0 : surprise OFF
        
        if gstt.pad1.get_button(2) == 0:
            gstt.surprise = 0
            gstt.cc[21] = 21    #FOV
            gstt.cc[22] = gstt.surpriseoff  #Distance
            
        #Bouton "4". cycle couleur
        
        #if gstt.pad1.get_button(3) == 1:
        #   print "3", str(gstt.pad1.get_button(3))
        '''
        if gstt.pad1.get_button(3) == 1:
            newcolor = random.randint(0,2)
            print newcolor
            
            if gstt.color[newcolor] == 0:
                gstt.color[newcolor] = 1
                
            else:
                gstt.color[newcolor] = 0
                
            print "Newcolor  : ",str(gstt.newcolor), " ", str(gstt.color[newcolor])
        
        '''
                
        '''
        #Bouton "3" : diminue Vitesse des planetes
        if gstt.pad1.get_button(2) == 1:
            print "2", str(gstt.pad1.get_button(2))
        if gstt.pad1.get_button(2) == 1 and gstt.cc[5] > 2:
            gstt.cc[5] -=1
            print "X Curve : ",str(gstt.cc[5])
            
            
        #Bouton "1" : augmente Vitesse des planetes
        if gstt.pad1.get_button(0) == 1:
            print "0", str(gstt.pad1.get_button(0))
        if gstt.pad1.get_button(0) == 1 and gstt.cc[5] < 125:
            gstt.cc[5] +=1
            print "X Curve : ",str(gstt.cc[5])
            
            
        #Bouton "4". diminue Nombre de planetes
        if gstt.pad1.get_button(3) == 1:
            print "3", str(gstt.pad1.get_button(3))
        if gstt.pad1.get_button(3) == 1 and gstt.cc[6] > 2:
            gstt.cc[6] -=1
            print "Y Curve : ",str(gstt.cc[6])
        
        
        
        #Bouton "2" augmente Nombre de planetes
        if gstt.pad1.get_button(1) == 1:
            print "1", str(gstt.pad1.get_button(1))
        if gstt.pad1.get_button(1) == 1 and gstt.cc[6] < 125:
            gstt.cc[6] +=1
            print "Y Curve : ",str(gstt.cc[6])
        
        '''


        # Hat bas : diminue Vitesse des planetes
        #if gstt.pad1.get_hat(0)[1] == -1:
            #print "2", str(gstt.pad1.get_hat(0)[1])
        if gstt.pad1.get_hat(0)[1] == -1 and gstt.cc[5] > 2:
            gstt.cc[5] -=1
            print "X Curve/vitesse planete : ",str(gstt.cc[5])
            
            
        #Hat haut : augmente Vitesse des planetes
        #if gstt.pad1.get_hat(0)[1] == 1:
            #print "0", str(gstt.pad1.get_hat(0)[1])
        if gstt.pad1.get_hat(0)[1] == 1 and gstt.cc[5] < 125:
            gstt.cc[5] +=1
            print "X Curve/Vitesse planete : ",str(gstt.cc[5])
            
            
        # hat Gauche. diminue Nombre de planetes
        #if gstt.pad1.get_hat(0)[0] == -1:
            #print "3", str(gstt.pad1.get_hat(0)[0])
        if gstt.pad1.get_hat(0)[0] == -1 and gstt.cc[6] > 2:
            gstt.cc[6] -=1
            print "Y Curve/ nombre planete : ",str(gstt.cc[6])
        
        
        
        # hat droit augmente Nombre de planetes
        #if gstt.pad1.get_hat(0)[0] == 1:
            #print "1", str(gstt.pad1.get_hat(0)[0])
        if gstt.pad1.get_hat(0)[0] == 1 and gstt.cc[6] < 125:
            gstt.cc[6] +=1
            print "Y Curve/nb de planetes : ",str(gstt.cc[6])
        
        #print "hat : ", str(gstt.pad1.get_hat(0)[1])

        

