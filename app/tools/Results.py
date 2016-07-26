from random import choice
import sys, os
class Results:
    """docstring for Results"""
    def __init__(self, data):
        self.results = data
        self.by_channel = self.sort_by_channel(self.results)
        print self.by_channel
    
    def sort_by_channel(self, results):
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

    def write_to_file(self, path = None):
        if path is None:
            print "[-] No path for output files specified. Exiting."
            sys.exit()

        for channel in self.by_channel:
            writer = open(os.path.join(path,str(channel)+".txt"), "w")
            for MAC in self.by_channel[channel]:
                ssid = self.by_channel[channel][MAC]
                writer.write(MAC + " " + ssid + "\n")
            writer.close()

        