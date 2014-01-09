### Generate a static web page with dogecoind account balances

Example of using dogecoind to generate a static webpage
of Kanye West's tracks ranked by the amount of DOGE donated
to each track's pubkey address.

Visible at http://coinyesbest.com/

Use `./coinyesbest.py createaccounts` to initialize accounts then
`./coinyesbest.py generateindex` to generate the static ranking page
`output/index.html`.

Serve output/ using to view the site. For example

    twistd web --path=output -p 8082
    google-chrome http://localhost:8082/

`coinyesbest.py` can be easily modified to interface with litecoind, bitcoind,
or any other crypto-currency based off the vanilla bitcoin sources.

Configure coinyecoind JSON-RPC by adding the `rpcuser` and `rpcpassword` config
entries to `~/.coinyecoin/coinyecoin.conf`.

Depends on bitcoin-python and mako templates:

    sudo pip install bitcoin-python mako

