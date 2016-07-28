import ConfigParser
import random

class User(object):
    def __init__(self, name, password):
        self.name = name
        self.password = password
        # self.mapzen_key = mapzen_key

class Users(object):
    def __init__(self, settings_path='settings.cfg'):
        self.settings_path = settings_path
        self.config = self.init_config()

        # self.mapzen_key = self.init_mapzen()
        self.users = self.init_users()


    def init_config(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.settings_path)
            print "[+] Read settings"
        except:
            print "[-] Could not read settings"
        return config

    # def init_mapzen(self):
    #     mapzen_key = None
    #     try:
    #         mapzen_key = self.config.get('mapzen', 'key' )
    #     except: pass
    #     return mapzen_key

    def init_users(self):
        users = list()
        try:
            for section in self.config.sections():
                username = self.config.get(section, 'u' )
                password = self.config.get(section, 'p' )
                print username
                print password
                if len(username) == 0 or len(password) == 0:
                    continue
                users.append(User(username, password))
        except: 
            pass   
        return users


    def select_random(self):
        ran_user = random.choice(self.users)
        return ran_user