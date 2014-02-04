#!/usr/bin/python

from ethereum import EBN, Block, Transaction, loadASMFromString, i2h, ContractStorage
import sys


def pop(stack, n): 
	if len(stack) < n:
		sys.stderr.write("Stack height insufficient, exiting")
		exit = True
		return [0] * n
	o = [stack.pop() for i in range(n)][::-1]
	return o


def runASM(asm, stack, block=Block(1,2**32,0x0,0,0), tx=Transaction('CHAINHEADERS',10**14,10**8,[],'alice')):
	opcount = 0
	asm2 = {}
	for n,ops in asm.iteritems():
		asm2[n] = loadASMFromString(ops)
	asm = asm2
	cstorage = ContractStorage()
	cstack = [['START',0]]
	
	# much of the following is borrowed from pyethereum/processblock.py
	
	while 1:
		if len(cstack) == 0:
			sys.stderr.write("Execution Finished\n")
			break
		print stack, cstack
		cblk = cstack[-1][0]
		ind = cstack[-1][1]
		try:
			op = asm[cblk][ind]
			opcount += 1
		except IndexError:
			op = 'NULL'
		print cblk, ind, op
		if op == 'STOP': break
		if op == 'NULL':
			cstack.pop()
			continue
		elif op == 'ADD':
			s = pop(stack, 2)
			stack.append(s[-2]+s[-1])
		elif op == 'SUB':
			s = pop(stack, 2)
			stack.append(s[-2]-s[-1])
		elif op == 'MUL':
			s = pop(stack, 2)
			stack.append(s[-2]*s[-1])
		elif op == 'DIV':
			s = pop(stack, 2)
			stack.append(s[-2]/s[-1])
		elif op == 'SDIV':
			s = pop(stack, 2)
			sign = (1 if s[-1] < 2**255 else -1) * (1 if s[-2] < 2**255 else -1)
			x = s[-2] if s[-2] < 2*255 else 2*256 - s[-2]
			y = s[-1] if s[-1] < 2*255 else 2*256 - s[-1]
			z = int(x/y)
			stack.append(z if sign == 1 else 2**256 - z)
		elif op == 'MOD':
			s = pop(stack, 2)
			stack.append(s[-2]%s[-1])
		elif op == 'SMOD':
			x,y = pop(stack, 2)
			sign = (1 if x < 2**255 else -1) * (1 if y < 2**255 else -1)
			xx = x if x < 2**255 else 2**256 - x
			yy = y if y < 2**255 else 2**256 - y
			z = xx%yy
			stack.append(z if sign == 1 else 2**256 - z)
		elif op == 'EXP':
			x,y = pop(stack, 2)
			stack.append(pow(x,y))
		elif op == 'NEG':
			stack.append(2**256 - pop(stack, 1)[0])
		elif op == 'LT':
			x,y = pop(stack, 2)
			stack.append(1 if x < y else 0)
		elif op == 'LE':
			x,y = pop(stack, 2)
			stack.append(1 if x <= y else 0)
		elif op == 'GT':
			x,y = pop(stack, 2)
			stack.append(1 if x > y else 0)
		elif op == 'GE':
			x,y = pop(stack, 2)
			stack.append(1 if x >= y else 0)
		elif op == 'EQ':
			x,y = pop(stack, 2)
			stack.append(1 if x == y else 0)
		elif op == 'NOT':
			x = pop(stack, 1)
			res = int(x[0] == 0)
			stack.append(res)
		elif op == 'MYADDRESS':
			stack.append(EBN('12345678901234567890'))
		elif op == 'TXSENDER':
			stack.append(tx.sender)
		elif op == 'TXVALUE':
			stack.append(tx.value)
		elif op == 'TXDATAN':
			stack.append(tx.datan)
		elif op == 'TXDATA':
			s = pop(stack, 1)
			stack.append(tx.data[int(s[-1])])
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
			stack.append(block.basefee)
		elif op == 'SHA256':
			s = pop(stack, 2)
			itemstotake = math.ceil(float(s[-1]) / 32.0)
			items = memory.slice(s[-2],s[-2]+itemstotake)
			tohash = EBN('')
			for item in items:
				tohash = tohash.concat(item)
			stack.append(sha256(tohash))
		elif op == 'PUSH':
			topush = asm[cblk][ind+1]
			if topush == 'loc:end':
				stack.append(EBN() + (len(asm)-1))
			elif topush[:4] == 'loc:':
				stack.append(EBN() + self.locs[topush[4:]])
			elif topush[:4] == 'var:':
				stack.append(self.vars[topush[4:]])
			else:
				stack.append(topush)
			ind += 1
		elif op == 'POP':
			pop(stack, 1)
		elif op == 'DUP':
			s = pop(stack, 1)
			stack.extend([s[-1],s[-1]])
		elif op == 'DUPN':
			todup = int(asm[cblk][ind+1])
			stack.append(stack[-todup])
			ind += 1
		elif op == 'SWAP':
			s = pop(stack, 2)
			stack.extend([s[-1],s[-2]])
		elif op == 'SWAPN':
			n = int(asm[cblk][ind+1])
			s1 = stack[-1]
			stack[-1] = stack[-n]
			stack[-n] = s1
		elif op == 'SLOAD':
			s = pop(stack, 1)
			stack.append(cstorage[s[-1]])
		elif op == 'SSTORE':
			s = pop(stack, 2)
			cstorage[s[-1]] = s[-2]
		elif op == 'IND':
			stack.append(EBN(i2h(ind)))
		elif op == 'EXTRO':
			pass
		elif op == 'BALANCE':
			pass
		elif op == 'MKTX':
			pass
		elif op == 'SUICIDE':
			pass
		elif op == 'FAIL':
			raise Exception("FAIL called")
		elif op == 'REVBYTES':
			s = pop(stack, 1)
			stack.append(s[-1][::-1])
		elif op == 'RUN':
			torun = asm[cblk][ind+1]
			cstack[-1][1] += 2
			cstack.append([torun,0])
			continue
		elif op == 'IF':
			print stack
			s = pop(stack, 1)
			print stack
			t = asm[cblk][ind+1]
			f = asm[cblk][ind+2]
			if s[-1] == EBN('00'):
				tr = f
			else:
				tr = t
			cstack[-1][1] += 3
			cstack.append([tr,0])
			continue
			
		ind += 1
		cstack[-1][1] = ind
	print stack, cstack
	print opcount, 'operations'