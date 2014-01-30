# start_debug
from ethereum import *
from contract_functions import *
from copy import deepcopy

class MARKETCOIN(Contract):
	def run(self, tx, block):
		# variables for testing:
		minfee = 0
		
		# contract.blah is self-referential
		contract = self
		
		# end_debug
		
		# actual contract
		
		ALT = 0
		ETR = 1
		NEXT_ORDER = 2
		RATE = 3
		OUTPUT = 4
		EXACT_VAL = 5
		SENDER = 6
		FL = 7 # foreign or local - local can be escrowed, foreign cannot and requires a pledge
				# 0 = foreign, 1 = local, => FL = tx.data[TX_CURR]
		PLEDGE = 8

		TX_CURR = 0
		TX_MIN_RET = 1
		TX_REQ_OUT = 2
		TX_CHAIN_ENTRY = 3
		TX_MAX_CURR = 4

		OM_REQ_ALT_OUT = 0
		OM_SUCCESS_OUT = 1
		OM_FAIL_OUT = 2
		OM_TRADE_ALT_VAL = 3
		OM_TRADE_ETR_VAL = 4
		OM_PLEDGE = 5

		def calcorderid(ord):
			# this is arbitrary, but needs to be 1:1 and easily calculable.
			# it probably will change, and is just a conglomeration of everything for the moment.
			return SHA3(ord)
			
		def calcAltTxHash(tx):
			return sha256(tx)
			
		def getVarInt(scratchpad):	
			varint = scratchpad[:1]
			if varint <= 0xfc:
				scratchpad = scratchpad[1:]
				return varint
			elif varint == 0xfd:
				varint = scratchpad[:2]
			elif varint == 0xfe:
				varint = scratchpad[:4]
			elif varint == 0xff:
				varint = scratchpad[:8]
			scratchpad = scratchpad[len(varint) + 1:]
			return varint
			
		def dumpBytes(scratchpad, bytes):
			toret = scratchpad[:bytes]
			scratchpad = scratchpad[bytes:]
			return toret
			
		def evaluateMarket():
			# run market for previous round
			alt_top_hash = contract.storage[ALT]
			etr_top_hash = contract.storage[ETR]
			
			if alt_top_hash == 0 or etr_top_hash == 0:
				self.stop("One order queue empty")
			
			alt_ord = deepcopy(contract.storage[alt_top_hash])
			etr_ord = deepcopy(contract.storage[etr_top_hash])
			
			last_complete = 0
			have_traded = False
			
			ordermatch_list = []
			
			while alt_ord[RATE] <= etr_ord[RATE]:
				have_traded = True
				
				set_rate = (alt_ord[RATE] + etr_ord[RATE]) / 2
				trade_etr_val = min(alt_ord[ALT]/set_rate, etr_ord[ETR])
				etr_ord[ETR] -= trade_etr_val
				trade_alt_val = trade_etr_val * set_rate
				pledge_cut = trade_alt_val / alt_ord[ALT] * pledge_cut
				alt_ord[ALT] -= trade_alt_val
				
				req_alt_output = etr_ord[OUTPUT] # specified in etr order, for alt network
				success_output = alt_ord[OUTPUT] # specified in alt order, for etr network
				fail_output = etr_ord[SENDER] # return all to sender of etr if tx fails
				
				# ALTER THIS LINE TO ALTER ORDERMATCH SCHEMA
				# NOTE: Need to keep state variable to ensure multiple payout isn't possible.
				ordermatch = [req_alt_output, success_output, fail_output, trade_alt_val, trade_etr_val, pledge_cut, block.number]
				ordermatch_list.append(ordermatch)
				
				# check if any orders are completely full
				if alt_ord[ALT] == 0: # not doing `<=` so we can see when and why it breaks
					last_complete = ALT
					# if there are no more orders break
					if alt_ord[NEXT_ORDER] == 0:
						new_alt_top = 0
						break # end of orderbook
					to_del = new_alt_top
					new_alt_top = alt_ord[NEXT_ORDER]
					alt_ord = contract.storage[alt_ord[NEXT_ORDER]]
					del contract.storage[to_del]
					
				if etr_ord[ETR] == 0:
					last_complete = ETR
					if etr_ord[NEXT_ORDER] == 0:
						new_etr_top = 0
						break # End of orderbook
					todel = new_etr_top
					new_etr_top = etr_ord[NEXT_ORDER]
					etr_ord = contract.storage[etr_ord[NEXT_ORDER]]
					del new_etr_top
					
			# record ordermatch_list
			state = len(ordermatch_list)
			contract.storage[block.prevblock.hash] = state
			
			i = 0
			len_om = len(ordermatch_list)
			while i < len_om:
				contract.storage[block.prevblock.hash + i + 1] = ordermatch_list[i]
				i += 1;
				
			# calculate change order
			if last_complete == ALT:
				# create new trade and commit
				orderid = calcorderid(etr_ord)
				new_etr_top = orderid
				contract.storage[orderid] = etr_ord
			elif last_complete == ETR:
				orderid = calcorderid(alt_ord)
				new_alt_top = orderid
				contract.storage[orderid] = alt_ord
			
			contract.storage[ALT] = new_alt_top
			contract.storage[ETR] = new_etr_top

		if tx.fee < minfee:
			stop
		if tx.datan < 2:
			stop
			
			
		if tx.data[0] == ALT or tx.data[0] == ETR:	
			# check if first order for this block (state)
			# if so execute market
			# afterwards add to list of orders and orderbook
			
			state = contract.storage[block.prevblock.hash]
			if state == 0:
				evaluateMarket()
				# done with market - NO VARIABLES COMMON TO SECTION BELOW
			
			# back to submitting an order
			
			# order prep
			min_return = tx.data[TX_MIN_RET]
			req_output = tx.data[TX_REQ_OUT]
			pledge = tx.value
			fl = tx.data[TX_CURR] # foreign or local chain
			if tx.data[TX_CURR] == ETR:
				etr = tx.value
				alt = min_return
			else:
				alt = tx.data[TX_MAX_CURR]
				etr = min_return
			rate = alt / etr
			
			# check entry point is good
			prev_ord_hash = tx.data[TX_CHAIN_ENTRY]
			if prev_ord_hash != 0: # we are not at the start of the orderbook
				prev_ord = contract.storage[prev_ord_hash]
				# condition: ensure rate is no better than than prev_ord's.
				if not((tx.data[TX_CURR] == ALT and prev_ord[RATE] >= rate) or (tx.data[TX_CURR] == ETR and prev_ord[RATE] <= rate)):
					stop
				next_ord_hash = prev_ord[NEXT_ORDER]
			else:
				next_ord_hash = contract.storage[tx.data[TX_CURR]]
			if next_ord_hash != 0: # not at end of orderbook
				next_ord = contract.storage[next_ord_hash]
				# condition, make sure next order is worse than this offer ( this means you have added yourself to the end of the queue)
				if not ((tx.data[TX_CURR] == ALT and next_ord[RATE] < rate) or (tx.data[TX_CURR] == ETR and next_ord[RATE] > rate)):
					stop
					
				
			if tx.data[TX_CURR] == ALT:
				# validate pledge
				# Find the worst deal possible for the seller of ALT. Take the difference of the maxima and 
				# minima of the exchange rates over the last 24hrs (timeout period).
				# That magnitude is the pledge because it is the most the buyer could lose due to the seller's
				# incompetence or malice. Typically only a few percent. This is returned when they prove
				# payment.
				## TODO: need to gather stats from market
				## for now use 5%
				if pledge < tx.data[TX_MAX_CURR] / 20:
					stop
				
			# exact val is set to 0 currently. In the future it can designate a non-zero exact value to buy in ALT
			# this allows for cross chain payments but needs a little more work.
			this_ord = [alt, etr, next_ord_hash, rate, req_output, 0, tx.sender, fl, pledge]
			orderid = calcorderid(this_ord) # I am aware as the market evaluates this does not update if the 
												# order is updated. This is irrelevant; we just want a unique id
				
			# alter prev_ord to modify orderbook
			if prev_ord_hash != 0:
				prev_ord[NEXT_ORDER] = orderid
				contract.storage[prev_ord_hash] = prev_ord
			else:
				contract.storage[tx.data[TX_CURR]] = orderid
			
		elif tx.data[0] == 2:
			# proof of payment
			ordermatch_index = tx.data[1]
			alt_tx = tx.data[2]
			alt_tx_hash = calcAltTxHash(alt_tx)
			blockhash = tx.data[3]
			
			# get what the output should be
			ordermatch = contract.storage[ordermatch_index]
			expected_value = ordermatch[OM_TRADE_ALT_VAL]
			expected_out = ordermatch[OM_REQ_ALT_OUT]
			
			# verify output
			scratchpad = tx[4:] # ignore version
			numinputs = getVarInt(scratchpad)
			
			# loop through and drop inputs
			i = 0
			while i < numinputs:
				i += 1;
				scratchpad = scratchpad[36:] # drop prevtx and txout index
				script_len = getVarInt(scratchpad)
				scratchpad = scratchpad[script_len+4:] # drop script and sequence_no
			
			# loop through outputs
			numoutputs = getVarInt(scratchpad)
				
			i = 0
			verified_output = False
			while i < numoutputs:
				i += 1
				check_output = False
				value = dumpBytes(scratchpad, 8)
				if value == expected_value:
					check_output = True
				output_len = getVarInt(scratchpad)
				output = dumpBytes(scratchpad, output_len)
				if check_output == True:
					if output == expected_output:
						verified_output = True
						break
			
			if verified_output == False:
				stop
			
			# access SPV client and check tx exists
			if block.contract_storage(SPV,alt_tx_hash) == 0:
				stop
				
			# finally check block is part of main chain
			TB = 1
			HIST = 4
			topblock = block.contract_storage(CHAINHEADERS,TB)
			topblockdata = block.contract_storage(CHAINHEADERS, topblock)
			history = topblockdata[HIST]
				
			totalValue = ordermatch[OM_TRADE_ETR_VAL] + ordermatch[OM_PLEDGE]
				
			# release funds to buyer of ETR
			make_transaction(value, ordermatch[OM_SUCCESS_OUT], [])
			
		elif tx.data[0] == 3:
			# cancel order
			orderid = tx.data[1]
			prev_orderid = tx.data[2]
			
			# verify sender
			order = contract.storage[orderid]
			if tx.sender != order[SENDER]:
				stop
			
			# verify prev_order[NEXT_ORDER] points to orderid
			prev_order = contract.storage[prev_orderid]
			if prev_order[NEXT_ORDER] != orderid:
				stop
			
			# point prev_order to order[NEXT_ORDER]
			prev_order[NEXT_ORDER] = order[NEXT_ORDER]
			contract.storage[prev_orderid] = prev_order
			# done
			
		elif tx.data[0] == 4:
			# push pledge
			ordermatch_index = tx.data[1]
			ordermatch = contract.storage[ordermatch_index]
			included_in = ordermatch[OM_BLOCK_NUM]
			current = block.number
			if 60*24 + included_in > current:
				stop # current is before timeout
			
			# we can allow seller of ETR to claim pledge
			total_value = ordermatch[OM_PLEDGE] + ordermatch[OM_TRADE_ETR_VAL]
			make_transaction(total_value, ordermatch[OM_FAIL_OUT], [])
			
		else:
			stop