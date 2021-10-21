#!/usr/bin/env python3
# Copyright (c) 2015-2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test Consensus Hash ."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *

import os
import json
import http.client
import urllib.parse

class ConsensusTest (BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.extra_args = [["-txindex=1"]]

    def setup_chain(self):
        super().setup_chain()
        #Append rpcauth to bitcoin.conf before initialization
        rpcauth = "rpcauth=rt:93648e835a54c573682c2eb19f882535$7681e9c5b74bdd85e78166031d2058e1069b3ed7ed967c93fc63abba06f31144"
        rpcuser = "rpcuser=rpcuser💻"
        rpcpassword = "rpcpassword=rpcpassword🔑"
        addresstype = "addresstype=legacy"
        fallbackfee = "fallbackfee=0.0002"
        settxfee = "settxfee=0.0001"
        datasize = "datacarriersize=80"
        with open(os.path.join(self.options.tmpdir+"/node0", "bitcoin.conf"), 'a', encoding='utf8') as f:
            f.write(rpcauth+"\n")
            f.write(rpcuser+"\n")
            f.write(rpcpassword+"\n")
            f.write(addresstype+"\n")
            f.write(fallbackfee+"\n")
            f.write(settxfee+"\n")
            f.write(datasize+"\n")

    # NOTE: this is the basis, of course, we can build more objects and classes
    # in order to do a better work

    def run_test(self):

        self.log.info("Preparing the workspace...")


        ################################################################################
        # Checking RPC tl_senddexoffer and tl_getactivedexsells (in the first 200 blocks of the chain) #
        ################################################################################

        url = urllib.parse.urlparse(self.nodes[0].url)

        #Old authpair
        authpair = url.username + ':' + url.password

        headers = {"Authorization": "Basic " + str_to_b64str(authpair)}

        addresses = ["2N2zjPhEyPPEhuyyNuRZYJrFYLo2rY8Pcd7", "2N7rhBvn5JKmGf1bh7CKqMg9MwTmiZVs4LT", "2N9gi6W5qrzsxpZ1MGWBdZACWKYvQyou3Fa", "2N7nKhhMm1PdjKvjJZo499hq2qmV3BwEjzA", "2MwfpVf6rdH3JULp4nbpFi14ZkGrnbsgyNA"]
        privkeys = ["cRhhuoo1mX7vatRKEAxXqAxWRyTwtNepKnEz4fKinH6u8UY1GYCJ", "cNqTmnPz42zHq52uB9oPcYGoZ6beDx3VoeiaBrxgqDV813gXdmaG", "cPv71tT4T3ZgzzCa52vHwnLgLDsaLfcyi5bBWzcP5pBEP2tQ71FD", "cMvqJHb6tPqqpJJvP1rLLF3Aude6Zdu8Cvtw6GBuCsEj3js1UGcb", "cSwwz2EcZTzhmnAbrgAuRSdWsNaP8Gvkgp9GnLD4V5iT4yR32Xeb"]

        rAddress = "2N2zjPhEyPPEhuyyNuRZYJrFYLo2rY8Pcd7"

        conn = http.client.HTTPConnection(url.hostname, url.port)
        conn.connect()

        self.log.info("importing privkeys of addresses")
        for priv in privkeys:
            params = str([priv]).replace("'",'"')
            out = tradelayer_HTTP(conn, headers, True, "importprivkey",params)
            # self.log.info(out)
            assert_equal(out['error'], None)

        params1 = str([200, rAddress]).replace("'",'"')
        tradelayer_HTTP(conn, headers, False, "generatetoaddress", params1)

        self.log.info("Funding addresses with LTC")
        amount = 3
        tradelayer_fundingAddresses(addresses, amount, conn, headers)

        params1 = str([1, rAddress]).replace("'",'"')
        tradelayer_HTTP(conn, headers, False, "generatetoaddress", params1)


        self.log.info("Checking consensus hash")
        out = tradelayer_HTTP(conn, headers, False, "tl_getcurrentconsensushash")
        # self.log.info(out)
        assert_equal (out['result']['consensushash'],"4d57f21205a36a6f9c956b7831c85962b1535811a6bac65cadcba90a86d17eab")

        self.log.info("Creating new tokens (sendissuancefixed)")
        array = [0]
        params = str([addresses[0], 2, 0,"lihki","","","90000000",array]).replace("'",'"')
        out = tradelayer_HTTP(conn, headers, True, "tl_sendissuancefixed",params)
        # self.log.info(out)

        params1 = str([1, rAddress]).replace("'",'"')
        tradelayer_HTTP(conn, headers, False, "generatetoaddress", params1)

        self.log.info("Checking consensus hash")
        out = tradelayer_HTTP(conn, headers, False, "tl_getcurrentconsensushash")
        # self.log.info(out)
        assert_equal (out['result']['consensushash'], "7f16261a86887290922478e9e755aa785890d717b8e41b7e3f2786f1f233c3f5")


        self.log.info("Self Attestation for addresses")
        for addr in addresses:
            params = str([addr,addr,""]).replace("'",'"')
            tradelayer_HTTP(conn, headers, False, "tl_attestation", params)
            params1 = str([1, rAddress]).replace("'",'"')
            tradelayer_HTTP(conn, headers, False, "generatetoaddress", params1)


        self.log.info("Checking attestations")
        out = tradelayer_HTTP(conn, headers, False, "tl_list_attestation")
        # self.log.info(out)

        result = []
        registers = out['result']

        for addr in addresses:
            for i in registers:
                if i['att sender'] == addr and i['att receiver'] == addr and i['kyc_id'] == 0:
                     result.append(True)

        assert_equal(result, [True, True, True, True, True])

        self.log.info("Checking the property lihki")
        params = str([4])
        out = tradelayer_HTTP(conn, headers, False, "tl_getproperty",params)
        assert_equal(out['error'], None)
        # self.log.info(out)
        assert_equal(out['result']['propertyid'],4)
        assert_equal(out['result']['name'],'lihki')
        assert_equal(out['result']['data'],'')
        assert_equal(out['result']['url'],'')
        assert_equal(out['result']['divisible'],True)
        assert_equal(out['result']['totaltokens'],'90000000.00000000')

        self.log.info("Checking consensus hash")
        out = tradelayer_HTTP(conn, headers, False, "tl_getcurrentconsensushash")
        # self.log.info(out)
        assert_equal (out['result']['consensushash'],"69f62bfc8947520701fe2b57bb6bd2b8c10a29e2791ab6642c2496abb5035c81")


        self.log.info("Creating new tokens (sendissuancefixed)")
        array = [0]
        params = str([addresses[1], 2, 0,"dan","","","123456789",array]).replace("'",'"')
        out = tradelayer_HTTP(conn, headers, True, "tl_sendissuancefixed",params)
        # self.log.info(out)

        params1 = str([1, rAddress]).replace("'",'"')
        tradelayer_HTTP(conn, headers, False, "generatetoaddress", params1)


        self.log.info("Checking the property dan")
        params = str([5])
        out = tradelayer_HTTP(conn, headers, False, "tl_getproperty",params)
        assert_equal(out['error'], None)
        assert_equal(out['result']['propertyid'],5)
        assert_equal(out['result']['name'],'dan')

        self.log.info("Checking consensus hash")
        out = tradelayer_HTTP(conn, headers, False, "tl_getcurrentconsensushash")
        # self.log.info(out)
        assert_equal (out['result']['consensushash'],"597d95980198a7483d3407d77dcf201b85e6ad4ca606574fbf8ea7a68e8acda3")


        conn.close()
        self.stop_nodes()

if __name__ == '__main__':
    ConsensusTest ().main ()
