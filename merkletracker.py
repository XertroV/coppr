# start_debug
from ethereum import *
from copy import deepcopy

class MERKLETRACKER(Contract):
	def run(self, tx, block):
		# variables for testing:
		minfee = 0
		
		# contract.blah is self-referential
		contract = self
		
		# end_debug
		
		# actual contract
		if tx.datan < 3:
			self.stop
		if tx.fee < minfee:
			stop
			
		def getmerkleroot(blockheader):
			return blockheader[4+32:4+32+32]

		if tx.data[0] == 0:
			# add a merkle root
			merkleroot = tx.data[1]
			blockhash = tx.data[2]
			blockheader = block.contract_storage('CHAINHEADERS')[blockhash][0]
			print merkleroot.hex(), getmerkleroot(blockheader).hex()
			if merkleroot == getmerkleroot(blockheader):
				# success!
				contract.storage[merkleroot] = 1
				print contract.storage._storage

		elif tx.data[0] == 1:
			# fill in merkle branch
			hash1 = tx.data[1]
			hash2 = tx.data[2]
			# first verify branch leads to existing entry
			counter = 2;
			while True: 
				counter += 1
				hash3 = sha256(sha256(hash1.concat(hash2)))
				print hash3.hex()
				if tx.datan > counter:
					lr = tx.data[counter][0]
					hash4 = tx.data[counter][1:33]
				else:
					pre = contract.storage[hash3]
					if pre == 1:
						# found merkle root
						merkleroot = hash3
						break
					elif pre == 0:
						# failed, not enough user input to confirm branch
						self.stop('Incomplete or invalid merkle branch')
					merkleroot = pre[2]
					break
				if lr == 0:
					hash1 = hash3
					hash2 = hash4
				else:
					hash1 = hash4
					hash2 = hash3
			
			# sweet, everything is valid so far, lets make some entries!
			hash1 = tx.data[1]
			hash2 = tx.data[2]
			counter = 2;
			while contract.storage[hash1] == 0:
				contract.storage[hash1] = [0x00, hash2, merkleroot]
				contract.storage[hash2] = [0x01, hash1, merkleroot]
				counter += 1
				hash3 = sha256(hash1.concat(hash2))
				if tx.datan > counter:
					lr = tx.data[counter][0]
					hash4 = tx.data[counter][1:33]
				else:
					break
				if lr == 0:
					hash1 = hash3
					hash2 = hash4
				else:
					hash1 = hash4
					hash2 = hash3
			
			# should be done, I think