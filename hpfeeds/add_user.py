import argparse
import pymongo
import uuid


def handle_list(arg):
    if arg:
        return arg.split(",")
    else:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongodb-host", required=True)
    parser.add_argument("--mongodb-port", required=True, type=int)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--ident", required=True)
    parser.add_argument("--secret", required=True)
    parser.add_argument("--publish", required=True)
    parser.add_argument("--subscribe", required=True)
    args = parser.parse_args()

    host = args.mongodb_host
    port = args.mongodb_port

    owner = args.owner
    ident = args.ident
    secret = args.secret
    publish = handle_list(args.publish)
    subscribe = handle_list(args.subscribe)

    if not secret:
        secret = str(uuid.uuid4()).replace("-", "")

    rec = {
        "owner": owner,
        "ident": ident,
        "secret": secret,
        "publish": publish,
        "subscribe": subscribe
    }

    client = pymongo.MongoClient(host=host, port=port)
    res = client.hpfeeds.auth_key.update({"identifier": ident}, {"$set": rec}, upsert=True)
    client.fsync()
    client.close()

    if res['updatedExisting']:
        print("updated %s" % rec)
    else:
        print("inserted %s" % rec)


if __name__ == "__main__":
    main()
