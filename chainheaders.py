# start_debug
from ethereum import *
from copy import deepcopy

class CHAINHEADERS(Contract):
	def run(self, tx, block):
		# variables for testing:
		requiredfee = 0
		
		# contract.blah is self-referential
		contract = self
		
		# end_debug
		
		# actual contract
		if tx.fee < requiredfee:
			self.stop()

		# special locations in memory:
		# mc-1  : state
		# mc    : [blockindexcount, topblock, topdiff, topheight]
		BIC = 0
		TB = 1
		TD = 2
		TH = 3
		# datastruct for blocks:
		# c.m[hash] = [blockheader, index, height, cumulative diff, history]
		BH = 0
		IDX = 1
		HGT = 2
		CD = 3
		HIST = 4
		# c.m[mc+index] = hash

		# other variables
		DIFFONETARGET = EBN("00000000FFFF0000000000000000000000000000000000000000000000000000")
			
		blockheader = tx.data[BH]
		mc = magicconstant = 2 ** 4 # really, anywhere will do.
		
		state = contract.storage[mc-1]
		if state == 0:
			i = 1
			contract.storage[mc] = [1, EBN("6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000"), 1, 1]
			contract.storage[mc+i] = EBN("6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000")
			# indexes cannot be EBNs (but int(EBN) is okay
			# cheating here for readability
			contract.storage[EBN("6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000")] = [EBN("0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"), 1, 0, 1, [EBN("6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000")]]
			
			contract.storage[mc-1] = 1
			
		# blockheader should be 80 bytes long
		if len(blockheader) != 80:
			self.stop()

		def getversion(bh):
			return bh[:4]
		def getparent(bh):
			return bh[4:4+32]
		def getmerkleroot(bh):
			return bh[4+32:4+32+32]
		def gettimestamp(bh):
			return bh[4+32+32:4+32+32+4]
		def getnbits(bh):
			return bh[4+32+32+4:4+32+32+4+4]
		def getnonce(bh):
			return bh[4+32+32+4+4:80]
		def getblockhash(bh):
			return sha256(sha256(bh))
		def nbitstotarget(nbits):
			return nbits[0:3][::-1] * (2 ** (8*(nbits[3]-3)))
			
		blockhash = getblockhash(blockheader)
		blockparent = getparent(blockheader)
		blockmerkleroot = getmerkleroot(blockheader)
		blocktimestamp = gettimestamp(blockheader)
		blocknbits = getnbits(blockheader)
		metadata = contract.storage[mc]
		blockindexcount = metadata[BIC]
		topblock = metadata[TB]
		topdiff = metadata[TD]

		# check we don't have it but do have parent
		parentdata = contract.storage[blockparent]
		if parentdata == 0:
			self.stop() # parent not in chain so fail
		blockdata = contract.storage[blockhash]
		if blockdata != 0:
			stop # block already known about

		# check difficulty
		target = nbitstotarget(blocknbits)
		if blockhash[::-1] >= target:
			self.stop()
		diff = DIFFONETARGET * 1.0 / target

		# check checkpoints - maybe
		# do this at some point

		# add to collection
		parentdata = contract.storage[blockparent]
		prevdiff = parentdata[CD]
		prevheight = parentdata[HGT]
		blockindexcount += 1
		metadata[BIC] = blockindexcount
		contract.storage[mc] = metadata
		contract.storage[mc+blockindexcount] = blockhash
		newdiff = diff + prevdiff
		newheight = prevheight + 1

		# incremental merkle trees
		history = deepcopy(parentdata[HIST])
		history.append(blockhash)
		j = 2
		while blockindexcount % j == 0:
			history = history[:-2] + [sha256(history[-2].concat(history[-1]))]
			j = j * 2

		blockdata = [blockheader, blockindexcount, newheight, newdiff, history]
		contract.storage[blockhash] = blockdata
		if newdiff > topdiff:
			# we have a new topblock
			metadata[TB] = blockhash
			metadata[TD] = newdiff
			metadata[TH] = newheight
			contract.storage[mc] = metadata