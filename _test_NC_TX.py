#!/usr/bin/python
from ethereum import Transaction, EBN
transactions_namecoin = [
(True, Transaction('NAMECOIN',10**14,10**8,[EBN('xk.io'.encode('hex')),EBN('c6c7662b')],EBN('0a11ce'))),
# wrong sender, should fail
(False, Transaction('NAMECOIN',10**14,10**8,[EBN('xk.io'.encode('hex')),EBN('ffffffff')],EBN('0b0b'))),
(True, Transaction('NAMECOIN',10**14,10**8,[EBN('xk2.io'.encode('hex')),EBN('c6c7ffff')],EBN('0b0b'))),
]