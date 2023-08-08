import os

def create_env_file():

    if os.path.exists('.env'):
        print('File already exists')
        inp = input('Do you want to overwrite it? (y/n): ')
        if inp == 'y':
            api_keys = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
            with open('.env', 'w') as f:
                f.write("DEBUG_MODE=true\n\n")
                for key in api_keys:
                    value = input(f'Enter your {key}: ')
                    f.write(f'{key}={value}\n')
                    print(f'{key}={value}')
            print('\nFile created successfully.')
        else:
            print('Exiting...')
    else:
        api_keys = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
        with open('.env', 'w') as f:
            f.write("DEBUG_MODE=true\n\n")
            for key in api_keys:
                value = input(f'Enter your {key}: ')
                f.write(f'{key}={value}\n')
                print(f'{key}={value}')
        print('\nFile created successfully.')

if __name__ == '__main__':
    create_env_file()