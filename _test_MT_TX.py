from ethereum import Transaction, EBN
'''
Tests
1. Load merkle root for block 170 - first non-coinbase tx on bitcoin network
2. add both txs to merkle root from block 170 (technically a merkle branch)
3. same as 2 but has one digit changed in first tx hash, so should fail
4. add merkle root of block 546, first block with >2 tx
5. add merkle branch for tx 1 and 2 from block 546, three hashs total
6. add broken merkle root for block 547 (last digit incremented by 1) - incorrect merkle root, correct block, should fail
7. add merkle root for nonexistant block 547 (first digit incremented by 1), should fail
8. add correct merkle root for block 547
'''
transactions_merkletracker = [
# remember the endianness!
# remember every hash past the second needs lr byte
(True, Transaction('MERKLETRACKER',10**14,10**8,[0,EBN("ff104ccb05421ab93e63f8c3ce5c2c2e9dbb37de2764b3a3175c8166562cac7d"),EBN("eea2d48d2fced4346842835c659e493d323f06d4034469a8905714d100000000")],'alice')),
(True, Transaction('MERKLETRACKER',10**14,10**8,[1,EBN("82501c1178fa0b222c1f3d474ec726b832013f0a532b44bb620cce8624a5feb1"),EBN("169e1e83e930853391bc6f35f605c6754cfead57cf8387639d3b4096c54f18f4")],'alice')),
(False, Transaction('MERKLETRACKER',10**14,10**8,[1,EBN("82501c1178fa0b222c1f3d474ec726b832013f0a532b44bb620cce8624a5feb3"),EBN("169e1e83e930853391bc6f35f605c6754cfead57cf8387639d3b4096c54f18f4")],'alice')),
(True, Transaction('MERKLETRACKER',10**14,10**8,[0,EBN("fe7d5e12ef0ff901f6050211249919b1c0653771832b3a80c66cea42847f0ae1"),EBN("e64ac3beec275a3edc5a0dfe11b51014b7afefce067e661e78ed4d5a00000000")],'alice')),
(True, Transaction('MERKLETRACKER',10**14,10**8,[1,EBN("703bb9ec7ab4f56d9e417a53ac19cef9c53513dc0352b9734e012d799ffe80e9"),EBN("5f9a06d3acdceb56be1bfeaa3e8a25e62d182fa24fefe899d1c17f1dad4c2028"),EBN("00e91eb9b0ede8c4735562363d58e31e061b71826c50cfdcccda62dadb25bad8b1")],'alice')),
(False, Transaction('MERKLETRACKER',10**14,10**8,[0,EBN("d2904c383785ce368c59e2145dda1b393c169318d8baf0242fa5c62e40cbf9bd"),EBN("77ebe63083af4cd6860105feda4a70065cdae0949bac1b54fb85af5500000000")],'alice')),
(False, Transaction('MERKLETRACKER',10**14,10**8,[0,EBN("d2904c383785ce368c59e2145dda1b393c169318d8baf0242fa5c62e40cbf9bc"),EBN("87ebe63083af4cd6860105feda4a70065cdae0949bac1b54fb85af5500000000")],'alice')),
(True, Transaction('MERKLETRACKER',10**14,10**8,[0,EBN("d2904c383785ce368c59e2145dda1b393c169318d8baf0242fa5c62e40cbf9bc"),EBN("77ebe63083af4cd6860105feda4a70065cdae0949bac1b54fb85af5500000000")],'alice')),

]
