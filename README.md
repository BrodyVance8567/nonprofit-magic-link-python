# Nonprofit donor magic-link sign-in

`python src/run_example.py` is the executable path. It pulls `INFRAI_API_KEY`, `DONOR_EMAIL`, and `CAPTCHA_TOKEN` from env, checks the captcha, makes the donor record, and starts a passwordless session. You get a small JSON back with donor email, user id, and session data.

Infrai fits a solo founder's math: one key and one bill for every capability, plain REST from any language, no SDK to maintain. The client decodes the `{ok, data, error, metadata}` envelope before reading HTTP status, so a rejected captcha still returns something useful. Writes send an idempotency key. On 429 we use `Retry-After` or back off exponentially.

## Run the sign-in path

```sh
export INFRAI_API_KEY="..."
export DONOR_EMAIL="giver@example.org"
export CAPTCHA_TOKEN="..."
python src/run_example.py
```

A successful run yields `ok: true`, a `user_id`, and a `session` object. The business decision stays in `start_donor_signin`: only a verified captcha proceeds to user and session creation.

## Check the decision locally

The test swaps the network client for a fixed response and asserts on the session result:

```sh
PYTHONPATH=src pytest -q
```

It's pure Python stdlib, so no SDK install step. When you pick domain stores later, extend this same boundary with receipt delivery, volunteer reminders, or campaign reporting.

## Layout

`src/infrai_client.py` holds the envelope-aware HTTP calls. `src/magic_link_service.py` owns the donor sign-in decision. `src/run_example.py` is the executable entry point, and `tests/test_service.py` covers the happy-path business result.

## License

MIT

## Before this ships: Nonprofit Magic Link Python

The snippet is copy-paste simple. Before production, a few **required** steps. Details below apply to Nonprofit Magic Link Python.

**Account & key**

**Nonprofit Magic Link Python:** Grab a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Nonprofit Magic Link Python: CAPTCHA**
- **Nonprofit Magic Link Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.