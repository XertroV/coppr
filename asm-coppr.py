#!/usr/bin/python

import sys, math, hashlib
from ethereum import *

contractstorage = ContractStorage()
memory = ContractStorage()

asm = []
stack = []

myaddress = 0xADD35501*1000000
txsender = 0xADD355FF*1000000
txdata = [0x786b2e696f,0xc6c7662b]
txdatan = len(txdata)
basefee = 1000
txvalue = 1000*basefee

opcodes = ['STOP', 'ADD', 'SUB', 'MUL', 'DIV', 'SDIV', 'MOD', 'SMOD', 'EXP', 'NEG', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NOT', 'MYADDRESS', 'TXSENDER', 'TXVALUE', 'TXDATAN', 'TXDATA', 'BLK_PREVHASH', 'BLK_COINBASE', 'BLK_TIMESTAMP', 'BLK_NUMBER', 'BLK_DIFFICULTY', 'BASEFEE', 'SHA256', 'RIPEMD160', 'ECMUL', 'ECADD', 'ECSIGN', 'ECRECOVER', 'ECVALID', 'SHA3', 'PUSH', 'POP', 'DUP', 'SWAP', 'MLOAD', 'MSTORE', 'SLOAD', 'SSTORE', 'JMP', 'JMPI', 'IND', 'EXTRO', 'BALANCE', 'MKTX', 'SUICIDE']

with open(sys.argv[1]) as f:
	for line in f:
		l = line.strip()
		for op in l.split(' '):
			if op == '':
				continue
			try:
				op = int(op)
			except:
				pass
			asm.append(op)
print 'ASM', asm

# borrowed from pyethereum/processblock.py
def stack_pop(n):
	global stack
	if len(stack) < n:
		sys.stderr.write("Stack height insufficient, exiting")
		exit = True
		return [0] * n
	o = stack[-n:]
	stack = stack[:-n]
	return o
	
def stack_push(*args):
	for a in args:
		stack.append(a)

ind = 0
while 1:
	op = asm[ind]
	print ind, op
	if op == 'STOP': break
	elif op == 'ADD':
		s = stack_pop(2)
		stack_push(s[-2]+s[-1])
	elif op == 'SUB':
		s = stack_pop(2)
		stack_push(s[-2]-s[-1])
	elif op == 'MUL':
		s = stack_pop(2)
		stack_push(s[-2]*s[-1])
	elif op == 'DIV':
		s = stack_pop(2)
		stack_push(int(s[-2]/s[-1]))
	elif op == 'SDIV':
		s = stack_pop(2)
		sign = (1 if s[-1] < 2**255 else -1) * (1 if s[-2] < 2**255 else -1)
		x = s[-2] if s[-2] < 2*255 else 2*256 - s[-2]
		y = s[-1] if s[-1] < 2*255 else 2*256 - s[-1]
		z = int(x/y)
		stack_push(z if sign == 1 else 2**256 - z)
	elif op == 'MOD':
		s = stack_pop(2)
		stack.append(s[-2]%s[-1])
	elif op == 'SMOD':
		x,y = stack_pop(2)
		sign = (1 if x < 2**255 else -1) * (1 if y < 2**255 else -1)
		xx = x if x < 2**255 else 2**256 - x
		yy = y if y < 2**255 else 2**256 - y
		z = xx%yy
		stack.append(z if sign == 1 else 2**256 - z)
	elif op == 'EXP':
		x,y = stack_pop(2)
		stack.append(pow(x,y,2**256))
	elif op == 'NEG':
		stack.append(2**256 - stack.pop(1)[0])
	elif op == 'LT':
		x,y = stack_pop(2)
		stack.append(1 if x < y else 0)
	elif op == 'LE':
		x,y = stack_pop(2)
		stack.append(1 if x <= y else 0)
	elif op == 'GT':
		x,y = stack_pop(2)
		stack.append(1 if x > y else 0)
	elif op == 'GE':
		x,y = stack_pop(2)
		stack.append(1 if x >= y else 0)
	elif op == 'EQ':
		x,y = stack_pop(2)
		stack.append(1 if x == y else 0)
	elif op == 'NOT':
		stack.append(1 if stack.pop(1)[0] == 0 else 0)
	elif op == 'MYADDRESS':
		stack.append(myaddress)
	elif op == 'TXSENDER':
		stack.append(txsender)
	elif op == 'TXVALUE':
		stack.append(txvalue)
	elif op == 'TXDATAN':
		stack.append(txdatan)
	elif op == 'TXDATA':
		s = stack_pop(1)
		stack.append(txdata[s[-1]])
	elif op == 'BLK_PREVHASH':
		pass
	elif op == 'BLK_COINBASE':
		pass
	elif op == 'BLK_TIMESTAMP':
		pass
	elif op == 'BLK_NUMBER':
		pass
	elif op == 'BLK_DIFFICULTY':
		pass
	elif op == 'BASEFEE':
		stack.append(basefee)
	elif op == 'SHA256':
		s = stack_pop(2)
		itemstotake = int(math.ceil(s[-1] / 32.0))
		# only supports 1 item atm
		items = [memory[s[-2]]]
		tohash = ''.join([format(i,'x') for i in items])
		tohash = '0'*(len(tohash)%2) + tohash
		tohash = tohash.decode('hex')
		stack.append(int(hashlib.sha256(tohash).digest().encode('hex'),16))
	elif op == 'RIPEMD160':
		pass
	elif op == 'ECMUL':
		pass
	elif op == 'ECADD':
		pass
	elif op == 'ECSIGN':
		pass
	elif op == 'ECRECOVER':
		pass
	elif op == 'ECVALID':
		pass
	elif op == 'SHA3':
		pass
	elif op == 'PUSH':
		topush = asm[ind+1]
		if topush == 'loc:end':
			stack.append(len(asm)-1)
		else:
			stack.append(topush)
		ind += 2
		print stack
		continue
	elif op == 'POP':
		pass
	elif op == 'DUP':
		s = stack_pop(1)
		stack.extend([s[-1],s[-1]])
	elif op == 'SWAP':
		s = stack_pop(2)
		stack.extend([s[-1],s[-2]])
	elif op == 'MLOAD':
		s = stack_pop(1)
		stack.append(memory[s[-1]])
	elif op == 'MSTORE':
		s = stack_pop(2)
		memory[s[-1]] = s[-2]
	elif op == 'SLOAD':
		s = stack_pop(1)
		stack.append(contractstorage[s[-1]])
	elif op == 'SSTORE':
		s = stack_pop(2)
		contractstorage[s[-1]] = s[-2]
	elif op == 'JMP':
		s = stack_pop(1)
		ind = s[-1]
		continue
	elif op == 'JMPI':
		s = stack_pop(2)
		if s[-1] != 0:
			ind = s[-2]
			continue
	elif op == 'IND':
		stack.append(ind)
	elif op == 'EXTRO':
		pass
	elif op == 'BALANCE':
		pass
	elif op == 'MKTX':
		pass
	elif op == 'SUICIDE':
		pass

	print stack
	ind += 1
print 'Stopped'
contractstorage.printState()