from ethereum import Transaction, EBN
'''
1. Test coinbase from block 546
2. Test above, bad coinbase
3. Test above, bad block
4. Nonsense

'''
transactions_spv = [
	(True, Transaction('SPV',10**14,10**8,[EBN("703bb9ec7ab4f56d9e417a53ac19cef9c53513dc0352b9734e012d799ffe80e9"),EBN("e64ac3beec275a3edc5a0dfe11b51014b7afefce067e661e78ed4d5a00000000")],'alice')),
	(False, Transaction('SPV',10**14,10**8,[EBN("703bb8ec7ab4f56d9e417a53ac19cef9c53513dc0352b9734e012d799ffe80e9"),EBN("e64ac3beec275a3edc5a0dfe11b51014b7afefce067e661e78ed4d5a00000000")],'alice')),
	(False, Transaction('SPV',10**14,10**8,[EBN("703bb9ec7ab4f56d9e417a53ac19cef9c53513dc0352b9734e012d799ffe80e9"),EBN("e64ac3beec275a3edc6a0dfe11b51014b7afefce067e661e78ed4d5a00000000")],'alice')),
	(False, Transaction('SPV',10**14,10**8,[EBN("77"),EBN("88")],'alice')),
]