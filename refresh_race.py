#!/usr/bin/env python3

import argparse
import os
import random
import signal
import sys
import time
import threading
import requests

failed = []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain")
    parser.add_argument("--client-id", default=os.environ.get("FRONTEGG_CLIENT_ID"))
    parser.add_argument("--secret-key", default=os.environ.get("FRONTEGG_SECRET_KEY"))
    args = parser.parse_args()

    if not args.domain:
        print("fatal: domain not specified", file=sys.stderr)
        return 1
    if not args.client_id:
        print("fatal: client ID not specifid", file=sys.stderr)
        return 1
    if not args.secret_key:
        print("fatal: client secret not specifid", file=sys.stderr)
        return 1

    exchange_url = f"https://{args.domain}/identity/resources/auth/v1/api-token"
    refresh_url = f"{exchange_url}/token/refresh"

    threads = []
    for i in range(1, 100):
        thread = threading.Thread(target=do_exchange, args=(i, exchange_url, refresh_url, args.client_id, args.secret_key))
        thread.start()
        threads.append(thread)
        # Sleep for between .3s and 1.3s. Weird, but seems to trigger the bug.
        time.sleep(random.random() + .3)
    for thread in threads:
        thread.join()

    if failed:
        print(f"fatal: {len(failed)} threads failed to refresh!", file=sys.stderr)
        print(sorted(failed), file=sys.stderr)
        print("see logs above for error messages", file=sys.stderr)
        return 1
    return 0



def do_exchange(i, exchange_url, refresh_url, client_id, secret_key):
    time.sleep(random.random())
    print(f"{i}: starting")

    exchange_response = requests.post(exchange_url, json={"clientId": client_id, "secret": secret_key})
    exchange_response.raise_for_status()
    refresh_token = exchange_response.json()['refreshToken']
    print(f"{i}: exchanged API key for refresh token: {refresh_token}")

    # Sleep for 10s. Again weird, but the bug doesn't happen if you remove this.
    time.sleep(10)

    refresh_response = requests.post(refresh_url, json={"refreshToken": refresh_token})
    try:
        refresh_response.raise_for_status()
    except:
        failed.append(i)
        print(f"{i}: failed to refresh token: {refresh_response.text}")
        raise
    refresh_token = refresh_response.json()['refreshToken']
    print(f"{i}: exchanged refresh token successfully for new refresh token: {refresh_token}")

if __name__ == "__main__":
    sys.exit(main())
