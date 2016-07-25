# https://search.mapzen.com/v1/search?api_key=search-TeXrSTX&text=Kornblumenweg%20Harlaching

import argparse
from pprint import pprint

from tools import Users
from tools import Wigle

parser = argparse.ArgumentParser()
parser.add_argument('--lat', default=40.727721, type=float, required=False, help='latitude')
parser.add_argument('--lon', default=-74.002102, type=float, required=False, help='longitude')
args = parser.parse_args()



if __name__ == '__main__':
    
    users = Users.Users()
    user = users.select_random()

    account = Wigle.Wigle(user.name, user.password)

    print "[+] MAKING REQUEST"
    print "\tUSERNAME", user.name, " PASSWORD", user.password[0] + "*"*(len(user.password)-1)
    print '\tLATITUDE', args.lat, " LONGITUDE", args.lon

    results = account.from_coordinates(args.lat, args.lon)
    
    # results = account.search(ssid = 'itpsandbox')
    print results

    for i, result in enumerate(results):
        print "-"*40+"\n"+str(i)+"\n"+"-"*40
        pprint(result)

    











