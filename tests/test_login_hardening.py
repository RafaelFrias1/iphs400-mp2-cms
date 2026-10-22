"""S2: login hardening. A failed login never reveals which emails have accounts."""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient

from app.login_limiter import limiter
from conftest import DEMO_ACCOUNTS

ALERT = re.compile(r'<p role="alert">(.*?)</p>', re.S)


def login(c: TestClient, csrf, email: str, password: str):
    return c.post("/login", data={"email": email, "password": password,
                                  "csrf_token": csrf(c, "/login")},
                  follow_redirects=False)


def alert(response) -> str:
    match = ALERT.search(response.text)
    assert match, "the login page shows no error"
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


class FrozenClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_wrong_password_and_unknown_email_get_the_same_response(client, csrf):
    wrong_password = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"], "nope")
    unknown_email = login(client, csrf, "nobody@example.test", "nope")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert alert(wrong_password) == alert(unknown_email) == "Incorrect email or password."


def test_sixth_attempt_for_an_email_is_refused_even_with_the_right_password(client, csrf):
    limiter.clock = FrozenClock()
    email = DEMO_ACCOUNTS["editor"]["email"]
    for _ in range(5):
        assert login(client, csrf, email, "nope").status_code == 401

    refused = login(client, csrf, email, DEMO_ACCOUNTS["editor"]["password"])

    assert refused.status_code == 429
    assert alert(refused) == "Too many failed logins. Try again in 15 minutes."
    assert client.get("/admin", follow_redirects=False).status_code == 303


def test_login_works_again_once_15_minutes_have_passed(client, csrf):
    clock = limiter.clock = FrozenClock()
    email = DEMO_ACCOUNTS["editor"]["email"]
    for _ in range(5):
        login(client, csrf, email, "nope")

    clock.now += 14 * 60
    refused = login(client, csrf, email, DEMO_ACCOUNTS["editor"]["password"])
    assert refused.status_code == 429
    assert alert(refused) == "Too many failed logins. Try again in 1 minute."

    clock.now += 60
    response = login(client, csrf, email, DEMO_ACCOUNTS["editor"]["password"])
    assert response.status_code == 303
    assert client.get("/admin").status_code == 200


def test_another_email_can_still_log_in_from_the_same_client(client, csrf):
    for _ in range(5):
        login(client, csrf, DEMO_ACCOUNTS["editor"]["email"], "nope")

    response = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"],
                     DEMO_ACCOUNTS["admin"]["password"])

    assert response.status_code == 303
    assert client.get("/admin").status_code == 200


def test_a_successful_login_clears_that_emails_failures(client, csrf):
    email = DEMO_ACCOUNTS["editor"]["email"]
    for _ in range(4):
        login(client, csrf, email, "nope")
    assert login(client, csrf, email, DEMO_ACCOUNTS["editor"]["password"]).status_code == 303

    assert login(client, csrf, email, "nope").status_code == 401
    response = login(client, csrf, email, DEMO_ACCOUNTS["editor"]["password"])
    assert response.status_code == 303


def test_simultaneous_wrong_guesses_get_no_more_than_five_tries(client, csrf):
    email = DEMO_ACCOUNTS["editor"]["email"]
    token = csrf(client, "/login")
    start = Barrier(10)

    def guess(_):
        start.wait()
        return client.post("/login", data={"email": email, "password": "nope",
                                           "csrf_token": token},
                           follow_redirects=False).status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        statuses = list(pool.map(guess, range(10)))

    assert sorted(statuses) == [401] * 5 + [429] * 5


def test_a_wrong_password_for_another_email_still_gets_401_during_a_lockout(client, csrf):
    for _ in range(5):
        login(client, csrf, DEMO_ACCOUNTS["editor"]["email"], "nope")

    response = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"], "nope")

    assert response.status_code == 401
    assert alert(response) == "Incorrect email or password."
