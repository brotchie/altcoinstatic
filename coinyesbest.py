#!/usr/bin/env python

"""
Example of using coinyecoind to generate a static webpage
of Kanye West tracks ranked by the amount of COYE donated
to each track's pubkey address.

Use './coinyesbest.py createaccounts' to initialize accounts then
'./coinyesbest.py generateindex' to generate the static ranking page
in output/index.html.

Server output/ using a webserver to view the site. e.g.
    twistd web --path=output -p 8082
    google-chrome http://localhost:8082/

This can be easily modified to interface with litecoind, bitcoind,
or any other crypto-currency based off the bitcoin sources.

Setup coinyecoind JSON-RPC by adding the rpcuser and rpcpassword config
entries to ~/.coinyecoin/coinyecoin.conf.

Depends on bitcoin-python and mako templates:
    sudo pip install bitcoin-python mako

"""

import os
import re
import csv
import sys
import json

import bitcoinrpc
from mako.template import Template

COINYE_RPC_PORT = 41337
COINYE_CONF_PATH = os.path.expanduser('~/.coinyecoin/coinyecoin.conf')

ADDRESSES_JSON_PATH = './addresses.json'
KANYE_TRACKS_CSV_PATH = './kanye.csv'

INDEX_TEMPLATE_PATH = 'templates/index.html'
INDEX_OUTPUT_PATH = 'output/index.html'

KEY_RPC_PASSWORD = 'rpcpassword'
KEY_RPC_USER = 'rpcuser'

ACTION_CREATE_ACCOUNT = 'createaccount'
ACTION_GENERATE_INDEX = 'generateindex'
VALID_ACTIONS = [ACTION_CREATE_ACCOUNT, ACTION_GENERATE_INDEX]

def parse_config(path=COINYE_CONF_PATH):
    """ Parses the coinyecoin config file
    """
    if not os.path.exists(path):
        raise IOError('Could not find coinyecoind config file at "{}".'.format(path))

    cfg = {}
    for entry in file(path):
        if '=' not in entry:
            continue
        key, value = entry.split('=', 1)
        cfg[key.strip()] = value.strip()
    return cfg

def load_addresses(path=ADDRESSES_JSON_PATH):
    """ Load a map from account names to pubkey addresses.
    """
    if os.path.exists(path):
        print 'Read addresses from "{}".'.format(path)
        return json.load(file(path))
    else:
        print 'Addresses not found at "{}" using empty address list.'.format(path)
        return {}

def save_addresses(addresses, path=ADDRESSES_JSON_PATH):
    """ Save a map from account names to pubkey addresses.
    """
    print 'Wrote {} addresses to "{}".'.format(len(addresses), path)
    json.dump(addresses, file(path, 'w+'))

CLEAN_RE = re.compile('[^A-Za-z0-9]')

def genkey(value):
    """ Strip all non-alphanumeric characters out of a string.
        Used to generate simple wallet account names.
    """
    return CLEAN_RE.sub('', value)

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in VALID_ACTIONS:
        sys.stderr.write('Invalid action. Available actions: {}.\n'
                            .format(', '.join(VALID_ACTIONS)))
        sys.exit(1)
    action = sys.argv[1]

    cfg = parse_config()
    if KEY_RPC_USER not in cfg or KEY_RPC_PASSWORD not in cfg:
        raise KeyError('coinyecoind config file must contain "{}" and "{}" entries.'
                        .format(KEY_RPC_USER, KEY_RPC_PASSWORD))

    addresses = load_addresses()
    rpc = bitcoinrpc.connect_to_remote(cfg[KEY_RPC_USER], cfg[KEY_RPC_PASSWORD], port=COINYE_RPC_PORT)

    if not os.path.exists(KANYE_TRACKS_CSV_PATH):
        raise IOError('List of Kanye West tracks not found at "{}".'.format(KANYE_TRACKS_CSV_PATH))
    kanye_tracks = csv.reader(file(KANYE_TRACKS_CSV_PATH))

    if action == ACTION_CREATE_ACCOUNT:
        # getaccountaddresses creates a new address even if that
        # account already exists. We only want a 1:1 mapping between
        # wallet accounts and addresses so we only call getaccountaddress
        # once per track and then store these addresess in addresses.json.
        accounts = rpc.listaccounts()
        for (track, title, album, year) in kanye_tracks:
            key = genkey(title + album)
            if key not in accounts:
                print 'Creating account ' + key
                addresses[key] = rpc.getaccountaddress(key)
                print 'Created account ' + key + ' with address ' + addresses[key]
        save_addresses(addresses)
    elif action == ACTION_GENERATE_INDEX:
        tracks = []
        for (track, title, album, year) in kanye_tracks:
            key = genkey(title + album)
            balance = rpc.getbalance(key)
            tracks.append({
                'track': track,
                'title': title,
                'album': album,
                'year': year,
                'address': addresses[key],
                'balance': float(balance),
                'balance_text': '%.2f' % float(balance)
            })
        # We rank the tracks by the amount of COYE donated to each.
        tracks.sort(key=lambda x: x['balance'], reverse=True)
        template = Template(filename=INDEX_TEMPLATE_PATH)
        print 'Read template from "{}".'.format(INDEX_TEMPLATE_PATH)
        file(INDEX_OUTPUT_PATH, 'w+').write(template.render(tracks=tracks))
        print 'Wrote rendered template to "{}".'.format(INDEX_OUTPUT_PATH)

if __name__ == '__main__':
    main()
