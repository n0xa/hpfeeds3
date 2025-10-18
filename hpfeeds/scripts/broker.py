import argparse
import asyncio
import logging
import ssl
import sys

import aiorun

from hpfeeds.broker.auth import env, sqlite, mongodb
from hpfeeds.broker.server import Server


def custom_exception_handler(loop, context):
    """
    Custom exception handler to suppress noisy asyncio socket warnings.
    These exceptions are expected when clients disconnect abruptly.
    """
    exception = context.get('exception')

    # Suppress common disconnect errors
    if exception and isinstance(exception, (BrokenPipeError, ConnectionResetError, OSError)):
        # Only log at debug level - connection_lost will handle cleanup
        logging.debug(f"Socket error (expected on disconnect): {context.get('message', 'N/A')}")
        return

    # For other exceptions, use the default handler
    loop.default_exception_handler(context)


def main():
    parser = argparse.ArgumentParser(description='Run a hpfeeds broker')
    parser.add_argument('--bind', default='0.0.0.0:20000', action='store')
    parser.add_argument('--exporter', default='', action='store')
    parser.add_argument('--name', default='hpfeeds', action='store')
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--auth', default='mongodb', action='store')
    parser.add_argument('--mongo_host', default="mongodb", action='store')
    parser.add_argument('--mongo_port', default=27017, action='store')
    parser.add_argument('--tlscert', default=None, action='store')
    parser.add_argument('--tlskey', default=None, action='store')
    args = parser.parse_args()

    if (args.tlscert and not args.tlskey) or (args.tlskey and not args.tlscert):
        parser.error('Must specify --tlskey AND --tlscert')
        return

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
    )

    # Suppress asyncio's noisy socket warnings for expected disconnect scenarios
    # These are normal when clients disconnect abruptly
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.ERROR)

    # Set custom exception handler for asyncio event loop
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_exception_handler)

    if args.auth == 'mongodb':
        logging.info("Opening connection to MongoDB at %s:%s", args.mongo_host, args.mongo_port)
        auth = mongodb.Authenticator(args.mongo_host, args.mongo_port)
    elif args.auth == 'env':
        auth = env.Authenticator()
    else:
        auth = sqlite.Authenticator('sqlite.db')

    ssl_context = None
    if args.tlscert:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(args.tlscert, args.tlskey)

    broker = Server(
        auth=auth,
        bind=args.bind,
        exporter=args.exporter,
        name=args.name,
        ssl=ssl_context,
    )

    return aiorun.run(broker.serve_forever())


if __name__ == '__main__':
    main()
