import pymongo


class Authenticator(object):

    def __init__(self, host, port):
        self.client = pymongo.MongoClient(host=host, port=port)

    def close(self):
        self.client.close()

    def get_authkey(self, ident):
        res = self.client.hpfeeds.auth_key.find_one({'identifier': ident})
        if not res:
            return None

        pubchans = res['publish']
        subchans = res['subscribe']
        ident = ident
        owner = res['owner']
        secret = res['secret']

        return dict(
            ident=ident,
            owner=owner,
            secret=secret,
            pubchans=pubchans,
            subchans=subchans
        )
