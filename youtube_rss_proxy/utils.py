from urllib.parse import urlencode
import requests

from django.conf import settings


class OAuth(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.access_token  = access_token

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer {}".format(self.access_token)
        return r


def get_auth_url(state):
    return "https://accounts.google.com/o/oauth2/auth?{}".format(urlencode({
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "https://www.googleapis.com/auth/youtube",
        "response_type": "code",
        "access_type": "offline",
        "state": state,
    }))


def get_tokens(code):
    r = requests.post("https://accounts.google.com//o/oauth2/token", {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }).json()
    return r["access_token"], r.get("refresh_token", "")


def get_username(access_token):
    r = requests.get("https://gdata.youtube.com/feeds/api/users/default?alt=json", auth=OAuth(access_token))
    return r.json()["entry"]["yt$username"]["$t"]


def get_rss(username, access_token):
    r = requests.get("https://gdata.youtube.com/feeds/api/users/{}/newsubscriptionvideos".format(username), auth=OAuth(access_token))
    return r.text, r.headers["Content-Type"]
