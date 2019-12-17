import json

def login(client, email, password):
  return client.post(
    '/auth/login',
    data=json.dumps(dict(
      email=email,
      password=password
    )),
    content_type='application/json'
  )

def register(client, f_name, s_name, email, password, domain):
  return client.post(
    '/auth/register',
    data=json.dumps(dict(
      f_name=f_name,
      s_name=s_name,
      email=email,
      password=password,
      domain=domain
    )),
    content_type='application/json'
  )

def test_config(app):
  ''' Test correct config applied '''
  assert app.config['TESTING'] is True

def test_add_user(app):
  ''' ensure a new user can be added '''
  with app.test_client() as client:
    response = register(client, 'fareed', 'idris', app.config['EMAIL'], app.config['PASSWORD'], 'fareed')
    data = json.loads(response.data.decode())
    assert response.status_code == 201
    assert 'fareedidris20@gmail.com user created.' in data['message']
    response = register(client, 'fareed', 'idris', app.config['EMAIL'] + 'x', app.config['PASSWORD'], 'fareedx')
    data = json.loads(response.data.decode())
    assert response.status_code == 201
    assert 'fareedidris20@gmail.comx user created.' in data['message']

def test_not_add_user(app):
  ''' Ensure user cannot be added with wrong inputs '''
  with app.test_client() as client:
    response = client.post(
      '/auth/register',
      data=json.dumps(dict(
        f_name='%$!@21`33',
        s_name='$!@3123"123',
        email='fareed',
        password='1',
        domain="/////!!53245/"
      )),
      content_type='application/json'
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 406
    assert 'fareed user created.' not in data['message']

def test_login(app, user_1_auth_tokens, user_2_auth_tokens):
  ''' Test App login function'''
  with app.test_client() as client:
    response = login(client, app.config['EMAIL'], app.config['PASSWORD'])
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    user_1_auth_tokens['access_token'] = data['access_token']
    response = login(client, app.config['EMAIL'] + 'x', app.config['PASSWORD'])
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    user_2_auth_tokens['access_token'] = data['access_token']


def test_not_login(app):
  ''' Test app does not login '''
  with app.test_client() as client:
    response = login(client, app.config['EMAIL'] + 'x', app.config['PASSWORD'] + 'x')
    data = json.loads(response.data.decode())
    assert response.status_code == 401
    assert 'Invalid Email or Password.' in data['message']

def test_get_user(app, user_1_auth_tokens):
  with app.test_client() as client:
    response = client.get(
      '/auth/user',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    assert response.status_code == 200

def test_not_get_user(app, user_1_auth_tokens):
  with app.test_client() as client:
    response = client.get(
      '/auth/user',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token'] + 'x'}
    )
    assert response.status_code == 422