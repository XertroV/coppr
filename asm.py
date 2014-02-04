#!/usr/bin/python

from ethereum import EBN, Block

def runASM(self, asm, stack, stopat=EBN("ffffffff"), block=Block(1,2**32,0x0,0,0), tx=Transaction('CHAINHEADERS',10**14,10**8,[],'alice')):
	cstorage = ContractStorage()
	self.stack = []
	asm = self.asm
	# much of the following is borrowed from pyethereum/processblock.py
	def stack_pop(n):
		if len(self.stack) < n:
			sys.stderr.write("Stack height insufficient, exiting")
			exit = True
			return [0] * n
		o = self.stack[-n:]
		self.stack = self.stack[:-n]
		return o
	
	ind = EBN("00")
	while 1:
		op = asm[int(ind)]
		if ind > stopat:
			break
		if op == 'STOP': break
		elif op == 'ADD':
			s = stack_pop(2)
			self.stack.append(s[-2]+s[-1])
		elif op == 'SUB':
			s = stack_pop(2)
			self.stack.append(s[-2]-s[-1])
		elif op == 'MUL':
			s = stack_pop(2)
			self.stack.append(s[-2]*s[-1])
		elif op == 'DIV':
			s = stack_pop(2)
			self.stack.append(s[-2]/s[-1])
		elif op == 'SDIV':
			s = stack_pop(2)
			sign = (1 if s[-1] < 2**255 else -1) * (1 if s[-2] < 2**255 else -1)
			x = s[-2] if s[-2] < 2*255 else 2*256 - s[-2]
			y = s[-1] if s[-1] < 2*255 else 2*256 - s[-1]
			z = int(x/y)
			self.stack.append(z if sign == 1 else 2**256 - z)
		elif op == 'MOD':
			s = stack_pop(2)
			self.stack.append(s[-2]%s[-1])
		elif op == 'SMOD':
			x,y = stack_pop(2)
			sign = (1 if x < 2**255 else -1) * (1 if y < 2**255 else -1)
			xx = x if x < 2**255 else 2**256 - x
			yy = y if y < 2**255 else 2**256 - y
			z = xx%yy
			self.stack.append(z if sign == 1 else 2**256 - z)
		elif op == 'EXP':
			x,y = stack_pop(2)
			self.stack.append(pow(x,y))
		elif op == 'NEG':
			self.stack.append(2**256 - stack_pop(1)[0])
		elif op == 'LT':
			x,y = stack_pop(2)
			self.stack.append(1 if x < y else 0)
		elif op == 'LE':
			x,y = stack_pop(2)
			self.stack.append(1 if x <= y else 0)
		elif op == 'GT':
			x,y = stack_pop(2)
			self.stack.append(1 if x > y else 0)
		elif op == 'GE':
			x,y = stack_pop(2)
			self.stack.append(1 if x >= y else 0)
		elif op == 'EQ':
			x,y = stack_pop(2)
			self.stack.append(1 if x == y else 0)
		elif op == 'NOT':
			x = stack_pop(1)
			res = int(x[0] == 0)
			self.stack.append(res)
		elif op == 'MYADDRESS':
			self.stack.append(contract.address)
		elif op == 'TXSENDER':
			self.stack.append(tx.sender)
		elif op == 'TXVALUE':
			self.stack.append(tx.value)
		elif op == 'TXDATAN':
			self.stack.append(tx.datan)
		elif op == 'TXDATA':
			s = stack_pop(1)
			self.stack.append(tx.data[int(s[-1])])
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
			self.stack.append(block.basefee)
		elif op == 'SHA256':
			s = stack_pop(2)
			itemstotake = math.ceil(float(s[-1]) / 32.0)
			items = memory.slice(s[-2],s[-2]+itemstotake)
			tohash = EBN('')
			for item in items:
				tohash = tohash.concat(item)
			self.stack.append(sha256(tohash))
		elif op == 'PUSH':
			topush = asm[int(ind+1)]
			if topush == 'loc:end':
				self.stack.append(EBN() + (len(asm)-1))
			elif topush[:4] == 'loc:':
				self.stack.append(EBN() + self.locs[topush[4:]])
			elif topush[:4] == 'var:':
				self.stack.append(self.vars[topush[4:]])
			else:
				self.stack.append(topush)
			ind += 1
		elif op == 'POP':
			pass
		elif op == 'DUP':
			s = stack_pop(1)
			self.stack.extend([s[-1],s[-1]])
		elif op == 'DUPN':
			todup = int(asm[int(ind+1)])
			stack.append(stack[-todup])
			ind += 1
		elif op == 'SWAP':
			s = stack_pop(2)
			self.stack.extend([s[-1],s[-2]])
		elif op == 'SWAPN':
			n, = stack_pop(1)
			s1 = stack[-1]
			stack[-1] = stack[-n]
			stack[-n] = s1
		elif op == 'SLOAD':
			s = stack_pop(1)
			self.stack.append(cstorage[s[-1]])
		elif op == 'SSTORE':
			s = stack_pop(2)
			cstorage[s[-1]] = s[-2]
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
			self.stack.append(ind)
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
			s = stack_pop(1)
			self.stack.append(s[-1][::-1])
		print self.stack
		ind += 1