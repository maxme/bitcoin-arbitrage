#!/usr/bin/env python

import json
import urllib
import urllib2
import time
import subprocess
from pprint import pprint

USDEUR_URL = "http://currency-api.appspot.com/api/USD/EUR.json?key=7c39adea3d9de51587da396d4f268db4aafa9b28"

class USDEUR_Rate:
    filename = "usdeur.json"
    update_time = 60 * 20 # 20 mins
    def __init__(self):
        try:
            self.load()
        except Exception, e:
            print e
            self.rate = 1
            self.last_update = 0
        self.update()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.rate = data["rate"]
        self.last_update = data["last_update"]

    def save(self):
        json.dump({"rate": self.rate, "last_update": self.last_update}, open(self.filename, "w"))

    def update(self):
        if (time.time() - self.last_update) > self.update_time:
            rate = self.http_request()
            self.last_update = time.time()
            if rate != 0:
                self.rate = rate
            self.save()

    def http_request(self):
        try:
            response = urllib2.urlopen(USDEUR_URL)
            json_response = json.loads(response.read())
            return json_response["rate"]
        except Exception, e:
            print e
            return 0

    def get_rate(self):
        self.update()
        return self.rate

if __name__ == "__main__":
    r = USDEUR_Rate()
    print r.get_rate()

