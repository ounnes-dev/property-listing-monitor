
import pytest
import requests

import collector


class FakeResponse:
    def __init__(self, result):
        self.result = result

    def raise_for_status(self):
        pass

    def json(self):
        return self.result


def make_search_response():
    return {
        "data": {
            "search": {
                "announcements": {
                    "data": [],
                    "paginatorInfo": {
                        "lastPage": 2,
                        "hasMorePages": True
                    }
                }
            }
        }
    }


def test_collection_stops_when_a_page_fails(monkeypatch):
    calls = 0

    def fake_post(*args, **kwargs):
        nonlocal calls
        calls += 1

        # Initial request and page 1 succeed.
        if calls <= 2:
            return FakeResponse(make_search_response())

        # Page 2 fails.
        raise requests.Timeout("Simulated timeout")

    monkeypatch.setattr(collector.requests, "post", fake_post)

    with pytest.raises(RuntimeError) as error:
        collector.collect_listings()

    assert calls == 3
