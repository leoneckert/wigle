import ConfigParser
import random
class Users(object):
    def __init__(self, settings_path='settings.cfg'):
        self.settings_path = settings_path
        self.users = self.init_users()
        

    def init_users(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.settings_path)
            print "[+] Read settings"
        except:
            print "[-] Could not read settings"

        users = dict()

        try:
            password = config.get('wigle_multi_accounts', 'psswrd' )
            usrnms = config.get('wigle_multi_accounts', 'usrnms' )
            usernames = map(lambda (a): a.strip(), usrnms.split(","))
            for user in usernames:
                users[user] = password
        except: pass


        idx_accounts = 1
        while True:
            try:
                user = config.get('wigle_individual_accounts', str(idx_accounts))
                user = map(lambda (a): a.strip(), user.split(","))
                if len(users) == 2:
                    users[user[0]] = user[1]
            except: break
            idx_accounts += 1
        
        return users


    def all(self):
        return self.users
    def ran(self):
        ran_user = random.choice(self.users.keys())
        return dict({'name': ran_user, 'pw':self.users[ran_user]})