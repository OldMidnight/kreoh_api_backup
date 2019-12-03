import json

def test_register_website(app, user_1_auth_tokens, site_props):
  ''' Test site registration '''
  with app.test_client() as client:
    response = client.post(
      '/create/register_site',
      data=json.dumps(dict(
        site_props=site_props
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    assert response.status_code == 200

def test_reregister_website(app, user_1_auth_tokens, site_props):
  ''' Test that re-registering websites fails '''
  with app.test_client() as client:
    response = client.post(
      '/create/register_site',
      data=json.dumps(dict(
        site_props=site_props
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    assert response.status_code == 409

def test_update_website(app, user_1_auth_tokens, site_props):
  ''' Test that websites successfully updates '''
  with app.test_client() as client:
    response = client.post(
      '/create/update_site',
      data=json.dumps(dict(
        site_props=site_props
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    assert response.status_code == 200

def test_update_with_no_website(app, user_2_auth_tokens, site_props):
  ''' Test an update fails if there is no website for the user '''
  with app.test_client() as client:
    response = client.post(
      '/create/update_site',
      data=json.dumps(dict(
        site_props=site_props
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_2_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert 'There is no website to update.' in data['message']
