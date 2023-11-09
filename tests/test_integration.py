import json
import pytest


def call(client, path, method='GET', body=None):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PUT':
        response = client.put(path, data=json.dumps(body), headers=headers)
    elif method == 'PATCH':
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == 'DELETE':
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode('utf-8')),
        "code": response.status_code
    }


@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


@pytest.mark.dependency()
def test_get_all(client):
    result = call(client, 'posts')
    assert result['code'] == 200
    assert result['json']['data']['posts'] == [
        {
            "coordinate_lat": "91.54789",
            "coordinate_long": "21.67890",
            "datefrom": "Mon, 18 Sep 2023 14:00:00 GMT",
            "dateposted": "Mon, 18 Sep 2023 12:00:00 GMT",
            "dateto": "Mon, 18 Sep 2023 18:00:00 GMT",
            "description": "Skewered, grilled chicken marinated in aromatic spices",
            "foodtype": "Normal",
            "location": "80 Stamford Rd, Singapore 178902",
            "post_id": 1,
            "title": "Chicken Satay",
            "verified": True
        },
        {
            "coordinate_lat": "103.755760",
            "coordinate_long": "1.290210",
            "datefrom": "Tue, 19 Sep 2023 16:00:00 GMT",
            "dateposted": "Tue, 19 Sep 2023 15:00:00 GMT",
            "dateto": "Tue, 19 Sep 2023 18:00:00 GMT",
            "description": "Leftover baked ziti with marinara sauce and vegetables. Can be reheated.",
            "foodtype": "Vegetarian",
            "location": "50 Jurong Gateway Rd, Singapore 608549",
            "post_id": 2,
            "title": "Vegetarian Pasta",
            "verified": True
        }
    ]


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    result = call(client, 'posts/2')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "coordinate_lat": "103.755760",
        "coordinate_long": "1.290210",
        "datefrom": "Tue, 19 Sep 2023 16:00:00 GMT",
        "dateposted": "Tue, 19 Sep 2023 15:00:00 GMT",
        "dateto": "Tue, 19 Sep 2023 18:00:00 GMT",
        "description": "Leftover baked ziti with marinara sauce and vegetables. Can be reheated.",
        "foodtype": "Vegetarian",
        "location": "50 Jurong Gateway Rd, Singapore 608549",
        "post_id": 2,
        "title": "Vegetarian Pasta",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    result = call(client, 'posts/55')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Post not found."
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_replace_existing_post(client):
    result = call(client, 'posts/2', 'PUT', {
        "coordinate_lat": "100.234",
        "coordinate_long": "1.2232",
        "datefrom": "2023-09-18 12:00:00",
        "dateposted": "2023-09-18 12:00:00",
        "dateto": "2023-09-18 12:00:00",
        "description": "Leftover baked ziti with marinara sauce and vegetables. Can be reheated.",
        "foodtype": "Vegetarian",
        "location": "50 Jurong Gateway Rd, Singapore 608549",
        "title": "Vegetarian Pasta",
        "verified": True
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "coordinate_lat": "100.234",
        "coordinate_long": "1.2232",
        "datefrom": "Mon, 18 Sep 2023 12:00:00 GMT",
        "dateposted": "Mon, 18 Sep 2023 12:00:00 GMT",
        "dateto": "Mon, 18 Sep 2023 12:00:00 GMT",
        "description": "Leftover baked ziti with marinara sauce and vegetables. Can be reheated.",
        "foodtype": "Vegetarian",
        "location": "50 Jurong Gateway Rd, Singapore 608549",
        "post_id": 2,
        "title": "Vegetarian Pasta",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_post(client):
    result = call(client, 'posts/2', 'PATCH', {
        "coordinate_lat": "100.965764",
        "coordinate_long": "1.22322321"
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "coordinate_lat": "100.965764",
        "coordinate_long": "1.22322321",
        "datefrom": "Tue, 19 Sep 2023 16:00:00 GMT",
        "dateposted": "Tue, 19 Sep 2023 15:00:00 GMT",
        "dateto": "Tue, 19 Sep 2023 18:00:00 GMT",
        "description": "Leftover baked ziti with marinara sauce and vegetables. Can be reheated.",
        "foodtype": "Vegetarian",
        "location": "50 Jurong Gateway Rd, Singapore 608549",
        "post_id": 2,
        "title": "Vegetarian Pasta",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    result = call(client, 'posts', 'POST', {})
    assert result['code'] == 500


@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_post(client):
    result = call(client, 'posts', 'POST', {
        "coordinate_lat": "1.340370",
        "coordinate_long": "103.932050",
        "datefrom": "2023-09-20 18:00:00",
        "dateposted": "2023-09-20 19:00:00",
        "dateto": "2023-09-20 21:00:00",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "title": "Leftover Biryani",
        "verified": True
    })
    assert result['code'] == 201
    assert result['json']['data'] == {
        "coordinate_lat": "1.340370",
        "coordinate_long": "103.932050",
        "datefrom": "Wed, 20 Sep 2023 18:00:00 GMT",
        "dateposted": "Wed, 20 Sep 2023 19:00:00 GMT",
        "dateto": "Wed, 20 Sep 2023 21:00:00 GMT",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "post_id": 28,
        "title": "Leftover Biryani",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_create_one_post'])
def test_replace_new_post(client):
    call(client, 'posts', 'POST', {
        "coordinate_lat": "1.340370",
        "coordinate_long": "103.932050",
        "datefrom": "2023-09-20 18:00:00",
        "dateposted": "2023-09-20 19:00:00",
        "dateto": "2023-09-20 21:00:00",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "title": "Leftover Biryani",
        "verified": True
    })
    result = call(client, 'posts/28', 'PUT', {
        "coordinate_lat": "2.14342",
        "coordinate_long": "103.932050",
        "datefrom": "2023-09-20 18:00:00",
        "dateposted": "2023-09-20 19:00:00",
        "dateto": "2023-09-20 21:00:00",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "title": "Leftover Biryani",
        "verified": True
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "coordinate_lat": "2.14342",
        "coordinate_long": "103.932050",
        "datefrom": "Wed, 20 Sep 2023 18:00:00 GMT",
        "dateposted": "Wed, 20 Sep 2023 19:00:00 GMT",
        "dateto": "Wed, 20 Sep 2023 21:00:00 GMT",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "post_id": 28,
        "title": "Leftover Biryani",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_create_one_post'])
def test_update_new_post(client):
    call(client, 'posts', 'POST', {
        "coordinate_lat": "1.340370",
        "coordinate_long": "103.932050",
        "datefrom": "2023-09-20 18:00:00",
        "dateposted": "2023-09-20 19:00:00",
        "dateto": "2023-09-20 21:00:00",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "title": "Leftover Biryani",
        "verified": True
    })
    result = call(client, 'posts/28', 'PATCH', {
        "coordinate_lat": "1.34354323",
        "coordinate_long": "103.933432",
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "coordinate_lat": "1.34354323",
        "coordinate_long": "103.933432",
        "datefrom": "Wed, 20 Sep 2023 18:00:00 GMT",
        "dateposted": "Wed, 20 Sep 2023 19:00:00 GMT",
        "dateto": "Wed, 20 Sep 2023 21:00:00 GMT",
        "description": "Vegetable biryani made with fragrant basmati rice and spices.",
        "foodtype": "Vegetarian",
        "location": "21 Sengkang East Way, Singapore 79765",
        "post_id": 28,
        "title": "Leftover Biryani",
        "verified": True
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_delete_post(client):
    result = call(client, 'posts/2', 'DELETE')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "post_id": 2
    }


@pytest.mark.dependency(depends=['test_delete_post'])
def test_deleted_post(client):
    call(client, 'posts/2', 'DELETE')
    result = call(client, 'posts/2', 'GET')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Post not found."
    }
