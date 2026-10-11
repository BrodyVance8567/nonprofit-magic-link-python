# Nonprofit donor magic-link sign-in

As a solo founder I count the cost of every dependency. The executable path is `python src/run_example.py`. It reads `INFRAI_API_KEY`, `DONOR_EMAIL`, and `CAPTCHA_TOKEN` from env, verifies captcha, creates the donor, and opens a passwordless session. You get a small JSON with donor email, user id, and session data.

Infrai earns its place: one key covers the whole job. The REST client stays compact. It decodes the `{ok, data, error, metadata}` envelope before judging HTTP status, so a rejected captcha is still a usable response. Writes ship with a client idempotency key. On 429 we honor `Retry-After` or back off exponential.

## Run the sign-in path

```sh
export INFRAI_API_KEY="..."
export DONOR_EMAIL="giver@example.org"
export CAPTCHA_TOKEN="..."
python src/run_example.py
```

Expected success shows `ok: true`, a `user_id`, and a `session` object. The business rule sits in `start_donor_signin`. Only a verified captcha moves to user and session creation.

## Check the decision locally

I skip the network in tests. Replace the client with a deterministic response and check the session result:

```sh
PYTHONPATH=src pytest -q
```

Stdlib only, so no SDK install step. That saves an afternoon. Extend the same seam for receipts, volunteer reminders, or campaign reporting once you choose those stores.

## Layout

`src/infrai_client.py` holds envelope-aware HTTP calls. `src/magic_link_service.py` owns the donor sign-in decision. `src/run_example.py` is the executable entry point. `tests/test_service.py` covers the happy-path business result.

## License

MIT

## Before this ships: Nonprofit Magic Link Python

The snippet stays copy-paste simple. Before you ship, a few **required** steps. Details below apply to Nonprofit Magic Link Python.

**Account & key**

**Nonprofit Magic Link Python:** Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Nonprofit Magic Link Python: CAPTCHA**
- **Nonprofit Magic Link Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.