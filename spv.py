# start_debug
from ethereum import *
from contract_functions import *
from copy import deepcopy

class SPV(Contract):
	def run(self, tx, block):
		# variables for testing:
		minfee = 0
		
		# contract.blah is self-referential
		contract = self
		
		# end_debug
		
		# actual contract
		if tx.fee < minfee:
			self.stop("fee too low")
		if tx.datan != 2:
			self.stop("datan != 2, wrong number of data bits")

		txhash = tx.data[0]
		blockhash = tx.data[1]

		# use merkletracker to get merkle root of txhash
		merkleroottxdata = block.contract_storage("MERKLETRACKER")[txhash]
		if merkleroottxdata == 0:
			self.stop("tx hash not found in MERKLETRACKER")
		print merkleroottxdata
		merkleroottx = merkleroottxdata[2]
		# use chainheaders to get merkle root of block
		bh = block.contract_storage("CHAINHEADERS")[blockhash]
		if bh == 0:
			self.stop("blockhash not found in MERKLETRACKER")
		merklerootbh = getmerkleroot(bh[0])
		if merklerootbh != merkleroottx:
			self.stop("incorrect merkle root provided")
			
		# confirmed tx is in merkle root and merkle root in block
		contract.storage[EBN(txhash ^ blockhash, False)] = 1