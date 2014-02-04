#!/usr/bin/python

from asm import *

stack = [
	EBN("79")
]

asm = {
	'LENBITS1':'''
		DUP PUSH 00 EQ IF NULL LENBITS2
	''',
	# take an int less than 256 and count the number of bits
	'LENBITS2':'''
		PUSH 02 PUSH 08 PUSH 02 PUSH 08 RUN LENBITS3 PUSH 01 ADD
	''',
	'LENBITS3':'''
		EXP DUPN 04 GT IF LENBITS4 NULL
	''',
	'LENBITS4':'''
		PUSH 01 SUB DUPN 02 DUPN 02 RUN LENBITS3
	''',
	'LENBITSSMALL':'''
		DUP PUSH 80 
	''',
	'FINISHLENBITSSMALL':'''
		
	''',
	'TRUE':'''
		PUSH 01
	''',
	'FALSE':'''
		PUSH 00
	''',
	
	'START':'''
	RUN LENBITS1
	''',
	'NULL':''''''
}

runASM(asm, stack)