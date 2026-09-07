import json
import os

from infrai_client import InfraiClient
from magic_link_service import public_result


def main() -> None:
    email = os.environ.get("DONOR_EMAIL", "donor@example.org")
    token = os.environ.get("CAPTCHA_TOKEN", "sample-token")
    result = public_result(email, token, InfraiClient())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
