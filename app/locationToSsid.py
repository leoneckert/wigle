# https://search.mapzen.com/v1/search?api_key=search-TeXrSTX&text=Kornblumenweg%20Harlaching

import argparse, os, sys
from pprint import pprint

from random import choice

from tools import Users
from tools import Wigle

parser = argparse.ArgumentParser()
parser.add_argument('--lat', default=40.727721, type=float, required=False, help='latitude')
parser.add_argument('--lon', default=-74.002102, type=float, required=False, help='longitude')
parser.add_argument('--name', required=True, help='name for output dir')
parser.add_argument('-f', '--overwrite', action='store_true', help='overwrite existing files')
args = parser.parse_args()

output_root_path = "output"


def filter_by_channels(results):
    channels = dict()
    for i, result in enumerate(results):
        if 'channel' in result:
            c = result["channel"]
            if c is None:
                c = choice([1,6,11])
            
            if c not in channels:
                channels[c] = dict()
            if 'netid' in result:
                channels[c][result['netid']] = " "
            if 'ssid' in result and result['ssid'] is not None:
                channels[c][result['netid']] = result['ssid']
    return channels

def write_channels_to_files(channels, path):
    for channel in channels:
        writer = open(os.path.join(path,str(channel)+".txt"), "w")
        for MAC in channels[channel]:
            ssid = channels[channel][MAC]
            writer.write(MAC + " " + ssid + "\n")
        writer.close()


if __name__ == '__main__':
    output_path = os.path.join(output_root_path, args.name)
    if os.path.isdir(output_path) and args.overwrite is False:
        print "[-] the out out folder exists already, use -f to force overwrite"
        sys.exit()
    elif os.path.isdir(output_path) and args.overwrite is True:
        print "[+] Overwriting", output_path
    elif not os.path.isdir(output_path):
        print "[+] Creating output directory."
        os.makedirs(output_path)
    

    
    users = Users.Users()
    user = users.select_random()

    account = Wigle.Wigle(user.name, user.password)

    print "[+] MAKING REQUEST"
    print "\tUSERNAME", user.name, " PASSWORD", user.password[0] + "*"*(len(user.password)-1)
    print '\tLATITUDE', args.lat, " LONGITUDE", args.lon

    results = account.from_coordinates(args.lat, args.lon)

    channels = filter_by_channels(results)

    write_channels_to_files(channels, path=output_path)

    











