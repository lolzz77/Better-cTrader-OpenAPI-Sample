# cTrader

A better sample scripts than the original Sample given by cTrader 
https://github.com/spotware/OpenApiPy/blob/main/samples/ConsoleSample/main.py

The original script uses 1 thread, all user command, message received, are handled
in one single thread, causing major disconnection and inconsistance message receiving.

This sample uses multithreading, solves random disconnection issue.

# Version
1. Python - 3.10.12

# How to start
1. Install python in your OS, google how to
2. `pip install -r requirements.txt`
3. Create `.env` file in this folder (eg: The folder this README.md is in)
4. Go to https://openapi.ctrader.com/apps
5. Click "Credentails"
6. Click "Sandbox"
7. Note down all these values
8. Put the following
```
APP_CLIENT_ID="xxx"
APP_CLIENT_SECRET="xxx"
ACCESS_TOKEN="xxx"
REFRESH_TOKEN="xxx"
ACCOUNT_TYPE="<demo or live>"
```
9. After that, to start the script, run `python main.py`
10. Read the console message, type `ProtoOAGetAccountListByAccessTokenReq`
to get list of accounts available
11. Type `setAccount <ctidTraderAccountId>` to authenticate that account
12. Then type `help` to proceed with any commands you would like to try
13. Press `CTRL + D` to disconnect & terminate the program
14. Known issue:
- There is one major unhandled error problem. If command typed result in python execution error 
(eg: type `ProtoOASubscribeSpotsReq` without giving required parameter, or account is not authorized 
before entering the rest of command), will result in script hang.
I don't know what's the better way of handling it yet. This is from original sample code.
- Calling `ProtoOASubscribeSpotsReq` will result in script error, it happens after the
parameter `timeInSeconds` timeout. I haven't work on how to better handle it yet.