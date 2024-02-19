# TON20 command line interface

## Steps to mint

1. Install all requirements
2. Create new wallet (optional) and top it up
3. Mint TON20 token

## Installation

You need to install python3 and install all requirements with:
```python -m pip install -r requirements.txt```

## Create new wallet

Command:
```python ton20cli.py new-wallet```

Example:
```
> python ton20cli.py new-wallet

New wallet mnemonic:	muscle error cost theory vehicle meat lady bid roof thrive undo decade direct dress object behave credit record picture west loan august flight dance
New wallet address: 	UQCT_qPaCo4I_F09ub2dJth5ppIJVQxZdaGoMh_jfU1qe9xj
New wallet address: 	EQCT_qPaCo4I_F09ub2dJth5ppIJVQxZdaGoMh_jfU1qe4Gm
```

*** Your wallet mnemonic will be also saved in 'wallet.txt' file. Don't loose you wallet!

## Mint TON20

```> python ton20cli.py mint --help

usage: ton20cli.py [-h] (--amount AMOUNT | --amount-nano AMOUNT_NANO)
                   [--tick TICK] [--repeat REPEAT] [--msgs MSGS]
                   (--mnemo MNEMO | --mnemo-file MNEMO_FILE)
                   [--wallet-type {auto,V4R2,V3R2}]
                   {mint,deploy,transfer,balance,new-wallet}

TON20 Command Line Interface

positional arguments:
  {mint,deploy,transfer,balance,new-wallet}
                        Command to execute

optional arguments:
  -h, --help            show this help message and exit
  --amount AMOUNT       Amount to mint
  --amount-nano AMOUNT_NANO
                        Amount to mint (nano)
  --tick TICK           Ticker symbol
  --repeat REPEAT       Number of times to mint
  --msgs MSGS           Number of mint requests in one message (1..4)
  --mnemo MNEMO         Mnemo phrase
  --mnemo-file MNEMO_FILE
                        Mnemo phrase file
  --wallet-type {auto,V4R2,V3R2}
                        Wallet type
```

Where:

* `mnemo` you can pass your mnemonic in command line
* `mnemo-file` is the path to to file with your mnemonic

Example:

```> python ton20cli.py mint --tick grum --amount 1234 --mnemo-file wallet.txt --repeat 10000

Wallet: EQCT_qPaCo4I_F09ub2dJth5ppIJVQxZdaGoMh_jfU1qe4Gm
Sending 3 transaction(s) with 4 message(s) each
You will mint: 14808.0 grum
Sent tx 1 with seqno 7
Sent tx 2 with seqno 8
Sent tx 3 with seqno 9
```

## Transfer TON20

```> python ton20cli.py transfer --help

usage: ton20cli.py [-h] (--amount AMOUNT | --amount-nano AMOUNT_NANO)
                   [--tick TICK] --to TO
                   (--mnemo MNEMO | --mnemo-file MNEMO_FILE)
                   [--wallet-type {auto,V4R2,V3R2}]
                   {mint,deploy,transfer,balance,new-wallet}

TON20 Command Line Interface

positional arguments:
  {mint,deploy,transfer,balance,new-wallet}
                        Command to execute

optional arguments:
  -h, --help            show this help message and exit
  --amount AMOUNT       Amount to mint
  --amount-nano AMOUNT_NANO
                        Amount to mint (nano)
  --tick TICK           Ticker symbol
  --to TO               Recipient address
  --mnemo MNEMO         Mnemo phrase
  --mnemo-file MNEMO_FILE
                        Mnemo phrase file
  --wallet-type {auto,V4R2,V3R2}
                        Wallet type
```

Example:

```> python ton20cli.py transfer --tick grum --amount 12345 --to UQDc4RBidUBLRYeGhSGoNzoxBkMJCCq-o6prwZW-PboQVu7P --mnemo-file wallet.txt

Sent transfer tx
```

## Query TON20 Balance

```> python ton20cli.py balance --help

usage: ton20cli.py [-h] [--tick TICK] [--mnemo MNEMO]
                   [--mnemo-file MNEMO_FILE] [--wallet-type WALLET_TYPE]
                   [--address ADDRESS]
                   {mint,deploy,transfer,balance,new-wallet}

TON20 Command Line Interface

positional arguments:
  {mint,deploy,transfer,balance,new-wallet}
                        Command to execute

optional arguments:
  -h, --help            show this help message and exit
  --tick TICK           Ticker symbol
  --mnemo MNEMO         Mnemo phrase
  --mnemo-file MNEMO_FILE
                        Mnemo phrase file
  --wallet-type WALLET_TYPE
                        Wallet type
  --address ADDRESS     Address
```

Examples:

```> python ton20cli.py balance --tick grum --mnemo-file wallet.txt

Balance: 44424.0 grum (44424000000000 nanogrum)
```

```> python ton20cli.py balance --tick nano --address UQDc4RBidUBLRYeGhSGoNzoxBkMJCCq-o6prwZW-PboQVu7P

Balance: 501.0 nano (501000000000 nanonano) 
```

## Deploy TON20

```> python ton20cli.py deploy --help

usage: ton20cli.py [-h] --tick TICK
                   (--supply SUPPLY | --supply-nano SUPPLY_NANO)
                   (--one-mint ONE_MINT | --one-mint-nano ONE_MINT_NANO)
                   (--mnemo MNEMO | --mnemo-file MNEMO_FILE)
                   [--wallet-type {auto,V4R2,V3R2}]
                   {mint,deploy,transfer,balance,new-wallet}

TON20 Command Line Interface

positional arguments:
  {mint,deploy,transfer,balance,new-wallet}
                        Command to execute

optional arguments:
  -h, --help            show this help message and exit
  --tick TICK           Ticker symbol
  --supply SUPPLY       Total Supply
  --supply-nano SUPPLY_NANO
                        Total Supply (nano)
  --one-mint ONE_MINT   Limit Per Mint
  --one-mint-nano ONE_MINT_NANO
                        Limit Per Mint (nano)
  --mnemo MNEMO         Mnemo phrase
  --mnemo-file MNEMO_FILE
                        Mnemo phrase file
  --wallet-type {auto,V4R2,V3R2}
                        Wallet type
```

Example:

```> python ton20cli.py deploy --tick github.com/grumpy-ton/ton20 --supply 102030 --one-mint 10203 --mnemo-file wallet.txt

Sent deploy tx
```
