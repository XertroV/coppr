#!/usr/bin/python

''' Test CHAINHEADERS '''

from chainheaders import *
from merkletracker import *
from ethereum import *
	
c_ch = CHAINHEADERS("CHAINHEADERS")
c_mt = MERKLETRACKER("MERKLETRACKER")
b = Block(1,2**32,0x0,0,0)
from _test_CH_TX import *
from _test_MT_TX import *

ETH = Ethereum()
ETH.addBlock(b)
ETH.addContract(c_ch)
ETH.addContract(c_mt)
ETH.accounts['alice'] = 10**20
	
testTransactions(ETH, transactions_chainheaders)
mt_results = testTransactions(ETH, transactions_merkletracker)

testResults(mt_results)

#ETH.contracts['CHAINHEADERS'].printState()
#ETH.contracts['MERKLETRACKER'].printState()
