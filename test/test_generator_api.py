import pytest
from flask import Flask

import apis.generator_api as generator


@pytest.fixture()
def generator_client(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(generator.generator_api)

    monkeypatch.setattr(generator, "articles", [f"Article_{i}" for i in range(60)])
    monkeypatch.setattr(generator, "weights", [1 for _ in range(60)])
    monkeypatch.setattr(generator, "count", 60)

    with app.test_client() as client:
        yield client


def test_prompt_generator_caps_too_many_articles(generator_client):
    response = generator_client.get(
        "/api/generator/prompt?difficulty=60&num_articles=999"
    )

    assert response.status_code == 200
    assert len(response.get_json()) == generator.MAX_NUM_ARTICLES


def test_prompt_generator_rejects_invalid_numbers(generator_client):
    response = generator_client.get(
        "/api/generator/prompt?difficulty=banana&num_articles=1"
    )

    assert response.status_code == 400
    assert b"difficulty" in response.data
