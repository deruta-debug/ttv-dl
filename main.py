import os

from dotenv import load_dotenv


def main():
    load_dotenv()
    CLIENT_ID, CLIENT_SECRET = get_api_credentials()
    print(CLIENT_ID, CLIENT_SECRET)


def get_api_credentials():
    if not os.path.exists(".env"):
        print(".env file not found")
        exit(1)

    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    if not client_id:
        print("CLIENT_ID environment variable not found")
        exit(1)
    if not client_secret:
        print("CLIENT_SECRET environment variable not found")
        exit(1)
    return client_id, client_secret


if __name__ == "__main__":
    main()
