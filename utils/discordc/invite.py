from tls_client import Session
import requests


def get_invite_code(server_id: str, headers: dict, session: Session) -> str | None:
    r = session.post(
        f"https://disboard.org/site/get-invite/{server_id}", headers=headers
    )
    print(r.text)
    with open("code.html", "w", encoding="utf-8") as f:
        f.write(r.text)


def get_invite_info(code: str) -> dict:
    response = requests.get(
        f"https://discord.com/api/v9/invites/{code.replace('https://discord.gg/','')}?with_counts=true&with_expiration=true"
    )
    response.raise_for_status()
    return response.json()
