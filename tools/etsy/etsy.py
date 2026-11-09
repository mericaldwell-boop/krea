#!/usr/bin/env python3
"""Small Etsy Open API v3 helper for managing the SailAndSeekStudio shop.

Secrets are never stored in this repo:
  * The API key header (x-api-key: <keystring>:<shared secret>) is injected by the
    session's network proxy, so this script sends a placeholder value.
  * OAuth tokens are kept in ~/.etsy_tokens.json (outside the repo).

Usage:
  etsy.py auth-url  <keystring>             print the one-time login link
  etsy.py auth-code <keystring> <code>      exchange the code for tokens
  etsy.py me                                show the connected user + shop
  etsy.py listings [state]                  list listings (active|draft|inactive|expired)
  etsy.py get <listing_id>                  show one listing
  etsy.py update <listing_id> <json-file>   PATCH title/description/tags/etc.
  etsy.py add-image <listing_id> <path> [rank]
  etsy.py images <listing_id>
  etsy.py delete-image <listing_id> <listing_image_id>
  etsy.py add-file <listing_id> <path> [name]
  etsy.py sections                          list shop sections
"""
import base64, hashlib, json, os, secrets, sys, time
import requests

API = "https://openapi.etsy.com/v3/application"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
CONNECT_URL = "https://www.etsy.com/oauth/connect"
REDIRECT = "https://localhost:3003/oauth/redirect"
SCOPES = "listings_r listings_w shops_r shops_w transactions_r"
STORE = os.path.expanduser("~/.etsy_tokens.json")
PLACEHOLDER_KEY = "proxy-injects-real-key"


def load():
    try:
        with open(STORE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(d):
    with open(STORE, "w") as f:
        json.dump(d, f)
    os.chmod(STORE, 0o600)


def auth_url(keystring):
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    d = load(); d.update(keystring=keystring, verifier=verifier, state=state); save(d)
    from urllib.parse import urlencode, quote
    q = CONNECT_URL + "?" + urlencode(dict(
        response_type="code", client_id=keystring, redirect_uri=REDIRECT, scope=SCOPES,
        state=state, code_challenge=challenge, code_challenge_method="S256"), quote_via=quote)
    print(q)


def token_request(data):
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    t = r.json()
    d = load()
    d.update(access_token=t["access_token"], refresh_token=t["refresh_token"],
             expires_at=time.time() + t.get("expires_in", 3600) - 60,
             user_id=t["access_token"].split(".")[0])
    save(d)
    return d


def auth_code(keystring, code):
    d = load()
    token_request(dict(grant_type="authorization_code", client_id=keystring,
                       redirect_uri=REDIRECT, code=code, code_verifier=d["verifier"]))
    print("Connected. Tokens saved to", STORE)


def token():
    d = load()
    if not d.get("refresh_token"):
        sys.exit("Not connected yet: run auth-url / auth-code first.")
    if time.time() > d.get("expires_at", 0):
        d = token_request(dict(grant_type="refresh_token", client_id=d["keystring"],
                               refresh_token=d["refresh_token"]))
    return d["access_token"]


def call(method, path, **kw):
    h = kw.pop("headers", {})
    h.update({"x-api-key": PLACEHOLDER_KEY, "Authorization": f"Bearer {token()}"})
    r = requests.request(method, API + path, headers=h, timeout=60, **kw)
    if r.status_code >= 400:
        sys.exit(f"{method} {path} -> {r.status_code}: {r.text[:800]}")
    return r.json() if r.content else {}


def shop_id():
    d = load()
    if "shop_id" not in d:
        me = call("GET", "/users/me")
        d["shop_id"] = me["shop_id"]; save(d)
    return d["shop_id"]


def main(a):
    cmd = a[0] if a else "help"
    if cmd == "auth-url":
        auth_url(a[1])
    elif cmd == "auth-code":
        auth_code(a[1], a[2])
    elif cmd == "me":
        print(json.dumps(call("GET", "/users/me"), indent=1))
    elif cmd == "listings":
        state = a[1] if len(a) > 1 else "active"
        out, off = [], 0
        while True:
            r = call("GET", f"/shops/{shop_id()}/listings", params=dict(state=state, limit=100, offset=off))
            out += r["results"]; off += 100
            if off >= r["count"]:
                break
        for l in out:
            print(l["listing_id"], "|", l["state"], "|", l["title"][:90])
    elif cmd == "get":
        print(json.dumps(call("GET", f"/listings/{a[1]}", params={"includes": "Images"}), indent=1))
    elif cmd == "update":
        body = json.load(open(a[2]))
        r = call("PATCH", f"/shops/{shop_id()}/listings/{a[1]}", data=body)
        print("updated", r.get("listing_id"), r.get("title"))
    elif cmd == "add-image":
        rank = a[3] if len(a) > 3 else None
        data = {"rank": rank} if rank else {}
        with open(a[2], "rb") as f:
            r = call("POST", f"/shops/{shop_id()}/listings/{a[1]}/images", files={"image": f}, data=data)
        print("image", r.get("listing_image_id"), "rank", r.get("rank"))
    elif cmd == "images":
        for i in call("GET", f"/listings/{a[1]}/images")["results"]:
            print(i["listing_image_id"], "rank", i["rank"], i["url_570xN"])
    elif cmd == "delete-image":
        call("DELETE", f"/shops/{shop_id()}/listings/{a[1]}/images/{a[2]}")
        print("deleted", a[2])
    elif cmd == "add-file":
        name = a[3] if len(a) > 3 else os.path.basename(a[2])
        with open(a[2], "rb") as f:
            r = call("POST", f"/shops/{shop_id()}/listings/{a[1]}/files", files={"file": f}, data={"name": name})
        print("file", r.get("listing_file_id"), r.get("filename"))
    elif cmd == "sections":
        for s in call("GET", f"/shops/{shop_id()}/sections")["results"]:
            print(s["shop_section_id"], s["title"])
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
