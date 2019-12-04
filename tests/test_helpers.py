import json

def test_site_activation(app, user_1_auth_tokens, site_props):
  ''' Ensure website activates '''
  with app.test_client() as client:
    client.post(
      '/create/register_site',
      data=json.dumps(dict(
        site_props=site_props
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    response = client.post(
      '/helper/site_config/site_activation',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    assert response.status_code == 200

def test_not_able_to_toggle_active(app, user_2_auth_tokens):
  ''' Ensure returns response if there is no website to toggle activation '''
  with app.test_client() as client:
    response = client.post(
      '/helper/site_config/site_activation',
      headers={'Authorization': 'Bearer ' + user_2_auth_tokens['access_token']}
    )
    assert response.status_code == 404

def test_site_deletion(app, user_1_auth_tokens):
  ''' Ensure site is deleted '''
  with app.test_client() as client:
    response = client.post(
      '/helper/delete_site',
      data=json.dumps(dict(
        domain='fareed'
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert 'Website deleted.' in data['message']

def test_site_not_deleted(app, user_2_auth_tokens):
  ''' Ensure website cannot be deleted if website does not exist '''
  with app.test_client() as client:
    response = client.post(
      '/helper/delete_site',
      data=json.dumps(dict(
        domain='fareedx'
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_2_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert 'Website could not be deleted. No Such website.' in data['message']