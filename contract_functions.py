#!/usr/bin/python

from ethereum import *

''' functions specifically used only in contracts
basically macros '''

def getversion(bh):
	return bh[:4]
def getparent(bh):
	return bh[4:4+32]
def getmerkleroot(bh):
	return bh[4+32:4+32+32]
def gettimestamp(bh):
	return bh[4+32+32:4+32+32+4]
def getnbits(bh):
	return bh[4+32+32+4:4+32+32+4+4]
def getnonce(bh):
	return bh[4+32+32+4+4:80]
def getblockhash(bh):
	return sha256(sha256(bh))
def nbitstotarget(nbits):
	return nbits[0:3][::-1] * (2 ** (8*(nbits[3]-3)))