# Frontegg refresh race

Demonstrates a race condition in Frontegg's issuance of refresh tokens.

Setup:

```shell
python3 -m venv env
. venv/bin/activate
pip install -r requirements.txt
```

Usage:

```shell
export FRONTEGG_CLIENT_ID=<...>
export FRONTEGG_SECRET_KEY=<...>

./refresh_race.py --domain=admin.cloud.materialize.com
```

The script launches 100 threads over the course of a minute or so. It waits
a random amount of time, between .3 and 1.3s, between launching each thread.
(The bug apparently doesn't reproduce without this sleep.)

Each thread:

  * Exchanges the API key for a refresh token.
  * Sleeps for 10s. (The bug doesn't seem to reproduce without this sleep
    either.)
  * Exchanges the refresh token for a new refresh token.

In all of my tests, the script fails because at least one of the threads fails
to refresh its token. Unless we're completely misunderstanding the Frontegg API,
this seems to pretty clearly demonstrate that Frontegg is occasionally losing
track of refresh tokens.
