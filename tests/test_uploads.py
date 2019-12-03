import json
import os

def test_creates_screenshot(app, user_1_auth_tokens, site_props):
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
    response = client.get(
      '/uploads/screenshot/grab',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data['screenshot_saved'] is True
    assert os.path.exists(app.config['UPLOAD_FOLDER'] + 'fareed.kreoh.com.png')

def test_screenshot_if_no_website(app, user_2_auth_tokens):
  with app.test_client() as client:
    response = client.get(
      '/uploads/screenshot/grab',
      headers={'Authorization': 'Bearer ' + user_2_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert data['screenshot_saved'] is False
    assert 'No such Website.' in data['message']
    assert not os.path.exists(app.config['UPLOAD_FOLDER'] + 'fareedx.kreoh.com.png')

def test_screenshot_if_site_disabled(app, user_1_auth_tokens):
  with app.test_client() as client:
    response = client.post(
      '/helper/site_config/site_activation',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data['active'] is False
    response = client.get(
      '/uploads/screenshot/grab',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data['screenshot_saved'] is False
    assert 'Website Disabled.' in data['message']