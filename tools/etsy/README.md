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

## Current live listings (relinked 2026-11-16)
On 2026-11-16 Printify republished every product as a new Etsy listing. The new listings below are the ones linked to Printify, and the old ones are inactive.
Never connect GHL (or anything else) to the SailAndSeekStudio Printify store.

| Product | Live listing | Old (inactive) |
|---|---|---|
| Cruise Crew Loading shirt | 4618332689 | 4608517578 |
| Family Cruise shirt | 4618332127 | 4609487330 |
| Girls Trip retro chairs shirt | 4618332403 | 4610978521 |
| Girls Trip badge shirt | 4618337932 | 4611665839 |
| Anniversary Cruise shirt | 4618331767 | 4613023056 |
| Family Cruise door magnet | 4618331987 | 4612836132 |
| Family Cruise name magnet | 4618331825 | 4612830337 |
| Family Cruise sticker | 4618331945 | 4613478436 |
| Anniversary sticker | 4618337394 | 4613486460 |
| Girls Trip sticker | 4618337490 | 4613489848 |
| Girls Trip badge sticker | 4618331915 | 4613705344 |
| Family Cruise door kit (digital) | 4612761780 | unchanged |
