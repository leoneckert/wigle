import argparse

from tools import Users
from tools import Wigle


parser = argparse.ArgumentParser()
parser.add_argument('--lat', default=40.7291, type=float, required=False, help='latitude')
parser.add_argument('--lon', default=-73.9943, type=float, required=False, help='longitude')
args = parser.parse_args()



if __name__ == '__main__':
    
    users = Users.Users()
    user = users.ran()
    account = Wigle.Wigle(user["name"], user["pw"])
    

    print "[+] MAKING REQUEST"
    print "\tUSERNAME:", user["name"], " PASSWORD:", user["pw"][0] + "*"*(len(user["pw"])-1)
    print '\tLATITUDE', args.lat, " LONGITUDE", args.lon

    lon_diff = -0.001148 #lon difference
    lat_diff = -0.000944 #lat difference



    results = account.search(lat_range=(lat - lat_diff, lat + lat_diff), long_range = (lon - lat_diff, lon + lat_diff))
    
    # results = account.search(ssid = 'itpsandbox')

    print account.get_user_info()
    for i, result in enumerate(results):
        print "-"*40+"\n"+str(i)+"\n"+"-"*40
        pprint(result)

    print results











