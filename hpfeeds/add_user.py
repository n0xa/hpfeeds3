import argparse
import pymongo
import uuid


def handle_list(arg):
    if arg:
        return arg.split(",")
    else:
        return []


def create_user(host, port, owner, ident, secret, publish, subscribe):
    publish_list = handle_list(publish)
    subscribe_list = handle_list(subscribe)
    rec = {
        "owner": owner,
        "ident": ident,
        "secret": secret,
        "publish": publish_list,
        "subscribe": subscribe_list
    }

    client = pymongo.MongoClient(host=host, port=port)
    res = client.hpfeeds.auth_key.update({"identifier": ident}, {"$set": rec}, upsert=True)
    client.fsync()
    client.close()
    return res, rec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongodb-host", required=True)
    parser.add_argument("--mongodb-port", required=True, type=int)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--ident", required=True)
    parser.add_argument("--secret", required=False, default="")
    parser.add_argument("--publish", required=True)
    parser.add_argument("--subscribe", required=True)
    args = parser.parse_args()

    host = args.mongodb_host
    port = args.mongodb_port

    owner = args.owner
    ident = args.ident
    publish = args.publish
    subscribe = args.subscribe
    if args.secret:
        secret = args.secret
    else:
        secret = str(uuid.uuid4()).replace("-", "")

    res, rec = create_user(host=host, port=port, owner=owner, ident=ident,
                           secret=secret, publish=publish, subscribe=subscribe)

    if res['updatedExisting']:
        print("updated %s" % rec)
    else:
        print("inserted %s" % rec)


if __name__ == "__main__":
    main()
