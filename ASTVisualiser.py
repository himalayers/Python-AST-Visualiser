#ASTVisualiser - visualise python ASTs graphically

import tkinter, astpp, ast
from tkinter import *
from ast import *
import numpy as np
import math

class offsettree(object):
    def __init__(self, offsets, children):
        self.offsets = offsets
        self.children = children

#Given a canvas and an AST
def visualise(node, zoom=1, leftoffset=0, upoffset=0):
    ROOTX = canw/2 + leftoffset*zoom
    ROOTY = 100 + upoffset*zoom
    BWIDTH = 100*zoom
    BHEIGHT = 50*zoom
    YSPACING = 300*zoom
    TEXTSIZE = round(20*zoom)
    PADDING = 25*zoom
    CANVAS.delete("all")
    def _calcsizes(node):
        #if it's a field
        if isinstance(node, tuple):
            #if it's a field of multiple values
            if isinstance(node[1], list):
                sizes = []
                children = []
                for i, item in enumerate(node[1]):
                    result = _calcsizes(item)
                    sizes.append(result[0] + PADDING)
                    children.append(result[1])
                offsets = [item-sum(sizes)/2 for item in [(list(np.cumsum(sizes)) + [0])[i-1] + sizes[i]/2 for i in range(len(sizes))]]
                return sum(sizes), offsettree(offsets, children)
            else:
                result = _calcsizes(node[1])
                return result[0], offsettree(0, [result[1]])
        elif isinstance(node, AST):
            fields = []
            for field, value in iter_fields(node):
                fields.append((field, value))
            sizes = []
            children = []
            for i, field in enumerate(fields):
                result = _calcsizes(field)
                sizes.append(result[0] + PADDING)
                children.append(result[1])
            offsets = [item-sum(sizes)/2 for item in [(list(np.cumsum(sizes)) + [0])[i-1] + sizes[i]/2 for i in range(len(sizes))]]
            return sum(sizes), offsettree(offsets, children)
        else:
            #it's just a piece of text or a number; bigness = itself's width
            return BWIDTH*2, offsettree(0, None)

    def _drawtree(node, offset, offtree, pos=0, maxpos=0, level=0, rootx=ROOTX, rooty=ROOTY):
        #draw this box
        XSPACING = BWIDTH*maxpos*2.5
        #draw box with name node coming from parent
        x1, y1 = rootx-BWIDTH/2 + offset, rooty+YSPACING
        x2, y2 = rootx+BWIDTH/2 + offset, rooty+BHEIGHT+YSPACING
        CANVAS.create_line(x1+(x2-x1)/2,y1,rootx,rooty+BHEIGHT/2)

        #recurse on fields or list items
        if isinstance(node, tuple):
            CANVAS.create_rectangle(x1, y1, x2, y2, fill="light cyan")
            CANVAS.create_text(x1+BWIDTH/2, y1+BHEIGHT/2, font=("Purisa", TEXTSIZE), text=node[0])
            if isinstance(node[1], list):
                #look up the offset tree to see how these list members should be offset, and pass it down
                for i, item in enumerate(node[1]):
                    _drawtree(item, offtree.offsets[i], offtree.children[i], pos=i, maxpos=len(node[1])-1, level=level+1, rootx=x1+(x2-x1)/2, rooty=y1+(y2-y1)/2)
            else:
                _drawtree(node[1], 0, offtree.children[0], pos=0, maxpos=0, level=level+1, rootx=x1+(x2-x1)/2, rooty=y1+(y2-y1)/2)
        elif isinstance(node, AST):
            CANVAS.create_rectangle(x1, y1, x2, y2, fill="white")
            CANVAS.create_text(x1+BWIDTH/2, y1+BHEIGHT/2, font=("Purisa", TEXTSIZE), text=node.__class__.__name__)
            fields = []
            for field, value in iter_fields(node):
                fields.append((field, value))
            for i, field in enumerate(fields):
                _drawtree(field, offtree.offsets[i], offtree.children[i], pos=i, maxpos=len(fields)-1, level=level+1, rootx=x1+(x2-x1)/2, rooty=y1+(y2-y1)/2)
        else:
            CANVAS.create_text(x1+BWIDTH/2, y1+BHEIGHT/2, font=("Purisa", TEXTSIZE), text=node)

    treesize, offtree = _calcsizes(node)
    _drawtree(node, 0, offtree)

global CANVAS
master = Tk()
canw, canh = 1300, 800
CANVAS = Canvas(master, width=canw, height=canh)
CANVAS.pack()
loffset, uoffset = 0, 0
zoom = 0.05
speed = 500
mouseposx, mouseposy = 0, 0

def leftKey(event):
    global loffset
    loffset += speed
    visualise(tree, CANVAS, zoom, loffset, uoffset)
def rightKey(event):
    global loffset
    loffset -= speed
    visualise(tree, CANVAS, zoom, loffset, uoffset)
def upKey(event):
    global uoffset
    uoffset += speed
    visualise(tree, CANVAS, zoom, loffset, uoffset)
def downKey(event):
    global uoffset
    uoffset -= speed
    visualise(tree, CANVAS, zoom, loffset, uoffset)
def mouseWheel(event):
    global zoom, loffset, uoffset
    if event.delta == -120:
        zoom /= 1.5
    if event.delta == 120:
        zoom *= 1.5
        loffset -= (event.x)*(zoom)*2
        uoffset -= (event.y)*(zoom)*2
    visualise(tree, CANVAS, zoom, loffset, uoffset)
def mouseDown(event):
    global mouseposx, mouseposy
    mouseposx, mouseposy = event.x, event.y
def mouseMove(event):
    global uoffset, loffset, mouseposx, mouseposy
    loffset += (event.x - mouseposx)*(1/zoom)
    uoffset += (event.y - mouseposy)*(1/zoom)
    mouseposx, mouseposy = event.x, event.y
    visualise(tree, CANVAS, zoom, loffset, uoffset)
#master.bind('<Left>', leftKey)
master.bind('<KeyPress-Left>', leftKey)
master.bind('<Right>', rightKey)
master.bind('<Up>', upKey)
master.bind('<Down>', downKey)
master.bind('a', leftKey)
master.bind('d', rightKey)
master.bind('w', upKey)
master.bind('s', downKey)
master.bind('<MouseWheel>', mouseWheel)
master.bind('<B1-Motion>', mouseMove)
master.bind('<Button-1>', mouseDown)
