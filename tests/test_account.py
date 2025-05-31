from tests.conftest import http, user
from fastapi import status

def test_account(http, user):
	res = http.post('/auth/register', json=user)
	assert res.status_code == status.HTTP_200_OK

	res = http.post('/auth/login/user', json={
        'username': 'oovrkill',
        'password': '123'
    })
	assert res.status_code == status.HTTP_200_OK

	res = http.get('/account/self')
	assert res.status_code == status.HTTP_200_OK
	assert res.json.get('username') == 'oovrkill'

	res = http.patch('/account/self/update', json={
		'name': 'Puma'
	})
	assert res.status_code == 200

	res = http.patch('/account/self/update', json={
		'name': 'Puma',
		'submit_password': '123'
	})
	assert res.status_code != 200

	res = http.patch('/account/self/update', json={
		'email': 'puma@example.com'
	})
	assert res.status_code != 200

	res = http.patch('/account/self/update', json={
		'email': 'puma@example.com',
		'submit_password': '123'
	})
	assert res.status_code == 200

	res = http.patch('/account/self/update', json={
		'password': 'new_pass',
		'submit_password': '123'
	})
	assert res.status_code != 200

	res = http.patch('/account/self/update', json={
		'password': 'new_pass',
		'repeat_password': 'new_pass'
	})
	assert res.status_code != 200

	res = http.patch('/account/self/update', json={
		'repeat_password': 'new_pass'
	})
	assert res.status_code != 200

	res = http.patch('/account/self/update', json={
		'password': 'new_pass',
		'repeat_password': 'new_pass',
		'submit_password': '123'
	})
	assert res.status_code == 200