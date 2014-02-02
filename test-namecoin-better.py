#!/usr/bin/python

''' Test NAMECOIN-BETTER '''

from ethereum import *
	
asm_nc = loadASMFromFile('asm/namecoin-better.txt')
c_nc_wp = ContractASM('NAMECOIN',asm_nc)
b = Block(1,2**32,0x0,0,0)
from _test_NC_TX import *

ETH = Ethereum()
ETH.addBlock(b)
ETH.addContract(c_nc_wp)
ETH.accounts['alice'] = 10**20
	
nc_results = testTransactions(ETH, transactions_namecoin)

testResults(nc_results)

ETH.contracts['NAMECOIN'].printState()
