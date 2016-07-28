# https://search.mapzen.com/v1/search?api_key=search-TeXrSTX&text=Kornblumenweg%20Harlaching

import argparse, os, sys
from pprint import pprint

from random import choice

from tools import Users
from tools import Wigle
from tools import Results

parser = argparse.ArgumentParser()
parser.add_argument('--lat', default=40.727721, type=float, required=True, help='latitude')
parser.add_argument('--lon', default=-74.002102, type=float, required=True, help='longitude')
parser.add_argument('--rad', default=1, type=int, required=False, help='radius scale, default=1 (roughly 100m)')
parser.add_argument('--name', required=True, help='name for output dir')
parser.add_argument('-f', '--overwrite', action='store_true', help='overwrite existing files')
args = parser.parse_args()




def validate_out_put_path(path):
    if os.path.isdir(output_path) and args.overwrite is False:
        print "[-] the out out folder exists already, use -f to force overwrite"
        sys.exit()
    elif os.path.isdir(output_path) and args.overwrite is True:
        print "[+] Overwriting", output_path
    elif not os.path.isdir(output_path):
        print "[+] Creating output directory."
        os.makedirs(output_path)

if __name__ == '__main__':

    output_root_path = "output"
    output_path = os.path.join(output_root_path, args.name)
    
    validate_out_put_path(output_path)
    
    
    users = Users.Users()
    user = users.select_random()

    account = Wigle.Wigle(user.name, user.password)

    print "[+] MAKING REQUEST"
    print "\tUSERNAME", user.name, " PASSWORD", user.password[0] + "*"*(len(user.password)-1)
    print '\tLATITUDE', args.lat, " LONGITUDE", args.lon

    data = account.from_coordinates(args.lat, args.lon, args.rad)

    results = Results.Results(data)
    results.write_to_file(path=output_path)


    











