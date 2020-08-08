import requests
import json
import sys

# data fille where to store config
credential_filename = '.namedns_data'


class NameAPI(object):
    """
    Interface for Name.com V4 API
    see: https://www.name.com/api-docs/
    create/modify/view credentials here: https://www.name.com/account/settings/api
    """
    def __init__(self, username, api_key, domain):
        self.username = username
        self.api_key = api_key
        self.base_url = 'https://api.name.com/v4/'
        self.domain_name = domain

    def list_records(self):
        """
        Gets a list of all the records (A, ANAME, MX, etc) and all the details associated with it
        see: https://www.name.com/api-docs/DNS#ListRecords
        :return: dict
        """
        endpoint = f'domains/{self.domain_name}/records'

        r = requests.get(f'{self.base_url}{endpoint}', auth=(self.username, self.api_key))
        records = json.loads(r.text)['records']
        return records

    def update_record(self, record_id, data):
        """
        Updates a record by ID with the specified json data.
        see: https://www.name.com/api-docs/DNS#UpdateRecord
        :param record_id:
        :param data:
        :return:
        """
        endpoint = f'domains/{self.domain_name}/records/{record_id}'
        r = requests.put(f'{self.base_url}{endpoint}', auth=(self.username, self.api_key), data=json.dumps(data))
        response = json.loads(r.text)
        print(response)


def query_yes_no(question, default='no'):
    """
    Console input for true/false input, stole this from somewh`ere on the internet but
    don't remember exactly where
    :param question:
    :param default:
    :return:
    """
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
    is_first_time_setup = False
    try:
        with open(credential_filename) as file:
            data = json.load(file)

        username = data['username']
        api_key = data['api_key']
        domain = data['domain']

    except (FileNotFoundError, KeyError) as e:
        # need the username and api key
        username = data['username'] = input('username: ')
        api_key = data['api_key'] = input('api key: ')
        domain = data['domain'] = input('domain: ')
        data['records'] = dict()
        is_first_time_setup = True

    # detect public ip
    public_ip = get_public_ip()
    print(f'public ip detected as: {public_ip}')

    # get records from name account
    name_api = NameAPI(username=username, api_key=api_key, domain=domain)
    records = name_api.list_records()

    # check whether the script should prompt for update
    # either if it is the first time setup
    # todo add --setup flag argument
    should_prompt_to_update = is_first_time_setup

    # only care about A records since they are the only ones that point to IP addresses
    a_records = [record for record in records if record['type'] == 'A']
    for record in a_records:
        record_id = record['id']
        record_fqdn = record['fqdn']
        record_value = record['answer']

        # check to see if we should prompt for update
        if should_prompt_to_update:
            print(f'"{record_fqdn}" currently points to "{record_value}"')
            # if the should_update_flags have changed, save them to the file
            data['records'][str(record_id)] = query_yes_no('automatically update? ')

            # save file if records have changed
            with open(credential_filename, 'w') as file:
                json.dump(data, file)

        # check to see if the update flag is set
        has_update_flag = str(record_id) in data['records']
        if has_update_flag:
            # check if the record is flagged for automatic update
            should_automatically_update = bool(data['records'][str(record_id)])
            if should_automatically_update:
                # check if the IP address has changed
                if record_value != public_ip:  # check if changed
                    name_api.update_record(record_id=record_id, data={
                        'answer': public_ip
                    })
                    print(f'{record_fqdn} updated: "{record_value}" changed to "{public_ip}"')
                else:
                    print(f'{record_fqdn} has not changed: "{record_value}" == "{public_ip}"')
            else:
                print(f'{record_fqdn} has update set to false, skipping.')
        else:
            print(f'{record_fqdn} does not have update flag set, skipping.')


if __name__ == '__main__':
    main()
