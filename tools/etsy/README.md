# Etsy connection (for Claude sessions)

The shop's Etsy app key is stored as the `ETSY_API_KEY` environment variable
(`keystring:shared_secret`) in the cloud environment settings. Never in this repo.

To connect in a new session:
1. `python3 tools/etsy/etsy.py auth-url 11nu4omsgtxqbr9q6n06q8lx`, then send the owner the link.
2. Owner clicks Allow and pastes back the `https://localhost:3003/oauth/redirect?code=...` address.
3. `python3 tools/etsy/etsy.py auth-code 11nu4omsgtxqbr9q6n06q8lx <code>`
4. Test with `python3 tools/etsy/etsy.py listings`.

There must be NO network secret for openapi.etsy.com: a saved network secret makes the
proxy strip the OAuth Authorization header.
