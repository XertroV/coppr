# coppr

## COntract PreProcessor and testeR

Coppr aims to provide a simple way to test contracts for *Ethereum*
locally and without a testnet. It is not a substitute for the testnet,
however. Coppr aims to ignore the details you don't need, and only
provide what is needed for the contract logic to be tested.

Contracts need to be written in the preprocessor language, which is
easily translated (by a computer) into Ethereum's pure HLL, to later be
compiled into Ethereum's assembly language.

Since Ethereum's HLL is very similar to python, Coppr asks that you
actually write python code, which is far more useful for testing. The
testing framework is provided by Coppr, so only the contract needs to be
written.

## Using Coppr

Ethereum is very limited when it comes to datatypes, which is useful.
Every variable in your contract should be a string or integer, which are
both stored in the EBN data structure (ethereum byte number). Arithmetic
operations treat the data as a number, and slices treat the data as a
list or array.

***While coppr is in development please see chainheaders.py / test-chainheaders.py
and merkletracker.py / test-merkletracker.py and extrapolate what do do from that.***

The dream is:

`coppr contract.coppr tests.tests` to test and give some nice output and 
`coppr contract.coppr` to 'compile' to the HLL / CHLL.

## Substitutions

There are a few changes needed to be made between the Ethereum HLL and
python, which are detailed below:

* Raising to the power: use `**` instead of `^`
* Concatenation: ebn1.concat(enb2) returns the concatenation equivelant to ebn1+ebn2


