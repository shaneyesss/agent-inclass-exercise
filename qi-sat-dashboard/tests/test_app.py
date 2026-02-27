import os
import sys
import pytest
from flask import redirect

# ensure the application directory is on sys.path so imports below work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import the modules directly; the parent folder has a hyphen so it cannot be
# treated as a normal Python package name.
import app
import store

# expose them in the names used by the rest of the tests
app = app.app
store = store


@pytest.fixture
def client():
    app.config['TESTING'] = True
    # clear store before each test
    store.submissions.clear()
    with app.test_client() as client:
        yield client


def test_get_rate(client):
    rv = client.get('/rate')
    assert rv.status_code == 200
    assert b'name="visit_date"' in rv.data
    assert b'name="nurse"' in rv.data
    assert b'name="physician"' in rv.data
    # ensure the page includes a View Dashboard link/button
    assert b'href=\"/dashboard\"' in rv.data


def test_post_valid(client):
    data = {
        'visit_date': '2026-02-27',
        'nurse': '4',
        'physician': '5'
    }
    rv = client.post('/rate', data=data, follow_redirects=False)
    # should redirect back to the form with success flag so multiple
    # submissions can be made before viewing the dashboard
    assert rv.status_code == 302
    assert '/rate?success=1' in rv.headers['Location']
    assert len(store.submissions) == 1


def test_post_invalid(client):
    # missing date
    rv = client.post('/rate', data={'visit_date': '', 'nurse': '3', 'physician': '3'})
    # should redirect back to form with error
    assert rv.status_code == 302
    assert '/rate?error=' in rv.headers['Location']
    assert len(store.submissions) == 0

    # invalid rating
    rv = client.post('/rate', data={'visit_date': '2026-02-27', 'nurse': '0', 'physician': '6'})
    assert rv.status_code == 302
    assert len(store.submissions) == 0


def test_dashboard_content(client):
    # populate store
    store.add_submission('2026-02-26', 3, 4)
    store.add_submission('2026-02-27', 5, 2)
    rv = client.get('/dashboard')
    assert rv.status_code == 200
    data = rv.data.decode('utf-8')
    assert 'canvas' in data
    assert 'chart.js' in data.lower()
    # the JSON-encoded labels list should include both dates; exact formatting
    # may vary so just check for each date string individually.
    assert '"2026-02-26"' in data
    assert '"2026-02-27"' in data


def test_root_redirects_to_rate(client):
    rv = client.get('/', follow_redirects=False)
    assert rv.status_code in (301, 302)
    assert '/rate' in rv.headers['Location']
