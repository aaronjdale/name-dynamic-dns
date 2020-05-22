import pickle
import requests


credential_filename = '.updater_credentials'


def main():
    store = dict()
    try:
        with open(credential_filename, 'rb') as file:
            username = pickle.load(file)
            api_key = pickle.load(file)

            # just test this
            print(username)
            print(api_key)

    except FileNotFoundError:
        # no credentials file exists, prompt user for their username and api key
        username = input('username: ')
        api_key = input('api key: ')
        with open(credential_filename, 'wb') as file:
            pickle.dump(username, file)
            pickle.dump(api_key, file)




if __name__ == '__main__':
    main()
