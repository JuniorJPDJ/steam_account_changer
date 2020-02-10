#!/usr/bin/env python3
import sys
import json
import time

import gevent
import gevent.event
from google.protobuf import json_format

from steam.client import SteamClient, EMsg
from steam.enums import EResult, ECurrencyCode
from csgo import CSGOClient

with open('acc.json', 'r') as f:
    accounts = json.load(f)

events = []

def run_account(acc):
    client = SteamClient()
    client.set_credential_location('creds')
    cs = CSGOClient(client)
    profile = gevent.event.Event()
    matches = gevent.event.Event()
    mm = gevent.event.Event()
    events.append(profile)
    events.append(matches)
    events.append(mm)

    @client.on('logged_on')
    def start_csgo():
        print("Logged in!")
        cs.launch()
        print("Launched CS:GO")

    @client.on('new_login_key')
    def key():
        print(f"New login key for {acc['username']}!")
        acc['login_key'] = client.login_key

#    @client.on(None)
#    def debug(msgtype, msg=None):
#        print(msgtype)
#        print(msg)

    @client.on(EMsg.ClientVACBanStatus)
    def vac_status(msg):
        acc['bans'] = msg.body.numBans

    @client.on(EMsg.ClientEmailAddrInfo)
    def email(msg):
        acc['email'] = msg.body.email_address

    @client.on(EMsg.ClientAccountInfo)
    def name(msg):
        acc['name'] = msg.body.persona_name

    @client.on(EMsg.ClientWalletInfoUpdate)
    def name(msg):
        if msg.body.currency:
            acc['wallet_balance'] = msg.body.balance64
            acc['wallet_balance_delayed'] = msg.body.balance64_delayed
            acc['wallet_currency'] = msg.body.currency

#    @cs.on(None)
#    def debug(msgtype, msg=None):
#        if str(msgtype) not in ('ECsgoGCMsg.EMsgGCCStrike15_v2_MatchList', 'recent_user_games'):   # huuuge messages
#            print("Type:", msgtype)
#            print(msg)

    @cs.on('ready')
    def gc_ready():
        print("CS:GO Ready!")
        cs.request_player_profile(cs.account_id)
        cs.request_recent_user_games(cs.account_id)
        cs.request_matchmaking_stats()
        print("Requested player profile info")

    @cs.on('recent_user_games')
    def got_matches(resp):
        if len(resp.matches) > 0:
            acc['csgo_last_mm'] = max(m.matchtime for m in resp.matches)
        matches.set()

    @cs.on('player_profile')
    def got_profile(response):
        if response.account_id == cs.account_id:
            print(f"Got {acc['username']} CS:GO profile!")
            acc['csgo_profile'] = json.loads(json_format.MessageToJson(response))
            #cs.exit()
            #client.logout()
            profile.set()

    @cs.on('matchmaking_stats')
    def got_mm_stats(resp):
        if resp.penalty_seconds:
            acc['csgo_penalty_end'] = resp.penalty_seconds + int(time.time())
            acc['csgo_penalty_reason'] = resp.penalty_reason
        mm.set()

#    def cleanup():
# TODO: group accounts in events and log out from csgo/steam
# TODO: write refresh date
        

    print(f'Logging in to {acc["username"]}')
    if 'login_key' not in acc or client.login(acc['username'], login_key=acc['login_key']) != 1:
        client.cli_login(acc['username'], acc['password'])

for acc in accounts:
    run_account(accounts[acc])

gevent.joinall(events)

with open('acc.json', 'w') as f:
    json.dump(accounts, f)
