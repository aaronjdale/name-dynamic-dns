import pickle
import requests


# no key file exists, prompt to enter credentials and save to file
def main():
    store = dict()
    try:
        with open('.updater_credentials', 'rb') as file:
            username = pickle.load(file)
            print(username)
    except FileNotFoundError:
        username = input('username: ')
        with open('.updater_credentials', 'wb') as file:
            pickle.dump(username, file)




if __name__ == '__main__':
    main()
