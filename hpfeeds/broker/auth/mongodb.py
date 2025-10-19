import motor.motor_asyncio


class Authenticator(object):

    def __init__(self, host, port):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(host=host, port=port)

    def close(self):
        self.client.close()

    async def get_authkey(self, ident):
        res = await self.client.hpfeeds.auth_key.find_one({'identifier': ident})
        if not res:
            return None

        pubchans = res['publish']
        subchans = res['subscribe']
        ident = ident
        owner = res.get('owner', '')
        secret = res['secret']

        return dict(
            ident=ident,
            owner=owner,
            secret=secret,
            pubchans=pubchans,
            subchans=subchans
        )
