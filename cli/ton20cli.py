import sys, os
import asyncio
import json
from typing import Optional
from pytoniq import WalletV3R2, WalletV4R2, Address, begin_cell
from pytoniq.liteclient.balancer import LiteBalancer
import aiohttp

def make_json_cell(data: dict):
    return begin_cell() \
            .store_uint(0, 32) \
            .store_snake_string(f"data:application/json,{json.dumps(data, separators=(',', ':'))}") \
           .end_cell()

def ton20_make_mint(amount: int, tick: str):  
    return make_json_cell({
        "p": "ton-20",
        "op": "mint",
        "tick": tick,
        "amt": str(amount)
    })


def ton20_make_deploy(tick: str, supply: int, per_mint: int):
    return make_json_cell({
        "p": "ton-20",
        "op": "deploy",
        "tick": tick,
        "max": str(supply),
        "lim": str(per_mint)
    })


def ton20_make_transfer(amount: int, tick: str, recipient: str):
    return make_json_cell({
        "p": "ton-20",
        "op": "transfer",
        "tick": tick,
        "to": recipient,
        "amt": str(amount)
    })

async def ton20_get_balance(address: str, tick: str):
    headers = {
        'Authority': 'dton.io',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'Origin': 'https://tonano.io',
        'Pragma': 'no-cache',
        'Referer': 'https://tonano.io/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    json_data = {
        'operationName': 'GetWalletCoins',
        'variables': {
            'address': address,
            'tick': tick
        },
        'query': """query GetWalletCoins($address: String, $tick: String) {
                coins: ton20wallets(
                    address: $address
                    tick: $tick
                ) {
                    amount
                    address
                    tick
                }
        }""",
    }

    balance = 0
    async with aiohttp.ClientSession() as session:
        async with session.post('https://dton.io/graphql_tonano', headers=headers, json=json_data) as response:
            result = await response.json()
            if ('data' in result) and ('coins' in result['data']):
                coins = result['data']['coins']
                balance = int(coins[0]['amount']) if coins else 0
    return balance


