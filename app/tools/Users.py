import ConfigParser
import random

class User(object):
    def __init__(self, name, password, mapzen_key):
        self.name = name
        self.password = password
        self.mapzen_key = mapzen_key

class Users(object):
    def __init__(self, settings_path='settings.cfg'):
        self.settings_path = settings_path
        self.config = self.init_config()

        self.mapzen_key = self.init_mapzen()
        self.users = self.init_users()
        
    def init_config(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.settings_path)
            print "[+] Read settings"
        except:
            print "[-] Could not read settings"
        return config

    def init_mapzen(self):
        mapzen_key = None
        try:
            mapzen_key = self.config.get('mapzen', 'key' )
        except: pass
        return mapzen_key

    def init_users(self):
        users = list()
        try:
            password = self.config.get('wigle_multi_accounts', 'psswrd' )
            usrnms = self.config.get('wigle_multi_accounts', 'usrnms' )
            usernames = map(lambda (a): a.strip(), usrnms.split(","))
            for user in usernames:
                users.append(User(user, password, self.mapzen_key))
        except: pass

        idx_accounts = 1
        while True:
            try:
                user = self.config.get('wigle_individual_accounts', str(idx_accounts))
                user = map(lambda (a): a.strip(), user.split(","))
                if len(users) == 2:
                    users[user[0]] = user[1]
            except: break
            idx_accounts += 1     
        return users


    def select_random(self):
        ran_user = random.choice(self.users)
        return ran_user