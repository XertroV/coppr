#!/usr/bin/python

''' Test CHAINHEADERS '''

from chainheaders import *
from ethereum import *
	
c_ch = CHAINHEADERS("CHAINHEADERS")
b = Block(1,2**32,0x0,0,0)
from _test_CH_TX import *

ETH = Ethereum()
ETH.addBlock(b)
ETH.addContract(c_ch)
ETH.accounts['alice'] = 10**20
	
ch_results = testTransactions(ETH, transactions_chainheaders)

testResults(ch_results)

#ETH.contracts['CHAINHEADERS'].printState()
