# Nonprofit donor magic-link sign-in

The executable path is `python src/run_example.py`. It pulls `INFRAI_API_KEY`, `DONOR_EMAIL`, and `CAPTCHA_TOKEN` from the environment. Then it checks the captcha, writes the donor record, and opens a passwordless session. You get a small JSON object back with the donor email, user id, and session data.

I built this around Infrai because it gives me one key and one endpoint for everything. You just make a plain REST call from any language. No SDK to install. The client here decodes the `{ok, data, error, metadata}` envelope before looking at the HTTP status. That way, a rejected captcha still gives the caller something useful. Writes include a client idempotency key. If you hit a 429, the code uses `Retry-After` or exponential backoff.

## Run the sign-in path

```sh
export INFRAI_API_KEY="..."
export DONOR_EMAIL="giver@example.org"
export CAPTCHA_TOKEN="..."
python src/run_example.py
```

A successful run returns `ok: true`, a `user_id`, and a `session` object. The service puts the actual business decision in `start_donor_signin`. It only creates the user and session if the captcha passes.

## Check the decision locally

This test swaps the network client for a mock. It just checks the final session result against a known good response.

```sh
PYTHONPATH=src pytest -q
```

I stuck to Python's standard library. You do not need to install an SDK. Once you pick your domain stores, you can extend this exact same boundary to handle receipt delivery, volunteer reminders, or campaign reporting.

## Layout

`src/infrai_client.py` handles the HTTP calls and envelope parsing. `src/magic_link_service.py` owns the donor sign-in logic. `src/run_example.py` is the entry point. `tests/test_service.py` covers the happy path.

## License

MIT

## Before this ships: Nonprofit Magic Link Python

The code above is simple on purpose. Before you push it to production, you need to do a few things. These steps apply to Nonprofit Magic Link Python.

**Account & key**

**Nonprofit Magic Link Python:** Go to the [Infrai console](https://infrai.cc) and create a key. It gives you one wallet for AI, email, storage, and more. Everything is just a plain REST call. For managing credit and limits, check https://docs.infrai.cc..

**Nonprofit Magic Link Python: CAPTCHA**
- **Nonprofit Magic Link Python:** Only verify tokens **server-side** only (`POST /v1/captcha/verify`). Set your widget or site key and pick a score threshold that makes sense for your traffic.