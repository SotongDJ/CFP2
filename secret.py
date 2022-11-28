import rtoml, argparse

parser = argparse.ArgumentParser(description="convert secret from env to toml")
parser.add_argument("--spotify_id", help="spotify web api id")
parser.add_argument("--spotify_secret", help="spotify web api secret")
args = parser.parse_args()

secret_dict = {
    "spotify_id": (args.spotify_id if args.spotify_id else str()),
    "spotify_secret": (args.spotify_secret if args.spotify_secret else str()),
}
with open("secret.toml",'w') as target_handler:
    rtoml.dump(secret_dict,target_handler)
