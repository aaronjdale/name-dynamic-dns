import pickle
import requests
import json
import sys


credential_filename = '.namedns_data'


class NameAPI(object):
    def __init__(self, username, api_key, domain):
        self.username = username
        self.api_key = api_key
        self.base_url = 'https://api.name.com/v4/'
        self.domain_name = domain

    def list_records(self):
        endpoint = f'domains/{self.domain_name}/records'

        r = requests.get(f'{self.base_url}{endpoint}', auth=(self.username, self.api_key))
        records = json.loads(r.text)['records']
        return records

    def update_record(self, record_id, data):
        endpoint = f'domains/{self.domain_name}/records/{record_id}'
        r = requests.put(f'{self.base_url}{endpoint}', auth=(self.username, self.api_key), data=json.dumps(data))
        response = json.loads(r.text)
        print(response)


def query_yes_no(question, default='no'):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_public_ip():
    r = requests.get('https://v4.ident.me')
    # r = requests.get('http://whatismyip.akamai.com/')

    public_ip = r.text

    # todo: error handle :)

    return public_ip


def main():
    data = dict()

    # load existing data
    try:
        with open(credential_filename) as file:
            data = json.load(file)

        username = data['username']
        api_key = data['api_key']
        domain = data['domain']
        record_data = data['records']

    except (FileNotFoundError, KeyError) as e:
        # need the username and api key
        username = data['username'] = input('username: ')
        api_key = data['api_key'] = input('api key: ')
        domain = data['domain'] = input('domain: ')
        record_data = data['records'] = dict()

    public_ip = get_public_ip()
    print(f'public ip detected as: {public_ip}')

    name_api = NameAPI(username=username, api_key=api_key, domain=domain)
    records = name_api.list_records()

    a_records = [record for record in records if record['type'] == 'A']

    for record in a_records:
        record_id = record['id']
        record_name = record['domainName']
        record_value = record['answer']

        # if we don't know how to handle this record
        if record_id not in record_data.keys():
            # check if this should be managed
            print(f'{record_name} currently points to: {record_value}')
            record_data[record_id] = query_yes_no('automatically update? ')

        # update if flagged as true
        if record_data[record_id] and record_value != public_ip:  # check if changed
            name_api.update_record(record_id=record_id, data={
                'answer': public_ip
            })
            print(f'entry updated: {record_value} > {public_ip}')
        else:  # no change required
            print(f'no change detected.')

    data['records'] = record_data

    # save file if records have changed
    with open(credential_filename, 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':
    main()
