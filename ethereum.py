#!/usr/bin/python


'''

ethereum.py provides basic classes and structures for contract testing.

This is not a substitute for the testnet, but should help increase the speed
of prototyping contracts.

To use, `from ethereum import *`

The following low level objects will become available:
EBN - an object that acts as either an int or a byte array depending on context.

TODO: EBN will be a representation of RLP in Ethereum. Arithmetic operations
cannot be done if there is a sublist involved. EG: [1,1] + 1 = ?. Unless meaning
can be found in that action it won't be implemented.

EBN does not yet support sublists.

'''

# EARLY IMPORTS


import pprint
pp = pprint.PrettyPrinter(indent=4)

import traceback, math
from termcolor import colored


# LOW LEVEL OBJECTS


class EBN:
	'''EBN = Ethereum Byte Number
	Special data structure where it acts as a number and a byte array.
	Slices like a byte array
	Adds and compares like a number
	Hashes like a byte array
	'''
	def __init__(self, initString='00', fromHex=True):
		if fromHex == True:
			'''input should be a string in hex encoding'''
			self.this = initString.decode('hex') # byte array
		else:
			self.this = initString
		
	def __lt__(self, other):
		return int(self) < int(other)
	def __gt__(self, other):
		return int(self) > int(other)
	def __eq__(self, other):
		if isinstance(other, str):
			return self.this == other
		return int(self) == int(other)
	def __ne__(self, other):
		return int(self) != int(other)
	def __le__(self, other):
		return int(self) <= int(other)
	def __ge__(self, other):
		return int(self) >= int(other)
	def __cmp__(self, other):
		return int(self) - int(other)
		
	def __len__(self):
		return len(self.this)
	def __getitem__(self,key):
		return EBN(self.this[key], fromHex=False)
	def __setitem__(self,key,value):
		self.this[key] = value
		
	# do I need to do the r___ corresponding functions? (__radd__ for example)
	def __add__(self, other):
		return EBN(i2h(int(self) + int(other) % 2**256))
	def __sub__(self, other):
		return EBN(i2h(int(self) - int(other) % 2**256))
	def __mul__(self, other):
		return EBN(i2h(int(self) * int(other) % 2**256))
	def __div__(self, other):
		return EBN(i2h(int(self) / int(other) % 2**256))
	def __mod__(self, other):
		return EBN(i2h(int(self) % int(other)))
	def __pow__(self, other):
		return EBN(i2h(int(self) ** int(other)))
	def __xor__(self, other):
		return EBN(xor_strings(self.this, other.this), False)
		
	def __str__(self):
		return self.this
	def __repr__(self):
		return self.hex()
	def __int__(self):
		return int(self.this.encode('hex'),16)
	def __float__(self):
		return float(self.__int__())
		
	def __hash__(self):
		return int(self.hex(), 16)
	
	def hex(self):
		return self.this.encode('hex')
	def to_JSON(self):
		return "\""+self.hex()+"\""
	def concat(self, other):
		return EBN(self.this + other.this, False)
	def raw(self):
		return self.this
	def str(self):
		return self.this
	
	
# HELPER FUNCTIONS


import hashlib
def sha256(message):
	# require EBN input at this stage
	return EBN(hashlib.sha256(str(message)).digest(), fromHex=False)

	
def xor_strings(xs, ys):
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(xs, ys))
	
def i2h(i):
	'''return int as shortest hex with an even number of digits as str'''
	h = format(i,'x')
	return '0'*(len(h)%2)+h

def testTransactions(ETH, lTx):
	''' takes a list of tuples: (bool, Transaction)
	First argument is if the test should fail or succeed (fail means running into an exception)
	Second argument is the Transaction() to load
	'''
	test_records = []
	for succeed, tx in lTx:
		print colored('TRANSACTION:','blue'), tx
		noex = True
		try:
			ETH.processTx(tx)
		except Exception as err:
			if succeed:
				print colored('BAD       ','grey','on_red')
			else:
				print colored('GOOD      ','grey','on_green')
			traceback.print_exc()
			noex = False
		test_records += [(succeed, noex)]
	return test_records
	
def testResults(lRes):
	''' print output of test results '''
	count = 1
	win = 0
	lose = 0
	for test in lRes:
		if test[0] == test[1]:
			print colored('Test %d passed' % count, 'green')
			win += 1
		else:
			print colored('Test %d failed!' % count, 'red')
			lose += 1
		count += 1
	print "Summary - Passed: %d, Failed: %d" % (win, lose)

	
	
def loadASMFromFile(asmFile):
	asm = []
	locations = {}
	with open(asmFile) as f:
		for line in f:
			l = line.strip()
			if l == '' or l[0] == '#':
				continue
			if l[0] == ':':
				locations[l[1:]] = len(asm)
				continue
			for op in l.split(' '):
				if op == '':
					continue
				try: 
					op = EBN(op)
				except: 
					pass
				asm.append(op)
	return asm, locations
	
	

