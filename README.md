# cTrader

A better sample scripts than the original Sample given by cTrader 
https://github.com/spotware/OpenApiPy/blob/main/samples/ConsoleSample/main.py

The original script uses 1 thread, all user command, message received, are handled
in one single thread, causing major disconnection and inconsistance message receiving.

This sample uses multithreading, solves random disconnection issue.

# Version
1. Python - 3.10.12

# How to start
1. First, go to https://openapi.ctrader.com/apps
2. Apply for an app
3. Wait until it approved
4. <img width="1711" height="288" alt="image" src="https://github.com/user-attachments/assets/2f8e9296-add1-4f0b-b751-2f5e3ad9cbfe" />
5. Open your cTrader account, go to `Settings` -> `FIX API`
6. <img width="263" height="179" alt="image" src="https://github.com/user-attachments/assets/3391cfc2-40bc-49be-8907-0faff38e428c" />
7. Copy `Host name`
8. <img width="587" height="593" alt="image" src="https://github.com/user-attachments/assets/7306cd0e-2933-4281-a8a4-5875685e7b2d" />
9. Click `Edit`
10. <img width="1434" height="253" alt="image" src="https://github.com/user-attachments/assets/2c772187-884f-4da6-99a2-17f2ff1933ac" />
11. Paste it into your `Redirect URL`
12. <img width="1177" height="363" alt="image" src="https://github.com/user-attachments/assets/1540c128-411a-46d0-b5fb-9162196546e7" />
13. Install python in your OS, google how to
14. `pip install -r requirements.txt`
15. Create `.env` file in this folder (eg: The folder this README.md is in)
16. Go to https://openapi.ctrader.com/apps
17. Click "Credentails"
18. Click "Sandbox"
19. Note down all these values
20. Put the following into the `.env` file
```
APP_CLIENT_ID="xxx"
APP_CLIENT_SECRET="xxx"
ACCESS_TOKEN="xxx"
REFRESH_TOKEN="xxx"
ACCOUNT_TYPE="<put 'demo' or 'live', my coding only detects these 2 words, go into main.py and search for 'ACCOUNT_TYPE' keyword and you know what im saying>"
```
21. After that, to start the script, run `python main.py`
22. Read the console message, type `ProtoOAGetAccountListByAccessTokenReq` to get list of accounts available
23. Type `setAccount <ctidTraderAccountId>` to authenticate that account
24. Then type `help` to proceed with any commands you would like to try
25. Press `CTRL + D` to disconnect & terminate the program
26. Press `CTRL + D` if your script encountered some error and the script seems hang/freezed.
27. Many reason will cause it to hang/freezed, like
- Forgot to authenticate account before trigger some function that requires your account to be authenticated first.
- Type some command and forgot to pass in some required argument.
