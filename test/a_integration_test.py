from flask import url_for
from flask.testing import FlaskClient
import models


def test_create_read():  # pragma: no cover
    models.Club().get_or_create(name="test",
                                email="test@test.com",
                                points=20)
    models.Competition().get_or_create(name="test",
                                       date="2021-01-01",
                                       numberOfPlaces=20)
    assert (models.Club()
            .select()
            .where(models.Club.name == "test")
            .count() == 1)


def test_summary_get(client: FlaskClient):  # pragma: no cover
    assert client.get(url_for("index")).status_code == 200


def test_points_display(client: FlaskClient):  # pragma: no cover
    assert client.get(url_for("pointsDisplay")).status_code == 200


def test_summary_post(client: FlaskClient):  # pragma: no cover
    request = client.post(url_for("summary"),
                          data=dict(email="test@test.com"))
    code = request.status_code
    is_logged_in = ("Set-Cookie" in request.headers and
                    "authentication" in request.headers["Set-Cookie"])
    assert code == 200 and is_logged_in


def test_booking_page(client: FlaskClient):  # pragma: no cover
    assert client.get("/book/test/test").status_code == 302


def test_booking(client: FlaskClient):  # pragma: no cover
    request = client.post(url_for("purchasePlaces"),
                          data=dict(club="test",
                                    competition="test",
                                    places=10))
    assert request.status_code == 302
    assert (models.Participation()
            .select()
            .where(models.Participation.club == "test")
            .count() == 1)


def test_logout(client: FlaskClient):  # pragma: no cover
    request = client.get(url_for("logout"))
    code = request.status_code
    is_logged_out = "Set-Cookie" in request.headers
    assert code == 200 and is_logged_out
