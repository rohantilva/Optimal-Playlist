import configparser

config = configparser.ConfigParser()
config.add_section('Spotify')
config.set('Spotify', 'client_id', 'b88d0c99674247bcb826148026417e6f')
config.set('Spotify', 'client_secret', "fcc139e4e91f4a78aa797bd11a194ce3")


with open('config.ini', 'w') as configfile:
	config.write(configfile)