# HIGH LEVEL OBJECTS



class Transaction:
	def __init__(self, receiver, value, fee, data, sender):
		self.receiver = receiver
		self.sender = sender
		self.value = value
		self.fee = fee
		self.data = data
		self.datan = len(data)
		
	def __str__(self):
		return '%s,%s,%s,%s' % (self.receiver, self.value, self.fee, self.data)

class Block:
	def __init__(self, number, difficulty, parenthash, basefee, timestamp):
		self.number = number
		self.difficulty = difficulty
		self.parenthash = parenthash
		self.basefee = basefee
		self.timestamp = timestamp
		self.eth = None
		self.transactions = []
		
	def setNetwork(self, eth):
		self.eth = eth
		
	def contract_storage(self, D):
		# D = name of contract (hash)
		return self.eth.contract_storage(D)
		
	def account_balance(self, a):
		return self.eth.account_balance(a)
		
	def addTx(self, tx):
		if not tx.isValid() or tx in self.transactions:
			return False
		self.transactions.append(tx)
		
class Ethereum:
	def __init__(self):
		self.contracts = {}
		self.accounts = {}
		self.blocks = []
		self.latestBlock = None
		
	def processTx(self, tx):
		self.addAccount(tx.sender)
		if self.accounts[tx.sender] < (tx.value + tx.fee):
			print "WARNING: -'ve balance %s" % tx.sender
		self.accounts[tx.sender] -= (tx.value + tx.fee)
		if tx.receiver not in self.accounts:
			self.accounts[tx.receiver] = 0.0
		self.accounts[tx.receiver] += tx.value
		if tx.receiver in self.contracts:
			self.contracts[tx.receiver].run(tx, self.latestBlock)
		
	def addContract(self, contract):
		self.contracts[contract.name] = contract
		self.accounts[contract.name] = 0.0
		
	def addBlock(self, block):
		'''Presume block is correct, add to end of chain'''
		self.blocks.append(block)
		self.latestBlock = self.blocks[-1]
		for tx in self.latestBlock.transactions:
			self.processTx(tx)
		self.latestBlock.setNetwork(self)
	
	def addAccount(self, sender):
		if sender not in self.accounts:
			self.accounts[sender] = 0.0
	
	def contract_storage(self, D):
		# D : name of contract (hash)
		return self.contracts[D].storage

class ContractStorage:
	def __init__(self):
		# storage is technically not a dictionary but an array
		# A dictionary is used here for simplicity
		self._storage = {}
	def __getitem__(self,key):
		#if type(key) is not int:
		#	key = int(key)
		try:
			return self._storage[key]
		except:
			return 0
	def __setitem__(self, key, val):
		#if type(key) is not int:
		#	key = int(key)
		self._storage[key] = val
	def slice(self, start, end):
		# start inclusive, end exclusive
		ret = []
		while start < end:
			ret.append(self._storage[start])
			start += 1
		return ret
	def printState(self):
		pp.pprint(self._storage)
		
class Contract:
	def __init__(self, name):
		self.name = name
		self.storage = ContractStorage()
		self.address = name
		
	def stop(self, message=''):
		print colored('# Contract Stopped - %s' % message,'red')
		raise Exception("# Contract Stopped - %s" % message)
		
	def run(self, tx, latestBlock):
		'''This should be overwritten when the class is inherited'''
		raise Exception("Contract not initialized correctly.")
		
	def printState(self):
		pp.pprint(self.storage._storage)
		
class ContractASM(Contract):
	def __init__(self, name, asm, locs):
		Contract.__init__(self,name)
		self.asm = asm
		self.locs = locs
	def run(self, tx, block):
		contract = self
		memory = ContractStorage()
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
			print ind.hex(), op
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
				print x
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
				topush = asm[int(ind+1)]
				if topush == 'loc:end':
					self.stack.append(EBN() + (len(asm)-1))
				elif topush[:4] == 'loc:':
					self.stack.append(EBN() + self.locs[topush[4:]])
				else:
					self.stack.append(topush)
				ind += 2
				print self.stack
				continue
			elif op == 'POP':
				pass
			elif op == 'DUP':
				s = stack_pop(1)
				self.stack.extend([s[-1],s[-1]])
			elif op == 'SWAP':
				s = stack_pop(2)
				self.stack.extend([s[-1],s[-2]])
			elif op == 'MLOAD':
				s = stack_pop(1)
				self.stack.append(memory[s[-1]])
			elif op == 'MSTORE':
				s = stack_pop(2)
				memory[s[-1]] = s[-2]
			elif op == 'SLOAD':
				s = stack_pop(1)
				self.stack.append(self.storage[s[-1]])
			elif op == 'SSTORE':
				s = stack_pop(2)
				self.storage[s[-1]] = s[-2]
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
			print self.stack
			ind += 1
	





