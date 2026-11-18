import logging
from unittest.mock import Mock, patch

import pytest
import requests


@pytest.mark.django_db
@patch("deezer.views.requests.get")
def test_get_album_tracks_success(mock_get, api_client, album):
    search_response = Mock()
    search_response.json.return_value = {"data": [{"id": 12345}]}
    search_response.raise_for_status.return_value = None

    tracks_response = Mock()
    tracks_response.json.return_value = {
        "data": [
            {
                "title": "Come Together",
                "duration": 259,
                "preview": "https://cdns-preview.dzcdn.net/test.mp3",
            }
        ]
    }
    tracks_response.raise_for_status.return_value = None

    mock_get.side_effect = [search_response, tracks_response]

    response = api_client.get(f"/api/albums/{album.id}/tracks/", format="json")

    assert response.status_code == 200
    assert response.data == [
        {
            "title": "Come Together",
            "duration": 259,
            "preview": "https://cdns-preview.dzcdn.net/test.mp3",
        }
    ]


@pytest.mark.django_db
@patch("deezer.views.requests.get")
def test_get_album_tracks_not_found_on_deezer(mock_get, api_client, album):
    search_response = Mock()
    search_response.json.return_value = {"data": []}
    search_response.raise_for_status.return_value = None
    mock_get.return_value = search_response

    response = api_client.get(f"/api/albums/{album.id}/tracks/", format="json")

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
@patch("deezer.views.requests.get")
def test_get_album_tracks_deezer_unavailable(mock_get, api_client, album, caplog):
    mock_get.side_effect = requests.RequestException("Connection error")

    with caplog.at_level(logging.ERROR, logger="deezer"):
        response = api_client.get(f"/api/albums/{album.id}/tracks/", format="json")

    assert response.status_code == 502
    assert "error" in response.data
    assert len(caplog.records) > 0


@pytest.mark.django_db
@patch("deezer.views.requests.get")
def test_get_album_tracks_album_not_found(mock_get, api_client):
    response = api_client.get("/api/albums/99999/tracks/", format="json")

    assert response.status_code == 404
    mock_get.assert_not_called()
