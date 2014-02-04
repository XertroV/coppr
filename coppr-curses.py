#!/usr/bin/python
# coding=UTF-8

import time, curses, locale, sys
from ethereum import *

locale.setlocale(locale.LC_ALL,"")

height = 40
width = 150
w1 = 76
w2 = 71

junc = [
	(0,77),
	(8,0),
	(8,77),
	(20,77),
	(20,149),
	(39,77)
]


def borderHor(n):
	return '═'*n
def borderVer(n):
	return '║'*n

def run(stdscr):
	pad = curses.newpad(height, width)

	curses.curs_set(0)
	curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
	GREENBLACK = curses.color_pair(1)
	curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_WHITE)
	BLACKWHITE = curses.color_pair(2)
	curses.init_pair(3,curses.COLOR_BLACK,curses.COLOR_GREEN)
	BLACKGREEN = curses.color_pair(3)
	curses.init_pair(4,curses.COLOR_WHITE,curses.COLOR_BLACK)
	WHITEBLACK = curses.color_pair(4)
	
	
	active_win = 2
	asm_index = 0
	
	# create subpads and borders - 11 total
	borders = [
		pad.subpad(1,150,0,0),
		pad.subpad(1,150,39,0),
		pad.subpad(39,1,1,0),
		pad.subpad(39,1,1,77),
		pad.subpad(39,1,1,148),
		pad.subpad(1,77,8,1),
		pad.subpad(1,72,20,78)
	]
	
	windows = [
		pad.subpad(7,w1,1,1),
		pad.subpad(19,w2,1,78),
		pad.subpad(30,w1,9,1),
		pad.subpad(18,w2,21,78)
	]
	
	def drawborders(active=None):
		borders[0].addstr(0,0,'█'*(width-1),curses.COLOR_RED)
		borders[1].addstr(0,0,'█'*(width-1))
		borders[2].addstr(0,0,'█'*(height-2))
		borders[3].addstr(0,0,'█'*(height-2))
		borders[4].addstr(0,0,'█'*(height-2))
		borders[5].addstr(0,0,'█'*(w1))
		borders[6].addstr(0,0,'█'*(w2))
		
		if active == 0:
			borders[0].addstr(0,0,'█'*(w1+2),GREENBLACK)
			borders[5].addstr(0,0,'█'*(w1),GREENBLACK)
			borders[2].addstr(0,0,'█'*(junc[1][0]),GREENBLACK)
			borders[3].addstr(0,0,'█'*(junc[2][0]),GREENBLACK)
		elif active == 1:
			borders[0].addstr(0,w1+1,'█'*(w2+1),GREENBLACK)
			borders[6].addstr(0,0,'█'*(w2-1),GREENBLACK)
			borders[3].addstr(0,0,'█'*(junc[3][0]),GREENBLACK)
			borders[4].addstr(0,0,'█'*(junc[4][0]),GREENBLACK)
		elif active == 2:
			borders[5].addstr(0,0,'█'*(w1),GREENBLACK)
			borders[1].addstr(0,0,'█'*(w1+2),GREENBLACK)
			borders[2].addstr(junc[1][0]-1,0,'█'*(height-junc[1][0]-1),GREENBLACK)
			borders[3].addstr(junc[1][0]-1,0,'█'*(height-junc[2][0]-1),GREENBLACK)
		elif active == 3:
			borders[6].addstr(0,0,'█'*(w2),GREENBLACK)
			borders[1].addstr(0,w1+1,'█'*(w2+1),GREENBLACK)
			borders[3].addstr(junc[3][0]-1,0,'█'*(height-junc[3][0]-1),GREENBLACK)
			borders[4].addstr(junc[4][0]-1,0,'█'*(height-junc[4][0]-1),GREENBLACK)
	
	ETH = Ethereum()
	
	filename = sys.argv[1]
	asm,locs,vars = loadASMFromFile(filename)
	contract = ContractASM('CONTRACT',asm,locs,vars)
	
	asm_cur_ind = 3
	
	def drawASM():
		win = 2
		[windows[win].addstr(i,0,' '*(w1-1)) for i in range(30)]
		fn = filename + '  '
		toprow = '    ASM'+' '*(w1-7-len(fn))+fn
		windows[win].addstr(0,0,toprow,BLACKWHITE)
		
		# go from 0 to 26, selected at 13
		selectedpos = 13 # middle
		numfollowing = 14
		numblank = selectedpos - asm_cur_ind
		numblank = max(0, numblank)
		start_pos = numblank
		curr_pos = start_pos
		
		start_asm = max(0, asm_cur_ind - selectedpos)
		relevant_asm = asm[start_asm : asm_cur_ind + numfollowing]
		toprint = [(start_asm + i, relevant_asm[i]) for i in range(len(relevant_asm))]
		
		curr = 0
		end = min(27, len(toprint))
		while curr < end:
			if curr + numblank == selectedpos:
				color = BLACKGREEN
			else:
				color = WHITEBLACK
			try:
				ts = toprint[curr][1].hex()
			except:
				ts = toprint[curr][1]
			windows[win].addstr(numblank+curr+2,1,'%04x %s' % (toprint[curr][0],ts), color)
			curr += 1
			
			
	def drawStack():
		win = 1
		[windows[win].addstr(i,0,' '*(w2-1)) for i in range(19)]
		toprow = '    STACK'+' '*(w2-9)
		windows[win].addstr(0,0,toprow,BLACKWHITE)
		
		color = WHITEBLACK
		
		i = 0
		end = min(len(contract.stack),16)
		while i < end:
			windows[win].addstr(i+2,1,'%03x %s' % (-i-1,i2h(int(contract.stack[-i-1]))), color)
			i += 1
			
	storage_curr = None
	
	def drawStorage():
		win = 3
		[windows[win].addstr(i,0,' '*(w2-1)) for i in range(18)]
		toprow = '    STORAGE'+' '*(w2-11)
		windows[win].addstr(0,0,toprow,BLACKWHITE)
		
		color = WHITEBLACK
		
		i = 0
		end = min(len(contract.storage._storage),8)
		#while i < end:
		#	windows[win].addstr(i+2,1,'%s' % (-i-1,i2h(int(contract.st[-i-1]))), color)
		#	windows[win].addstr(i+2,1,'└── %s' % (-i-1,i2h(int(contract.stack[-i-1]))), color)
		#	i += 2
			
	def retest():
		contract.run(Transaction('CONTRACT',10**14,10**8,[],'alice'),Block(1,2**32,0x0,0,0),stopat=asm_cur_ind)
		
	
	pad.refresh(0,0, 0,0, height,width)
	while 1:
		retest()
		drawASM()
		drawStack()
		drawStorage()
		drawborders(active_win)
		
		stdscr.refresh()
		pad.refresh(0,0, 0,0, height,width)
		pressed = stdscr.getch()
		if pressed == curses.KEY_UP:
			asm_cur_ind = max(0, asm_cur_ind - 1)
		elif pressed == curses.KEY_DOWN:
			asm_cur_ind = min(len(asm)-1, asm_cur_ind + 1)
	
	
import curses
curses.wrapper(run)
try:
	curses.wrapper(run)
except curses.error as e:
	print 'Ensure console is minimum %d x %d' % (width, height)
	print e