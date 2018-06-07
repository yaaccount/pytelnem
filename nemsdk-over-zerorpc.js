var nem = require("nem-sdk").default;
var readlineSync = require('readline-sync'); //to get wallet password interactivelly
var zerorpc = require("zerorpc");
//content of .wlt file - base64 encoded json string
var rawwallet = readlineSync.question('Enter content of .wlt file (base64): ', {
    hideEchoBack: true,
    mask: '*' //'*' default
});
//enter password interactively
var password = readlineSync.question('Enter wallet password: ', {
    hideEchoBack: true,
    mask: '' //'*' default
});

var wallet = JSON.parse(nem.crypto.js.enc.Base64.parse(rawwallet).toString(nem.crypto.js.enc.Utf8));
var account = wallet.accounts[0];
var common = { "password": password };
nem.crypto.helpers.passwordToPrivatekey(common, account, account.algo);
if (common.privateKey) {
    console.log("OK. Using wallet: " + account.address)
} else {
    console.log("Wrong.")
};

var server = new zerorpc.Server({
    sign: function(_tx, _common, net_name, reply) {
        // parse arguments to get objects
        // ignore given _common object, use "our" composed from wallet file
        // var common=JSON.parse(_common);
        var tx=JSON.parse(_tx);

        // get network object corresponding to name passed as argument, eg "testnet"
        var network=nem.model.network.data[net_name];

        // build the transaction object
        var transactionEntity = nem.model.transactions.prepare("transferTransaction")(common, tx, network.id);

        // initialise keypair object based on private key
        var kp = nem.crypto.keyPair.create(common.privateKey);

        // serialise transaction object
        var serialized = nem.utils.serialization.serializeTransaction(transactionEntity);

        // sign serialised transaction
        var signature = kp.sign(serialized);

        // build result object
        var result = {// 'debug_te' : transactionEntity,
            'data': nem.utils.convert.ua2hex(serialized),
            'signature': signature.toString()
        };

        // send response to client
        reply(null, result);
    }
});

//server.bind("tcp://0.0.0.0:4242");
server.bind("tcp://127.0.0.1:4242");

