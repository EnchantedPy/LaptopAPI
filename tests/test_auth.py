import pytest
from src.utils.logger import test_logger
from fastapi import status
from tests.conftest import http, get_cookies

# https://claude.ai/chat/ecb821c3-0879-4d31-8b81-83af4dd1e602


def test_auth_middleware(http, get_cookies):
    
    # 1. User registration
    res = http.post('/auth/register', json={
        'name': 'Danila',
        'username': 'ovrkill',
        'email': 'danila@example.com',
        'password': '123'
    })
    assert res.status_code == status.HTTP_200_OK
    assert res.json.get('status') == 'success'

    # 2. User login
    res = http.post('/auth/login/user', json={
        'username': 'ovrkill',
        'password': '123'
    })
    assert res.status_code == status.HTTP_200_OK
    assert res.json.get('status') == 'success'
    cookies = get_cookies()
    assert cookies.get('Bearer-token') is not None
    assert cookies.get('Refresh-token') is not None
    
	 # 3. User role test
    res = http.get('/auth/users/me')
    assert res.status_code == 200
    assert res.json.get('payload').get('role') == 'user'
    
    # 4. Authorizied registering (exp 403)
    exc = http.post('/auth/register', json={
        'name': 'Maxim',
        'username': 'odyssey',
        'email': 'maxim@example.com',
        'password': '321'
    }, raises=True)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    
    # 5. User logout
    res = http.post('/auth/logout')
    assert res.status_code == status.HTTP_200_OK
    cookies = get_cookies()
    assert len(cookies) == 0

    # 6. Admin login
    res = http.post('/auth/login/admin', json={
        'name': 'King',
        'password': 'apple',
        'admin_secret': 'qqq'
    })
    assert res.status_code == status.HTTP_200_OK
    cookies = get_cookies()
    assert cookies.get('Bearer-token') is not None
    assert cookies.get('Refresh-token') is not None
    
    # 7. Admin rights test
    res = http.get('/auth/admin/test')
    assert res.status_code == status.HTTP_200_OK
    assert res.json == {'msg': 'seems like you are admin'}
    
    # 8. Admin role test
    res = http.get('/auth/users/me')
    assert res.status_code == status.HTTP_200_OK
    assert res.json.get('payload').get('role') == 'admin'
    
    # 9. Admin authorizied register (exp 403)
    exc = http.post('/auth/register', json={
        'name': 'Poma',
        'username': 'redokn',
        'email': 'poma@example.com',
        'password': '12345'
    }, raises=True)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    
    # 10. Admin authorizied trying to login as user (exp 403)
    exc = http.post('/auth/login/user', json={
        'username': 'ovrkill',
        'password': '123'
    }, raises=True)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    
    # 11. Admin authorizied trying to login as admin (exp 403)
    exc = http.post('/auth/login/admin', json={
        'name': 'King',
        'password': 'apple',
        'admin_secret': 'qqq'
    }, raises=True)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    
    # 12. Admin logout
    res = http.post('/auth/logout')
    assert res.status_code == status.HTTP_200_OK

    # 13. Not authorizied logout (exp 401)
    exc = http.post('/auth/logout', raises=True)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 14. Unathorizied profile get (exp 401)
    exc = http.get('/auth/users/me', raises=True)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 15. Unathorizied admin rights get (exp 401)
    exc = http.get('/auth/admin/test', raises=True)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 16. Register user with same username
    res = http.post('auth/register', json={
        'name': 'Poma',
        'username': 'ovrkill',
        'email': 'secondpoma@example.com',
        'password': 'secret'
    })
    assert res.status_code != 200
    