from mtgoxeur import MtGoxEUR
from bitcoincentraleur import BitcoinCentralEUR
from intersangoeur import IntersangoEUR

mbc = BitcoinCentralEUR()
mgox = MtGoxEUR()
mis = IntersangoEUR()

print mbc.name, mbc.get_ticker()
print mgox.name, mgox.get_ticker()
print mis.name, mis.get_ticker()


