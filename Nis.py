#!/usr/bin/python

import zerorpc
import requests, json

class NemBridge:
    mainnet = [ # from NanoWallet 2.1.2 main.js code
        '62.75.171.41',
        'san.nem.ninja',
        'go.nem.ninja',
        'hachi.nem.ninja',
        'jusan.nem.ninja',
        'nijuichi.nem.ninja',
        'alice2.nem.ninja',
        'alice3.nem.ninja',
        'alice4.nem.ninja',
        'alice5.nem.ninja',
        'alice6.nem.ninja',
        'alice7.nem.ninja',
        'localhost',
    ]

    def __init__(self):
        self.index = -1
        self.baseurl = None
        self.pickAnotherOne()
        #self.baseurl = "%s://%s:%i/" % ('http', NemBridge.mainnet[self.index], 7890)

    # makes a best effort to pick a healthy NIS from mainnet list;
    # each call changes self.index at least once, so we are not stuck on some server returning "ok" to status call but failing actual announce for other reasons
    def pickAnotherOne(self):
        maxtries = len(NemBridge.mainnet)
        self.index = (self.index + 1) % maxtries #-1 initially, will be 0 after 1st call
        triedtimes = 0

        while (triedtimes < maxtries):
            try:
                self.baseurl = "%s://%s:%i/" % ('http', NemBridge.mainnet[self.index], 7890)
                url = self.baseurl + "status"
                r = requests.get(url)
                if (r.status_code==200):
                    response = json.loads(r.text)
                    if (response['code']==6): # OK, use current index
                        break
                    else:
                        pass
                else:
                    pass
            except:
                pass
            self.index = (self.index + 1) % maxtries
            triedtimes = triedtimes + 1

    def selected(self):
        return NemBridge.mainnet[self.index]

    def _height(self):
        url = self.baseurl + "chain/height"
        r = requests.get(url)
        if (r.status_code==200):
            return r.text
        else:
            raise Exception()

    def height(self):
        try:
            return self._height()
        except:
            try:
                self.pickAnotherOne()
                return self._height()
            except:
                return None

    def _announce(self, _signed_tx_json):
        url = self.baseurl + "transaction/announce"
        r = requests.post(url, json = _signed_tx_json)
        if (r.status_code==200):
            pass
        else:
            raise Exception()

    def announce(self, _signed_tx_json):
        try:
            self._announce(_signed_tx_json)
        except:
            try:
                self.pickAnotherOne()
                self._announce(_signed_tx_json)
            except:
                pass

class TxSignService:
    def __init__(self, _nembridge = None):
        self.nem = _nembridge
        if (self.nem == None):
            self.nem = NemBridge()
        self.rpcclient = None
        pass

    # we will use nem-sdk.js served through zerorpc instead of locally running NIS
    def simplesendXEM(self, _amount, _message, _address):
        # initialise transaction and signer data
        tx = {
            "amount"            : _amount,
            "recipient"         : _address,
            "recipientPublicKey": "",
            "isMultisig"        : False,
            "multisigAccount"   : "",
            "message"           : ("" if _message is None else _message),
        #    "isEncrypted"       : False,
            "mosaics"           : []
        }

        # not used anyway
        common = {
            "password"  : "",
            "privateKey": ""
        }
        # convert to json strings
        str_common=json.dumps(common)
        str_tx=json.dumps(tx)

        try:
            if (self.rpcclient == None):
                # initialise client
                self.rpcclient = zerorpc.Client()
                self.rpcclient.connect("tcp://127.0.0.1:4242")

            # call remote procedure, passing string arguments
            signed = self.rpcclient.sign(str_tx, str_common, "mainnet")

            #signed = self.rpcclient.sign(str_tx, str_common, "testnet")
            # post signed transaction to a NIS instance
            self.nem.announce(signed)
            return True
        except:
            return False

def test():
    t = TxSignService()
    for i in range(1, len(NemBridge.mainnet)*2):
        print(t.nem.selected())
        print(t.nem.height())
        t.nem.pickAnotherOne()
if __name__ == "__main__":
    test()
