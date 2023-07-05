import time
import requests


class StackOverflowClient:
    BASE_URL = 'https://api.stackexchange.com/2.2/questions'
    PAGE_SIZE = 100
    MAX_PAGES = 5

    def __init__(self, tags, access_token, key):
        self.tags = tags
        self.ac_token = access_token
        self.ac_key = key

    def fetch_questions(self, page, tag):
        try:
            params = {
                'site': 'stackoverflow',
                'tagged': tag,
                'sort': 'creation',
                'key': self.ac_key,
                'access_token': self.ac_token,
                'page': page,
                'pagesize': self.PAGE_SIZE,
                'order': 'desc',
                'filter': 'withbody'
            }

            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()  # raise an exception for HTTP errors

            return response.json()
        except:
            pass

    def fetch_all_questions(self):
        for tag in self.tags:
            try:
                for page in range(1, self.MAX_PAGES + 1):
                    data = self.fetch_questions(page, tag)
                    if 'items' in data:
                        yield data['items']
                        if not data['has_more']:
                            break
                    # Check remaining quota and pause if it's low
                    if 'quota_remaining' in data and data['quota_remaining'] < 10:
                        print('Quota remaining is low. Sleeping for 10 seconds...')
                        time.sleep(10)
                    time.sleep(1)
            except (ValueError, KeyError, Exception) as ex:
                print(f"Something happened: {ex}")
                continue
