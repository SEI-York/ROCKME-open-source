'''
Utility functions for using the Nowhere.it API
'''
import os
import requests


# class APIError(Exception):
#     pass


# def _cached(func):
#     '''
#     A simple caching decorator that ignores invocation failures.
#     - If an exception is raised, the cache is ignored and the next
#       call will raise the exception again.
#     '''
#     _cache = {'result': None}

#     def _inner():
#         key = _cache.get('result')
#         if key is not None:
#             return key

#         _cache['result'] = func()
#         return _cache['result']

#     return _inner


# @_cached
# def get_api_key():
#     '''
#     Find the Nowhere.it API key in the local environment or dev.env.
#     '''
#     # If the key is in the environment then return it
#     key = os.environ.get('API_KEY')
#     if key is not None:
#         return key

#     # Look for a `dev.env` file
#     path = os.path.realpath(__file__)
#     env_path = os.path.join(
#         os.path.dirname(os.path.dirname(path)), 'dev.env')

#     if not os.path.isfile(env_path):
#         raise APIError('Unable to locate dev.env file')

#     with open(env_path, 'r') as f:
#         for line in f:
#             if line.startswith('API_KEY'):
#                 # Split off the key and remove quotes and newline
#                 return line.split('=')[1].strip()[1:-1]

#     raise APIError('API_KEY not specified in dev.env')


# def get_user_list(api_key=None):
#     '''Fetch the current user list from Nowhere.it'''
#     if api_key is None:
#         api_key = get_api_key()

#     resp = requests.post(
#         'https://www.rockproject.eu/userlist.php',
#         data={'v': api_key}
#     )

#     if not resp.ok:
#         raise APIError('Unable to fetch details from Nowhere.it')

#     # Dicts of firstName, lastName, department, organization
#     return resp.json()


# def get_authenticated_user_details(user, password, api_key=None):
#     '''
#     Verify if a user is authenticated and return their details if they are.

#     The API returns JSON `{"verified": false}` for any error (incorrect key,
#     invalid user etc)

#     The payload on successful login is json object of:
#         verified
#         firstName
#         lastName
#         department
#         organization

#     NOTE: If users change their details this is going to be brittle...
#     '''
#     if api_key is None:
#         api_key = get_api_key()

#     resp = requests.post(
#         'https://www.rockproject.eu/authenticate.php',
#         data={
#             'v': api_key,
#             'user': user,
#             'pwd': password,
#         }
#     )

#     if not resp.ok:
#         raise APIError('Unable to fetch details from Nowhere.it')

#     return resp.json()
