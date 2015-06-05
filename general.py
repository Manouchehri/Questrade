import urllib.request
import gzip
import json
# import uuid
# import os

# These default headers are not used.
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-us',
           'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) '
                         'AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4'}


base_host = ["https://practicelogin.questrade.com", "https://login.questrade.com"]

API_ver = "v1/"


def grab(url):
    req = urllib.request.Request(url, headers=headers)
    # print(headers)
    try:
        response = urllib.request.urlopen(req)
        if response.info().get('Content-Encoding') == 'gzip':
            page_data = gzip.decompress(response.read())
        elif response.info().get('Content-Encoding') == 'deflate' or not response.info().get('Content-Encoding'):
            page_data = response.read()
        elif response.info().get('Content-Encoding'):
            raise ValueError('Encoding type unknown')
        return json.loads(page_data.decode('utf-8'))
    except urllib.error.HTTPError as err:
        print(err.code + " when fetching " + url)
        raise err


def get_tokens():
    auth_file = 'auth.json'
    with open(auth_file) as inf:
        global parsed
        parsed = json.load(inf)
    print("Loaded " + auth_file)

    try:
        global headers
        headers = {"Authorization": parsed['token_type'] + " " + parsed['access_token']}
        global API_URL
        API_URL = parsed['api_server'] + API_ver
        printJSON(grab(API_URL + "time"))
    except:
        print("Expired access token, creating new one...")
        refresh_url = "/oauth2/token?grant_type=refresh_token&refresh_token="
        data_reply = grab(base_host[0] + refresh_url + parsed['refresh_token'])
        if not data_reply:
            print("Expired refresh key.")
            print("Go to: " + base_host[0] + "/Signin.aspx?ReturnUrl=%2fAPIAccess%2fUserApps.aspx")
            data_reply = grab(base_host[0] + refresh_url + input("Please enter your new refresh key: "))

        if data_reply:
            with open(auth_file, 'w') as outf:
                json.dump(data_reply, outf)
            with open(auth_file) as inf:
                parsed = json.load(inf)
        else:
            raise ValueError("Failure to get tokens.")


def printJSON(dump):
    print(json.dumps(dump, indent=4, sort_keys=True))

get_tokens()

# For logging
# print(uuid.uuid4)
# print(os.uname())

accounts = grab(API_URL + "accounts")

account_number = accounts['accounts'][0]['number']

# print(account_number)

# printJSON(grab(API_URL + "accounts/" + account_number + "/balances"))
printJSON(grab(API_URL + "markets/quotes/38738"))