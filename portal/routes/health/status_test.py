

def test_get_health_status(client):
    res = client.get('/v1/health/status')
    assert res.status_code == 200
    assert res.json == {'result': 'Success'}
