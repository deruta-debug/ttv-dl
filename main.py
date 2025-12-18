import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

AUTH_PATH = "auth.json"
BASE_URL = "https://id.twitch.tv/oauth2"


def main():
    load_dotenv()

    token = Token(AUTH_PATH)
    print(token)


class Token:
    def __init__(self, file_path):
        self.file_path = file_path
        self.access_token = None

        self.load()
        self.validate()

    def load(self):
        print(f"Loading {self.file_path}...")
        file, err = read_file(self.file_path)
        if err is not None:
            raise Exception(err)

        if file is None or file == "":
            self.authenticate()
            return

        try:
            data = json.loads(file)
            self.access_token = data["access_token"]
        except Exception as e:
            raise Exception(f"[{type(e).__name__}] {self.file_path}: invalid JSON")

    def authenticate(self):
        print("Fetching new access_token...")
        credentials, err = get_api_credentials()
        if err is not None or credentials is None:
            raise Exception(f"Invalid API credentials: {err}")

        data, err = get_access_token(credentials)
        if err is not None or data is None:
            raise Exception(err)

        self.access_token = data["access_token"]
        self.write()

    def validate(self):
        print("Validating token...")
        data, err = validate_access_token(self.access_token)
        if err is not None or data is None:
            print(f"FAIL: {err}")
            self.authenticate()
            return
        days_left = round(data["expires_in"] / (24 * 60 * 60))
        print(f"The token is valid, expires in {days_left} days...")

    def write(self):
        auth_dict = {"access_token": self.access_token}
        err = write_file(self.file_path, auth_dict)
        if err is not None:
            raise Exception(err)

        print(f"{self.file_path} saved successfully!")

    def __str__(self):
        return f"Token: {self.access_token}"


def validate_access_token(access_token):
    url = BASE_URL + "/validate"
    headers = {"Authorization": "Bearer " + access_token}

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if res.status_code != 200:
            return (data, f"{res.reason} {data["status"]}: {data["message"]}")

        return (data, None)
    except Exception as e:
        return (None, f"Error validating access_token: {e}")


def get_access_token(credentials):
    url = BASE_URL + "/token"
    payload = {
        "client_id": credentials[0],
        "client_secret": credentials[1],
        "grant_type": "client_credentials",
    }

    try:
        res = requests.post(url, data=payload)
        data = res.json()

        if res.status_code != 200:
            return (data, f"{res.reason} {data["status"]}: {data["message"]}")

        return (data, None)
    except Exception as e:
        return (None, f"Error getting access_token: {e}")


def read_file(path):
    try:
        file_path = Path(path)
        file_path.touch(exist_ok=True)

        with open(file_path, "r") as f:
            content = f.read()

        return (content, None)
    except Exception as e:
        return (None, f"Error reading {path}: {e}")


def write_file(path, content):
    try:
        with open(path, "w") as f:
            json.dump(content, f, indent=2)

        return None
    except Exception as e:
        return f"Error writing to file: {e}"


def get_api_credentials():
    env_filepath = Path(".env")
    env_filepath.touch(exist_ok=True)

    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    if not client_id:
        return (None, "CLIENT_ID environment variable not found")
    if not client_secret:
        return (None, "CLIENT_SECRET environment variable not found")

    credentials = (client_id, client_secret)
    return (credentials, None)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}")
        exit(1)
