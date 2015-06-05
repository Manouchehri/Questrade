import urllib.request
import gzip
import json

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-us',
           'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) '
                         'AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4'}


baseHost = ["https://practicelogin.questrade.com", "https://login.questrade.com"]

API_ver = "v1/"

# https://practicelogin.questrade.com/Signin.aspx?ReturnUrl=%2fAPIAccess%2fUserApps.aspx

def grab(url, headers=headers):
    req = urllib.request.Request(url, headers=headers)
    print(headers)
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
        print("Something went wrong.")
        print(err.code)
        raise err


def get_tokens():

    with open('auth.json') as inf:
        parsed = json.load(inf)
    printJSON(parsed)

    try:
        headers = {"Authorization": parsed['token_type'] + " " + parsed['access_token']}
        temp_data = grab(parsed['api_server'] + API_ver + "time", headers)
        print(temp_data)
    except:
        print("oops")
        refresh_url = "/oauth2/token?grant_type=refresh_token&refresh_token="
        data_reply = grab(baseHost[0] + refresh_url + parsed['refresh_token'])
        if not data_reply:
            print("Go to: " + baseHost[0] + "/Signin.aspx?ReturnUrl=%2fAPIAccess%2fUserApps.aspx")
            data_reply = grab(baseHost[0] + refresh_url + input("Please enter your refresh key: "))

        if data_reply:
            with open('auth.json', 'w') as outf:
                json.dump(data_reply, outf)
                parsed = json.load(outf)
        else:
            raise ValueError("Failure to get tokens.")

    return {"Authorization": parsed['token_type'] + " " + parsed['access_token']}, parsed['api_server']

def printJSON(dump):
    print(json.dumps(dump, indent=4, sort_keys=True))


headers, API_server = get_tokens()

API_URL = API_server + API_ver

print(grab(API_URL + "time", headers))  # I want to avoid typing the second headers.