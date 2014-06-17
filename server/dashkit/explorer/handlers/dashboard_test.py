"""Tests for data handlers in the Dashkit Explorer application."""

__author__ = 'joemu@google.com (Joe Allan Muharsky)'


import json
import os
import pytest
import webtest
import unittest

from google.appengine.api import users
from google.appengine.ext import testbed

from . import dashboard
from ..model import dashboard as dashboard_model

DEFAULT_USERS = [{'id': '1', 'email': 'test01@mydomain.com'},
                 {'id': '2', 'email': 'newowner@mydomain.com'}]


class DashboardTest(unittest.TestCase):

  def setUp(self):
    super(DashboardTest, self).setUp()

    self.app = webtest.TestApp(dashboard.app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_user_stub()

    os.environ['USER_EMAIL'] = DEFAULT_USERS[0]['email']
    os.environ['USER_ID'] = DEFAULT_USERS[0]['id']
    dashboard_model.DEFAULT_DOMAIN = 'mydomain.com'

    DashboardTest.original_getDashboardOwner = (
        dashboard_model.Dashboard.GetDashboardOwner)
    dashboard_model.Dashboard.GetDashboardOwner = (
        DashboardTest.mockGetDashboardOwner)

  @classmethod
  def mockGetDashboardOwner(cls, owner_string):
    if owner_string:
      owner_email = dashboard_model.Dashboard.GetCanonicalEmail(
          owner_string)
    else:
      owner_email = DEFAULT_USERS[0]['email']

    try:
      next(
          obj for (index, obj) in
          enumerate(DEFAULT_USERS) if obj['email'] == owner_email)
      return users.User(owner_email)
    except StopIteration:
      raise users.UserNotFoundError()

  def tearDown(self):
    dashboard_model.Dashboard.GetDashboardOwner = (
        DashboardTest.original_getDashboardOwner)
    self.testbed.deactivate()

  def testViewDashboard(self):
    provided_data = '{"title": "foo"}'
    expected_data = {'title': 'foo'}

    dashboard_id = dashboard_model.Dashboard(data=provided_data).put().id()
    resp = self.app.get(url='/dashboard/view',
                        params=[('id', dashboard_id)])
    self.assertDictEqual(resp.json, expected_data)

  def testDeleteDashboard(self):
    original_data = '{"title": "foo"}'

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=original_data).put().id()

    self.app.post(url='/dashboard/delete',
                  status=200,
                  params=[('id', dashboard_id)])
    stored_dashboard = dashboard_model.Dashboard.get_by_id(dashboard_id)
    self.assertIsNone(stored_dashboard)

  def testCreateDashboard(self):
    provided_data = '{"title": "foo"}'
    expected_response = {'id': '1', 'title': 'foo',
                         'owner': DEFAULT_USERS[0]['email']}

    resp = self.app.post(url='/dashboard/create',
                         params=[('data', provided_data)])
    self.assertDictEqual(resp.json, expected_response)

  def testCopyDashboard(self):
    provided_data = '{{"title": "foo", "owner": "{owner:}"}}'.format(
        owner=DEFAULT_USERS[0]['email'])

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=provided_data).put().id()

    resp = self.app.post(url='/dashboard/copy',
                         params=[('id', dashboard_id)])
    new_id = resp.json['id']
    expected_response = {'id': new_id}

    self.assertNotEqual(new_id, dashboard_id)
    self.assertDictEqual(resp.json, expected_response)

  def testCopyAndRenameDashboard(self):
    provided_data = '{{"title": "foo", "owner": "{owner:}"}}'.format(
        owner=DEFAULT_USERS[0]['email'])
    new_title = 'bar'

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=provided_data).put().id()

    resp = self.app.post(url='/dashboard/copy',
                         params=[('id', dashboard_id),
                                 ('title', new_title)])
    new_id = resp.json['id']
    expected_response = {'id': new_id}

    self.assertNotEqual(new_id, dashboard_id)
    self.assertDictEqual(resp.json, expected_response)

  def testGetUserEmailFromOwner(self):
    expected_email = 'test01@mydomain.com'
    actual_user = dashboard_model.UserValidator.GetUserFromEmail(
        'test01@mydomain.com')
    self.assertEquals(actual_user.email(), expected_email)

  def testGetCanonicalEmail(self):
    expected_email = 'test01@mydomain.com'
    actual_email = dashboard_model.Dashboard.GetCanonicalEmail('test01')
    self.assertEquals(actual_email, expected_email)

  @pytest.mark.testing
  def testEditDashboard(self):
    original_data = '{"title": "foo"}'

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=original_data).put().id()

    updated_data = ('{{"id": {id:}, "title": "bar", '
                    '"owner": "{owner}"}}').format(
                        id=dashboard_id, owner=DEFAULT_USERS[0]['email'])
    self.app.post(url='/dashboard/edit',
                  status=200,
                  params=[('id', dashboard_id),
                          ('data', updated_data)])
    stored_dashboard = dashboard_model.Dashboard.get_by_id(dashboard_id)
    self.assertEqual(stored_dashboard.data, updated_data)

  def testEditDashboardOwner(self):
    original_data = '{"title": "untitled"}'
    new_owner = 'newowner@mydomain.com'

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=original_data).put().id()
    updated_data = (
        '{{"title": "untitled", "owner": "{owner:}"}}').format(owner=new_owner)
    self.app.post(url='/dashboard/edit-owner',
                  status=200,
                  params=[('id', dashboard_id),
                          ('email', new_owner)])
    stored_dashboard = dashboard_model.Dashboard.get_by_id(dashboard_id)
    self.assertEqual(stored_dashboard.data, updated_data)

  def testEditDashboardOwnerWithoutDomain(self):
    nodomain_owner = 'newowner'
    new_owner = 'newowner@mydomain.com'

    original_data = '{{"title": "untitled", "owner": "{owner:}"}}'.format(
        owner=nodomain_owner)
    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=original_data).put().id()
    expected_data = (
        '{{"title": "untitled", "owner": "{owner:}"}}').format(
            owner=new_owner)

    self.app.post(url='/dashboard/edit-owner',
                  status=200,
                  params=[('id', dashboard_id),
                          ('email', nodomain_owner)])
    stored_dashboard = dashboard_model.Dashboard.get_by_id(dashboard_id)
    self.assertEqual(stored_dashboard.data, expected_data)

  def testEditDashboardInvalidOwner(self):
    original_data = '{"title": "untitled"}'
    provided_owner_email = 'invalid_user@mydomain.com'
    actual_owner_email = DEFAULT_USERS[0]['email']

    dashboard_id = dashboard_model.Dashboard(
        created_by=users.get_current_user(),
        data=original_data).put().id()
    updated_data = json.dumps({
        'id': dashboard_id,
        'title': 'untitled',
        'owner': provided_owner_email})

    expected_warning = (
        'The user {provided_email:} does not exist.  '
        'Owner set to {owner_email:}.'.format(
            provided_email=provided_owner_email,
            owner_email=actual_owner_email))
    expected_response = {
        'id': dashboard_id,
        'title': 'untitled',
        'owner': actual_owner_email,
        'warnings': [expected_warning]}

    response = self.app.post(url='/dashboard/edit',
                             status=200,
                             params=[('id', dashboard_id),
                                     ('data', updated_data)])
    self.assertIsNotNone(response.json)
    self.assertDictEqual(expected_response, response.json)

    stored_dashboard = dashboard_model.Dashboard.get_by_id(dashboard_id)
    self.assertEqual(stored_dashboard.data, json.dumps(expected_response))

  def testViewDashboardMissingParameters(self):
    expected_response = {'message': 'The "id" parameter is required.'}

    resp = self.app.get(url='/dashboard/view', status=400)
    self.assertEqual(resp.json, expected_response)

  def testCreateDashboardMissingParameters(self):
    expected_response = {'message': 'The "data" parameter is required.'}

    resp = self.app.post(url='/dashboard/create', status=400)
    self.assertEqual(resp.json, expected_response)

  def testEditDashboardMissingParameters(self):
    expected_response_id = {'message': 'The "id" parameter is required.'}
    expected_response_data = {'message': 'The "data" parameter is required.'}

    resp = self.app.post(url='/dashboard/edit', status=400)
    self.assertEqual(resp.json, expected_response_id)

    resp = self.app.post(url='/dashboard/edit',
                         status=400,
                         params=[('id', 1)])
    self.assertEqual(resp.json, expected_response_data)

  def testViewDashboardInvalidParameters(self):
    expected_response = {'message': ('The "id" parameter must be an integer.  '
                                     'Found "invalid".')}

    resp = self.app.get(url='/dashboard/view',
                        status=400,
                        params=[('id', 'invalid')])
    self.assertEqual(resp.json, expected_response)

  def testCreateDashboardInvalidParameters(self):
    message = 'The "data" parameter must be valid JSON.  Found:\ninvalid'
    expected_response = {'message': message}

    resp = self.app.post(url='/dashboard/create',
                         status=400,
                         params=[('data', 'invalid')])
    self.assertEqual(resp.json, expected_response)

  def testEditDashboardInvalidParameters(self):
    message = 'The "id" parameter must be an integer.  Found "invalid".'
    expected_response = {'message': message}

    resp = self.app.post(url='/dashboard/edit',
                         status=400,
                         params=[('id', 'invalid'),
                                 ('data', {'data': 'valid'})])
    self.assertEqual(resp.json, expected_response)

    message = 'The "data" parameter must be valid JSON.  Found:\ninvalid'
    expected_response = {'message': message}

    resp = self.app.post(url='/dashboard/edit',
                         status=400,
                         params=[('id', 1),
                                 ('data', 'invalid')])
    self.assertEqual(resp.json, expected_response)

  def testViewDashboardMissingId(self):
    expected_response = {'message': 'No dashboard with ID 1 was found.'}

    resp = self.app.get(url='/dashboard/view',
                        status=400,
                        params=[('id', 1)])
    self.assertEqual(resp.json, expected_response)

  def testEditDashboardMissingId(self):
    expected_response = {'message': 'No dashboard with ID 1 was found.'}

    resp = self.app.post(url='/dashboard/edit',
                         status=400,
                         params=[('id', 1),
                                 ('data', '{"foo": "bar"}')])
    self.assertEqual(resp.json, expected_response)

  def testViewDashboardInvalidData(self):
    provided_data = 'INVALID'
    message = ('The "data" field in dashboard row 1 must be valid JSON.  '
               'Found:\nINVALID')
    expected_reponse = {'message': message}

    dashboard_id = dashboard_model.Dashboard(data=provided_data).put().id()
    resp = self.app.get(url='/dashboard/view',
                        status=400,
                        params=[('id', dashboard_id)])
    self.assertDictEqual(resp.json, expected_reponse)


if __name__ == '__main__':
  unittest.main()