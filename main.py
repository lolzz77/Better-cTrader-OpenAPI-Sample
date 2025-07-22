#!/usr/bin/env python

from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from ctrader_open_api.endpoints import EndPoints
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
from inputimeout import inputimeout, TimeoutOccurred
import webbrowser
import datetime
import calendar
import threading
import queue
import os
from dotenv import load_dotenv
import inspect

# For logging use
filename = os.path.basename(inspect.getfile(inspect.currentframe()))

# Any command inputted by user, to be put into this queue.
# 2nd thread will always query from this queue & process
# command.
g_command_queue = queue.Queue()

# A variable to tell when `Command (ex help)` can start.
# Because we have to wait for connection success first.
CONNECTION_HAS_COMPLETED = False

# Only trigger user command input function, after this
# variable tells it to trigger
COMMAND_PROCESSED = True

# For ProtoOASubscribeSpotsReq, server will keep sending data
# Wait until unsubscribed then only trigger user input command
UNSUBSCRIBED = True

# Find `.env` and load the data into OS environment
load_dotenv()

if __name__ == "__main__":
    currentAccountId    = None
    appClientId         = os.getenv("APP_CLIENT_ID")
    appClientSecret     = os.getenv("APP_CLIENT_SECRET")
    accessToken         = os.getenv("ACCESS_TOKEN")
    hostType            = os.getenv("ACCOUNT_TYPE")
    hostType            = hostType.lower()

    while hostType != "live" and  hostType != "demo":
        print(f"{hostType} is not a valid host type.")
        hostType = input("Host (Live/Demo): ")

    client = Client(EndPoints.PROTOBUF_LIVE_HOST if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

    def connected(client): # Callback for client connection
        print(f"\n[{filename}:{inspect.currentframe().f_lineno}] Connected")
        request = ProtoOAApplicationAuthReq()
        request.clientId = appClientId
        request.clientSecret = appClientSecret
        deferred = client.send(request)
        deferred.addErrback(onError)

    def disconnected(client, reason): # Callback for client disconnection
        print(f"\n[{filename}:{inspect.currentframe().f_lineno}] Disconnected: ", reason)

    def onMessageReceived(client, message): # Callback for receiving all messages
        global CONNECTION_HAS_COMPLETED
        global COMMAND_PROCESSED
        global UNSUBSCRIBED

        # List of ignored message
        if message.payloadType in [ProtoOASubscribeSpotsRes().payloadType, ProtoOAAccountLogoutRes().payloadType, ProtoHeartbeatEvent().payloadType]:
            return

        elif message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print(f"[{filename}:{inspect.currentframe().f_lineno}] API Application authorized")
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Now please use `ProtoOAGetAccountListByAccessTokenReq` command to get list of accounts")
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Then, run command `setAccount <ctidTraderAccountId> to authorize that account")
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Type `help` for more helps")
            if currentAccountId is not None:
                sendProtoOAAccountAuthReq()
                return
            CONNECTION_HAS_COMPLETED = True

        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            protoOAAccountAuthRes = Protobuf.extract(message)
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Account {protoOAAccountAuthRes.ctidTraderAccountId} has been authorized")
            print(f"[{filename}:{inspect.currentframe().f_lineno}] This acccount will be used for all future requests")
            print(f"[{filename}:{inspect.currentframe().f_lineno}] You can change the account by using setAccount command")
            CONNECTION_HAS_COMPLETED = True

        elif message.payloadType == ProtoOAUnsubscribeSpotsRes().payloadType:
            print(f"[{filename}:{inspect.currentframe().f_lineno}] sendProtoOAUnsubscribeSpotsReq is ran. Unsubscribed.")
            UNSUBSCRIBED = True

        else:
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Message received: \n", Protobuf.extract(message))

        COMMAND_PROCESSED = True

    def onError(failure): # Call back for errors
        print(f"[{filename}:{inspect.currentframe().f_lineno}] Message Error: ", failure)

    def showHelp():
        global COMMAND_PROCESSED
        print("\n")
        print("List of Commands (Parameters with an * are required), those with '()' are descriptions.")
        print("1.  setAccount <*accountId>")
        print("2.  ProtoOAVersionReq")
        print("3.  ProtoOAGetAccountListByAccessTokenReq")
        print("4.  ProtoOAAssetListReq")
        print("5.  ProtoOAAssetClassListReq")
        print("6.  ProtoOASymbolCategoryListReq")
        print("7.  ProtoOASymbolsListReq <includeArchivedSymbols(True/False)>")
        print("8.  ProtoOATraderReq")
        print("9.  ProtoOASubscribeSpotsReq <*symbolId> <*timeInSeconds(Unsubscribes after this time)> <subscribeToSpotTimestamp(True/False)>")
        print("10. ProtoOAReconcileReq")
        print("11. ProtoOAGetTrendbarsReq <*weeks> <*period> <*symbolId>")
        print("12. ProtoOAGetTickDataReq <*days> <*type> <*symbolId>")
        print("13. NewMarketOrder <*symbolId> <*tradeSide> <*volume>")
        print("14. NewLimitOrder <*symbolId> <*tradeSide> <*volume> <*price>")
        print("15. NewStopOrder <*symbolId> <*tradeSide> <*volume> <*price>")
        print("16. ClosePosition <*positionId> <*volume>")
        print("17. CancelOrder <*orderId>")
        print("18. DealOffsetList <*dealId>")
        print("19. GetPositionUnrealizedPnL")
        print("20. OrderDetails")
        print("21. OrderListByPositionId <*positionId> <fromTimestamp> <toTimestamp>")
        COMMAND_PROCESSED = True

    def setAccount(accountId):
        global currentAccountId
        if currentAccountId is not None:
            sendProtoOAAccountLogoutReq()
        currentAccountId = int(accountId)
        sendProtoOAAccountAuthReq()

    def sendProtoOAVersionReq(clientMsgId = None):
        request = ProtoOAVersionReq()
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetAccountListByAccessTokenReq(clientMsgId = None):
        request = ProtoOAGetAccountListByAccessTokenReq()
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAccountLogoutReq(clientMsgId = None):
        request = ProtoOAAccountLogoutReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAccountAuthReq(clientMsgId = None):
        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = currentAccountId
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAssetListReq(clientMsgId = None):
        request = ProtoOAAssetListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAssetClassListReq(clientMsgId = None):
        request = ProtoOAAssetClassListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASymbolCategoryListReq(clientMsgId = None):
        request = ProtoOASymbolCategoryListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASymbolsListReq(includeArchivedSymbols = False, clientMsgId = None):
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = currentAccountId
        request.includeArchivedSymbols = includeArchivedSymbols if type(includeArchivedSymbols) is bool else bool(includeArchivedSymbols)
        deferred = client.send(request)
        deferred.addErrback(onError)

    def sendProtoOATraderReq(clientMsgId = None):
        request = ProtoOATraderReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAUnsubscribeSpotsReq(symbolId, clientMsgId = None):
        request = ProtoOAUnsubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASubscribeSpotsReq(symbolId, timeInSeconds, subscribeToSpotTimestamp	= False, clientMsgId = None):
        global UNSUBSCRIBED
        UNSUBSCRIBED = False
        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        request.subscribeToSpotTimestamp = subscribeToSpotTimestamp if type(subscribeToSpotTimestamp) is bool else bool(subscribeToSpotTimestamp)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)
        reactor.callLater(int(timeInSeconds), sendProtoOAUnsubscribeSpotsReq, symbolId)

    def sendProtoOAReconcileReq(clientMsgId = None):
        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetTrendbarsReq(weeks, period, symbolId, clientMsgId = None):
        request = ProtoOAGetTrendbarsReq()
        request.ctidTraderAccountId = currentAccountId
        request.period = ProtoOATrendbarPeriod.Value(period)
        request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=int(weeks))).utctimetuple())) * 1000
        request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
        request.symbolId = int(symbolId)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetTickDataReq(days, quoteType, symbolId, clientMsgId = None):
        request = ProtoOAGetTickDataReq()
        request.ctidTraderAccountId = currentAccountId
        request.type = ProtoOAQuoteType.Value(quoteType.upper())
        request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(days=int(days))).utctimetuple())) * 1000
        request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
        request.symbolId = int(symbolId)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOANewOrderReq(symbolId, orderType, tradeSide, volume, price = None, clientMsgId = None):
        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId = int(symbolId)
        request.orderType = ProtoOAOrderType.Value(orderType.upper())
        request.tradeSide = ProtoOATradeSide.Value(tradeSide.upper())
        request.volume = int(volume) * 100
        if request.orderType == ProtoOAOrderType.LIMIT:
            request.limitPrice = float(price)
        elif request.orderType == ProtoOAOrderType.STOP:
            request.stopPrice = float(price)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendNewMarketOrder(symbolId, tradeSide, volume, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "MARKET", tradeSide, volume, clientMsgId = clientMsgId)

    def sendNewLimitOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "LIMIT", tradeSide, volume, price, clientMsgId)

    def sendNewStopOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "STOP", tradeSide, volume, price, clientMsgId)

    def sendProtoOAClosePositionReq(positionId, volume, clientMsgId = None):
        request = ProtoOAClosePositionReq()
        request.ctidTraderAccountId = currentAccountId
        request.positionId = int(positionId)
        request.volume = int(volume) * 100
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOACancelOrderReq(orderId, clientMsgId = None):
        request = ProtoOACancelOrderReq()
        request.ctidTraderAccountId = currentAccountId
        request.orderId = int(orderId)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOADealOffsetListReq(dealId, clientMsgId=None):
        request = ProtoOADealOffsetListReq()
        request.ctidTraderAccountId = currentAccountId
        request.dealId = int(dealId)
        deferred = client.send(request, clientMsgId=clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetPositionUnrealizedPnLReq(clientMsgId=None):
        request = ProtoOAGetPositionUnrealizedPnLReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId=clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAOrderDetailsReq(orderId, clientMsgId=None):
        request = ProtoOAOrderDetailsReq()
        request.ctidTraderAccountId = currentAccountId
        request.orderId = int(orderId)
        deferred = client.send(request, clientMsgId=clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAOrderListByPositionIdReq(positionId, fromTimestamp=None, toTimestamp=None, clientMsgId=None):
        request = ProtoOAOrderListByPositionIdReq()
        request.ctidTraderAccountId = currentAccountId
        request.positionId = int(positionId)
        deferred = client.send(request, fromTimestamp=fromTimestamp, toTimestamp=toTimestamp, clientMsgId=clientMsgId)
        deferred.addErrback(onError)

    commands = {
        "help": showHelp,
        "setAccount": setAccount,
        "ProtoOAVersionReq": sendProtoOAVersionReq,
        "ProtoOAGetAccountListByAccessTokenReq": sendProtoOAGetAccountListByAccessTokenReq,
        "ProtoOAAssetListReq": sendProtoOAAssetListReq,
        "ProtoOAAssetClassListReq": sendProtoOAAssetClassListReq,
        "ProtoOASymbolCategoryListReq": sendProtoOASymbolCategoryListReq,
        "ProtoOASymbolsListReq": sendProtoOASymbolsListReq,
        "ProtoOATraderReq": sendProtoOATraderReq,
        "ProtoOASubscribeSpotsReq": sendProtoOASubscribeSpotsReq,
        "ProtoOAReconcileReq": sendProtoOAReconcileReq,
        "ProtoOAGetTrendbarsReq": sendProtoOAGetTrendbarsReq,
        "ProtoOAGetTickDataReq": sendProtoOAGetTickDataReq,
        "NewMarketOrder": sendNewMarketOrder,
        "NewLimitOrder": sendNewLimitOrder,
        "NewStopOrder": sendNewStopOrder,
        "ClosePosition": sendProtoOAClosePositionReq,
        "CancelOrder": sendProtoOACancelOrderReq,
        "DealOffsetList": sendProtoOADealOffsetListReq,
        "GetPositionUnrealizedPnL": sendProtoOAGetPositionUnrealizedPnLReq,
        "OrderDetails": sendProtoOAOrderDetailsReq,
        "OrderListByPositionId": sendProtoOAOrderListByPositionIdReq,
    }

    def User_Disconnect(clientMsgId=None): # disconnect the client
        client.stopService()
        reactor.callLater(3, callable=terminate_script)

    def terminate_script():
        """
        Terminate the script forcefully
        """
        os._exit(0)

    def GetUserCommand():
        global COMMAND_PROCESSED
        global UNSUBSCRIBED
        while CONNECTION_HAS_COMPLETED == False:
            continue

        try:
            while True:
                while COMMAND_PROCESSED and UNSUBSCRIBED:
                    userInput = input("\nCommand (ex help): ")
                    print(f"Command typed: {userInput}")
                    COMMAND_PROCESSED = False
                    g_command_queue.put(userInput) # Put them into queue for processUserCommand()
        except KeyboardInterrupt:
            """
            Attempted to detect CTRL + C but sadly,
            CTRL + C is only detected for main thread
            which is started by `reactor.run()`
            """
            print(f"[{filename}:{inspect.currentframe().f_lineno}] CTRL C is pressed")
        except EOFError:
            """
            Detect CTRL + D
            """
            print(f"[{filename}:{inspect.currentframe().f_lineno}] Disconnect & Terminate script")
            User_Disconnect()

    def processUserCommand():
        global COMMAND_PROCESSED
        while True:
            userInput = g_command_queue.get() # Get command from queue
            userInputSplit = userInput.split(" ")
            if not userInputSplit:
                print(f"[{filename}:{inspect.currentframe().f_lineno}] Command split error")
                COMMAND_PROCESSED = True
                continue
            command = userInputSplit[0]
            try:
                parameters = [parameter if parameter[0] != "*" else parameter[1:] for parameter in userInputSplit[1:]]
            except:
                print(f"[{filename}:{inspect.currentframe().f_lineno}] Invalid parameters")
                COMMAND_PROCESSED = True
                continue
            if command in commands:
                try:
                    commands[command](*parameters)
                except TypeError as e:
                    print(f"[{filename}:{inspect.currentframe().f_lineno}] {e}")
                    print(f"""[{filename}:{inspect.currentframe().f_lineno}] Possible causes:
1. You did not authorize your account set, run `setAccount <ctidTraderAccountId>`
2. Missong or wrong parameter given to the command
3. The command is outdated, check their documentation""")
                    COMMAND_PROCESSED = True
                    continue
            else:
                print(f"[{filename}:{inspect.currentframe().f_lineno}] Invalid Command, try `help`")
                COMMAND_PROCESSED = True
                continue
            


    # Start a new thread that handle user input command
    thread_user_input = threading.Thread(target=GetUserCommand)
    thread_user_input.start()

    # Start a new thread that handle command input-ed by user
    thread_process_command = threading.Thread(target=processUserCommand)
    thread_process_command.start()

    # Setting optional client callbacks
    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(onMessageReceived)
    # Starting the client service
    client.startService()

    # Start the main thread
    reactor.run()