async def main():
    import argparse

    parser_base = argparse.ArgumentParser(description='TON20 Command Line Interface', add_help=False)
    parser_base.add_argument('command', choices=['mint', 'deploy', 'transfer', 'balance', 'new-wallet'], help='Command to execute')

    parser = argparse.ArgumentParser(parents=[parser_base], description=parser_base.description, add_help=False)
    parser.add_argument('args', nargs='*', help='Arguments for the command')
    args = parser.parse_args(args = sys.argv[1:2])

    parser_mnemo = argparse.ArgumentParser(add_help=False)
    mnemo_group = parser_mnemo.add_mutually_exclusive_group(required=True)
    mnemo_group.add_argument('--mnemo', help='Mnemo phrase')
    mnemo_group.add_argument('--mnemo-file', help='Mnemo phrase file')
    parser_mnemo.add_argument('--wallet-type', help='Wallet type', choices=['auto', 'V4R2', 'V3R2'], default='auto')

    parser_addr = argparse.ArgumentParser(add_help=False)
    addr_group = parser_addr.add_mutually_exclusive_group(required=True)
    addr_group.add_argument('--mnemo', help='Mnemo phrase')
    addr_group.add_argument('--mnemo-file', help='Mnemo phrase file')
    parser_addr.add_argument('--wallet-type', help='Wallet type', default='V4R2')
    addr_group.add_argument('--address', help='Address')

    all_parsers = []

    if args.command == 'mint':
        parser = argparse.ArgumentParser(description=parser_base.description, add_help=False)
        amount_group = parser.add_mutually_exclusive_group(required=True)
        amount_group.add_argument('--amount', type=str, help='Amount to mint')
        amount_group.add_argument('--amount-nano', type=int, help='Amount to mint (nano)')
        parser.add_argument('--tick', type=str, help='Ticker symbol', default = 'grum')
        parser.add_argument('--repeat', type=int, default=1, help='Number of times to mint')
        parser.add_argument('--msgs', type=int, help='Number of mint requests in one message (1..4)', default = 4)
        all_parsers.extend([parser, parser_mnemo])
    elif args.command == 'transfer':
        parser = argparse.ArgumentParser(description=parser_base.description, add_help=False)
        amount_group = parser.add_mutually_exclusive_group(required=True)
        amount_group.add_argument('--amount', type=str, help='Amount to mint')
        amount_group.add_argument('--amount-nano', type=int, help='Amount to mint (nano)')
        parser.add_argument('--tick', type=str, help='Ticker symbol', default = 'grum')
        parser.add_argument('--to', type=str, help='Recipient address', required=True)
        all_parsers.extend([parser, parser_mnemo])
    elif args.command == 'deploy':
        parser = argparse.ArgumentParser(description=parser_base.description, add_help=False)
        parser.add_argument('--tick', type=str, help='Ticker symbol', required=True)
        supply_group = parser.add_mutually_exclusive_group(required=True)
        supply_group.add_argument('--supply', type=str, help='Total Supply')
        supply_group.add_argument('--supply-nano', type=int, help='Total Supply (nano)')
        one_mint_group = parser.add_mutually_exclusive_group(required=True)
        one_mint_group.add_argument('--one-mint', type=str, help='Limit Per Mint')
        one_mint_group.add_argument('--one-mint-nano', type=int, help='Limit Per Mint (nano)')
        all_parsers.extend([parser, parser_mnemo])
    elif args.command == 'balance':
        parser = argparse.ArgumentParser(description=parser_base.description, add_help=False)
        parser.add_argument('--tick', type=str, help='Ticker symbol', default = 'grum')
        all_parsers.extend([parser, parser_addr])
    elif args.command == 'new-wallet':
        pass
    else:
        raise Exception(f"Unsupported command: {args.command}")

    parser = argparse.ArgumentParser(parents=[parser_base] + all_parsers, description=parser_base.description)
    args = parser.parse_args()

    async def load_wallet(provider: LiteBalancer, mnemo: Optional[str], mnemo_file: Optional[str], wallet_type: str = 'auto', check_balance: bool = True):
        res = None
        try:
            mnemo_list = []
            if(mnemo is not None):
                mnemo_list = mnemo.split()
            elif(mnemo_file is not None):
                with open(mnemo_file, "rt") as f:
                    s = f.readline()
                    mnemo_list = s.split()
                    if(len(mnemo_list) < 24):
                      s += f.read()
                      mnemo_list = s.split()
            else:
                raise Exception("Mnemo is not provided")
            if(len(mnemo_list) != 24):
                raise Exception(f"Unsupported mnemo length: expected 24 words, provieded {len(mnemo_list)}")
        except Exception as e:
            raise Exception(f"Unable to load or parse mnemo: {e}")

        wallets = []
        wallet_type = wallet_type.lower()
        try:
            if(wallet_type in ['auto', 'v4r2']):
                wallet_v4r2 = await WalletV4R2.from_mnemonic(provider = provider, mnemonics = mnemo_list)
                if(wallet_v4r2.is_active or wallet_v4r2.balance):
                    wallets.append(wallet_v4r2)
        except Exception as e:
            raise Exception(f"Checking v4r2 wallet: {e}")
        try:
            if(wallet_type in ['auto', 'v3r2']):
                wallet_v3r2 = await WalletV3R2.from_mnemonic(provider = provider, mnemonics = mnemo_list)
                if(wallet_v3r2.is_active or wallet_v3r2.balance):
                    wallets.append(wallet_v3r2)
        except Exception as e:
            raise Exception(f"Checking v3r2 wallet: {e}")
        if(len(wallets) == 0):
            raise Exception("No wallets found")
        wallets.sort(key = lambda w: w.balance, reverse = True)
        if(check_balance and wallets[0].balance == 0):
            raise Exception("No balance")
        return wallets[0]

    def parse_amount(amount: Optional[str], amount_nano: Optional[int], field_name: str = 'amount') -> int:
        res = None
        try:
            if(amount_nano is not None):
                res = amount_nano
            elif(isinstance(amount, str)):
                if( amount.isnumeric()):
                    res = int(amount) * 10**9
                else:
                    res = int(float(amount) * 1e9)
            if(res is None):
                raise Exception("Not provided")
            return res
        except Exception as e:
            raise Exception(f"Unable to parse {field_name}: {e}")

    while True:
        try:
            provider = LiteBalancer.from_mainnet_config(trust_level=1)
            blockchain_required = not(args.command == 'balance' and (args.mnemo is None) and (args.mnemo_file is None))
            provider_started = False
            if(blockchain_required):
              await provider.start_up()
              provider_started = True

            if args.command == 'mint':
                amount = parse_amount(args.amount, args.amount_nano)
                wallet = await load_wallet(provider, args.mnemo, args.mnemo_file, args.wallet_type)

                body = ton20_make_mint(amount, args.tick)
                repeat = args.repeat
                n_tx = 0

                print(f"Wallet: {wallet.address.to_str()}")
                print(f"Sending {repeat} transaction(s) with {args.msgs} message(s) each")
                print(f"You will mint: {(amount * repeat * args.msgs) / 1e9} {args.tick}")

                if(wallet.is_uninitialized):
                  print("Initializing wallet...")
                  await wallet.send_init_external()
                  while wallet.is_uninitialized:
                    await asyncio.sleep(1)
                    await wallet.update()

                while(n_tx < repeat):
                    n_tx += 1
                    is_last = n_tx == repeat
                    seqno = wallet.seqno
                    msg = wallet.create_wallet_internal_message(
                        destination=wallet.address,
                        value=0,
                        body=body,
                        send_mode=1
                    )
                    result = await wallet.raw_transfer(msgs=[msg] * args.msgs)
                    print(f"Sent tx {n_tx} with seqno {seqno}")

                    if(not is_last):
                      # Waiting tx complete
                      n_retry = 1000
                      while(n_retry > 0):
                          n_retry -= 1
                          await wallet.update()
                          if(wallet.seqno != seqno):
                              break
                          await asyncio.sleep(1)
            elif args.command == 'deploy':
                supply = parse_amount(args.supply, args.supply_nano, 'supply')
                per_mint = parse_amount(args.one_mint, args.one_mint_nano, 'one_mint')
                wallet = await load_wallet(provider, args.mnemo, args.mnemo_file, args.wallet_type)

                body = ton20_make_deploy(args.tick, supply, per_mint)
                msg = wallet.create_wallet_internal_message(
                    destination=wallet.address,
                    value=0,
                    body=body,
                    send_mode=1
                )
                result = await wallet.raw_transfer(msgs=[msg])
                print(f"Sent deploy tx")
            elif args.command == 'transfer':
                amount = parse_amount(args.amount, args.amount_nano)
                wallet = await load_wallet(provider, args.mnemo, args.mnemo_file, args.wallet_type)
                address_to = Address(args.to)

                body = ton20_make_transfer(amount, args.tick, args.to)
                msg = wallet.create_wallet_internal_message(
                    destination=wallet.address,
                    value=0,
                    body=body,
                    send_mode=1
                )
                result = await wallet.raw_transfer(msgs=[msg])
                print(f"Sent transfer tx")
            elif args.command == 'balance':
                if(args.mnemo is not None) or (args.mnemo_file is not None):
                    wallet = await load_wallet(provider, args.mnemo, args.mnemo_file, args.wallet_type, False)
                    address = wallet.address
                else:
                    address = Address(args.address)
                balance = await ton20_get_balance(address.to_str(), args.tick)
                print(f"Balance: {balance / 1e9} {args.tick} ({balance} nano{args.tick})")
            elif args.command == 'new-wallet':
                from pytoniq_core.crypto.keys import mnemonic_new
                mnemo = mnemonic_new(24)
                wallet = await WalletV4R2.from_mnemonic(provider, mnemo)
                print(f"New wallet mnemonic:\t{' '.join(mnemo)}")
                print(f'New wallet address: \t{wallet.address.to_str(is_bounceable=False)}')
                print(f'New wallet address: \t{wallet.address.to_str(is_bounceable=True)}')
                for i in range(1000000):
                  wallet_backup_file = f'wallet{str(i) if i else ""}.txt'
                  if(not os.path.exists(wallet_backup_file)):
                    with open(wallet_backup_file, "wt") as f:
                      print(" ".join(mnemo), file=f)
                      print('Address:', wallet.address.to_str(is_bounceable=False), file=f)
                      print('Address:', wallet.address.to_str(is_bounceable=True), file=f)
                    break
            else:
                raise Exception(f"Unsupported command: {args.command}")
        except Exception as e:
            print(f"Error: {e}", file = sys.stderr)
        break

    if(provider_started):
      await provider.close_all()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    #asyncio.run(main())
