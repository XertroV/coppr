#!/usr/bin/python

''' Test CHAINHEADERS '''

from ethereum import *

asm_ch, locs = loadASMFromFile('asm/chainheaders.txt')
c_ch = ContractASM("CHAINHEADERS",asm_ch,locs)
b = Block(1,2**32,0x0,0,0)
from _test_CH_ASM_TX import *

ETH = Ethereum()
ETH.addBlock(b)
ETH.addContract(c_ch)
ETH.accounts['alice'] = 10**20
	
ch_results = testTransactions(ETH, transactions_chainheaders)

testResults(ch_results)

ETH.contracts['CHAINHEADERS'].printState()


