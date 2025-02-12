from datetime import date
import pytest
from fastapi import status
from src.conf import messages

test_contact = {
    "first_name": "firstname",
    "last_name": "lastname",
    "email": "test@example.com",
    "phone_number": "1298765423",
    "birthday": str(date(2010, 12, 12)),
    "additional_data": "additional data",
}


@pytest.fixture(scope="module")
def create_contact(client, get_token):
    """Create a test contact and return its ID."""
    response = client.post(
        "/api/contacts",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_get_contact(client, get_token, create_contact):
    contact_id = create_contact
    response = client.get(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert "id" in data
    assert data["id"] == contact_id


def test_get_contact(client, get_token, create_contact):
    contact_id = create_contact

    response = client.get(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert "id" in data
    assert data["id"] == contact_id


def test_get_contact_not_found(client, get_token):
    non_existent_id = 99999
    response = client.get(
        f"/api/contacts/{non_existent_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_get_contacts(client, get_token, create_contact):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(contact["id"] == create_contact for contact in data)


def test_update_contact(client, get_token, create_contact):
    contact_id = create_contact
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "New_name"

    response = client.put(
        f"/api/contacts/{contact_id}",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["first_name"] == updated_test_contact["first_name"]
    assert "id" in data
    assert data["id"] == contact_id


def test_update_contact_not_found(client, get_token):
    non_existent_id = 99999
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "New_name"

    response = client.put(
        f"/api/contacts/{non_existent_id}",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact(client, get_token, create_contact):
    contact_id = create_contact

    response = client.delete(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    response = client.get(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_repeat_delete_contact(client, get_token):
    """Try to delete a non-existent contact."""
    response = client.delete(
        "/api/contacts/99999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND
