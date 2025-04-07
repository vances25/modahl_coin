import time
import hashlib
import json
import websockets
import asyncio
import socket
from motor.motor_asyncio import AsyncIOMotorClient
import ecdsa
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()



NODE_KEY = os.getenv("NODE_KEY")
MINNER_KEY = os.getenv("MINNER_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY").encode()


print(NODE_KEY)
print(MINNER_KEY)
print(DATABASE_URL)

class Blockchain():
    def __init__(self, peer=None):

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                print(local_ip)
                self.ip = str(local_ip)
        except:
            self.ip = "0.0.0.0"


        self.database = AsyncIOMotorClient(DATABASE_URL)
        self.crypter = Fernet(ENCRYPT_KEY)
        self.pending = {}
        self.nodes = set([])
        self.minners = set()
        self.peer = peer

    async def sync(self):
        if self.peer:
            print(f"syncing node to {self.peer}")
            await self._sync_nodes(self.peer)
            await self._get_full_blockchain(self.peer)
        else:
            GOD_WALLET_PUBLIC = "596986a4c18db14e525e5cd447b339dcc520895d89e3209559fcee14500cc221d8293255837c0b977ec33b4cb6147f084ea1bfa7100ac239192b73fdfaa454e9"
            god_transaction = {"sender":"god", "receiver": GOD_WALLET_PUBLIC, "amount": 20}
            hashed_name = hashlib.sha256(json.dumps(god_transaction,sort_keys=True).encode()).hexdigest()

            print("creating a foundation block")
            if not await self.database["coin"]["blockchain"].find_one(projection={"_id": 0}):
                number = 0
                while True:
                    number += 1
                    block = {"index": 0, "timestamp": int(time.time()), "transactions": {hashed_name: god_transaction}, "previous_hash": "000000000000000000", "nonce": number}
                    block["timestamp"] = int(time.time())
                    block["nonce"] = number
                    block_hash = self._hash_json(block)
                    if block_hash[:5] == "00000":
                        await self.database["coin"]["blockchain"].insert_one(block)
                        break

    async def _get_full_blockchain(self, peer):
        print(f"getting blockchain from {peer}")
        async with websockets.connect(f"ws://{peer}:4200") as websocket:
            await websocket.send(self.crypter.encrypt(json.dumps({"type": "request_blockchain", "key": NODE_KEY}, sort_keys=True).encode()))
            while True:
                response_encrypted = await websocket.recv()
                response = self.crypter.decrypt(response_encrypted).decode()

                if response == "END_BLOCKCHAIN":
                    break

                block = json.loads(response)
                if not await self.database["coin"]["blockchain"].find_one({"index": block["index"]}):
                    await self.database["coin"]["blockchain"].insert_one(block)
                    print(f"added block the the database #{block['index']}")

    def _verify_transaction(self, transaction):
        print("verifing transaction")
        sender = transaction["sender"]
        signature = bytes.fromhex(transaction["signature"])
        transaction_data = transaction.copy()
        del transaction_data["signature"]
        
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        
        try:
            public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(sender), curve=ecdsa.SECP256k1)
            print("valid transaction")
            return public_key.verify(signature, transaction_string.encode())
        except Exception as e:
            print(e)
            print("invalid transaction")
            return False

    async def _sync_nodes(self, peer):
        print("syncing node....")
        async with websockets.connect(f"ws://{peer}:4200") as websocket:
            await websocket.send(self.crypter.encrypt(json.dumps({"type": "pair_node", "key": NODE_KEY}, sort_keys=True).encode()))

            response_encrypted = await websocket.recv()
            response = self.crypter.decrypt(response_encrypted).decode()

            data = json.loads(response)
            print(data)
            if data["type"] == "pair_node":
                self.nodes = set(data["all_nodes"])
                self.nodes.add(peer)
                self.pending = data["pending"]

    async def _broadcast_nodes(self, json_data):
        print("starting to broadcasting")
        nodes = self.nodes
        if "block" in json_data and "_id" in json_data["block"]:
            del json_data["block"]["_id"]
        json_data["key"] = NODE_KEY

        for ip in nodes.copy():
            try:
            	if ip != self.ip:
	                print(f"trying {ip}....")
	                async with websockets.connect(f"ws://{ip}:4200") as websocket:
	                    await websocket.send(self.crypter.encrypt(json.dumps(json_data, sort_keys=True).encode()))
	                    print(f"{ip} was worked!!")
            except asyncio.TimeoutError:
                print(f"Timeout error when connecting to {ip}")
            except Exception as e:
                print(f"Error in broadcasting: {e}")

    async def prune_nodes(self):
        while True:
            print(self.pending)
            for node in list(self.nodes):
            	if node != self.ip:
		            print(f"sending heartbeat to {node}")
		            try:
		                async with websockets.connect(f"ws://{node}:4200") as ws:
		                    await ws.send(self.crypter.encrypt(json.dumps({"type": "ping", "key": NODE_KEY}, sort_keys=True).encode()))
		                    await ws.recv()
		                    print(f"heartbeat got back from {node}")
		                    self.nodes.add(node)
		            except:
		                self.nodes.discard(node)
		                print(f"discarding node {node}")
            await asyncio.sleep(5)

    async def _verify_wallet_balance(self, wallet):
        balance = 0

        blocks = await self.database["coin"]["blockchain"].find({}, {"transactions": 1, "_id": 0}).to_list(None)
        for block in blocks:
            transactions = block["transactions"]

            for tx_id in transactions:
                sender = transactions[tx_id]["sender"]
                receiver = transactions[tx_id]["receiver"]
                amount_sent = transactions[tx_id]["amount"]

                # Subtract amount if wallet is sender
                if sender == wallet:
                    balance -= amount_sent

                # Add amount if wallet is receiver
                if receiver == wallet:
                    balance += amount_sent

        pending_transaction = self.pending

        for tx_id in pending_transaction:
            sender = pending_transaction[tx_id]["sender"]
            receiver = pending_transaction[tx_id]["receiver"]
            amount_sent = pending_transaction[tx_id]["amount"]

            if sender == wallet:
                balance -= amount_sent

            if receiver == wallet:
                balance += amount_sent
        print(balance)
        return balance

    async def _broadcast_minners(self, json_data):
        print("doing the minning shit")
        nodes = self.minners
        json_data["key"] = MINNER_KEY
        for ip in nodes.copy():
            print(f"SENDING TO {ip}")
            try:
            	if ip != self.ip:
	                async with websockets.connect(f"ws://{ip}:9090") as websocket:
	                    await websocket.send(self.crypter.encrypt(json.dumps(json_data, sort_keys=True).encode()))
	                    print("✅ Broadcast message sent!")
            except asyncio.TimeoutError:
                self.minners.discard(ip)
                print(f"Timeout error when connecting to {ip}")
            except Exception as e:
                self.minners.discard(ip)
                print(f"Error in broadcasting: {e}")

    def _hash_json(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    async def broadcast_new_block(self, block):
        if block:
            data = {
                "type": "update_blockchain",
                "block": block
            }
            await self._broadcast_nodes(data)

    async def start_server(self):
        async def handle_request(websocket):
            request_ip = None
            try:
                response_encrypted = await websocket.recv()
                message = self.crypter.decrypt(response_encrypted).decode()
                data = json.loads(message)
                request_ip = websocket.remote_address[0]
                match data["type"]:
                    case "request_blockchain":
                        if data["key"] == NODE_KEY:
                            print("blockchain has been requested")
                            blockchain_cursor = self.database["coin"]["blockchain"].find({},projection={"_id": 0}).sort("index", 1)
                            something_blockchain = await blockchain_cursor.to_list(None)
                            for block in something_blockchain:
                                await websocket.send(self.crypter.encrypt(json.dumps(block, sort_keys=True).encode()))
                                await asyncio.sleep(0.01)
                            await websocket.send(self.crypter.encrypt("END_BLOCKCHAIN".encode()))

                    case "pair_node":
                        if data["key"] == NODE_KEY:
                            print(f"node {request_ip} has joined chain")
                            self.nodes.add(request_ip)
                            await websocket.send(self.crypter.encrypt(json.dumps({"type": "pair_node", "all_nodes": list(self.nodes), "pending": self.pending}, sort_keys=True).encode()))
                    case "update_blockchain":
                        if data["key"] == NODE_KEY:
                            print("update blockchain request from other node")
                            block = data["block"]
                            if not await self.database["coin"]["blockchain"].find_one({"index": block["index"]}, projection={"_id": 0}):
                                await self.database["coin"]["blockchain"].insert_one(block)
                                for tx in block["transactions"]:
                                    print(f"DELETING: {tx}")
                                    del self.pending[tx]
                                await asyncio.gather(
                                self._broadcast_minners({"type": "update_block"}),
                                self._broadcast_nodes({"block": block, "type": "update_blockchain"})
                                )
                            else:
                                print(f"⚠️ Duplicate block {block['index']} rejected.")

                    case "submit_block":
                        if data["key"] == MINNER_KEY:
                            print("block has been submitted!!!")
                            hashed_block = self._hash_json(data["block"])
                            if hashed_block[:5] == "00000":
                                print("-"*100)
                                print(data["block"]["transactions"])
                                for tx in data["block"]["transactions"]:
                                    print(f"DELETING: {tx}")
                                    del self.pending[tx]
                                print("BLOCK IS VALID TIME FOR NEW ONE")
                                await self.database["coin"]["blockchain"].insert_one(data["block"])
                                await asyncio.gather(
                                self._broadcast_minners({"type": "update_block"}),
                                self.broadcast_new_block(data["block"])
                                )
                    case "request_mine":
                        if data["key"] == MINNER_KEY:
                            print("a minner has requested to mine")
                            self.minners.add(request_ip)
                            print("minner requested block")
                            last_block = await self.database["coin"]["blockchain"].find_one(sort=[("index", -1)], projection={"_id": 0})
                            current_block = {"index": last_block["index"] + 1, "timestamp": None, "transactions": self.pending, "previous_hash": self._hash_json(last_block), "nonce": None}
                            if len(self.pending) != 0:
                                await websocket.send(self.crypter.encrypt(json.dumps(current_block, sort_keys=True).encode()))
                            else:
                                await websocket.send(self.crypter.encrypt("NONE".encode()))
                    case "update_transaction":
                        if data["key"] == NODE_KEY:
                            print("new transaction added")
                            transaction = data["data"]

                            transaction_hash = self._hash_json(transaction)
                            check_sign = self._verify_transaction(transaction)
                            balance = await self._verify_wallet_balance(transaction["sender"])
                            check_wallet_balance = False
                            if balance >= transaction["amount"]:
                                check_wallet_balance = True


                            if not check_sign:
                                print("invalid signature!!!")
                                return

                            if transaction_hash in self.pending:
                                print("duplicate transaction")
                                return

                            if not check_wallet_balance:
                                print("not enough funds..")
                                return


                            print("adding new transaction")
                            self.pending[transaction_hash] = transaction
                            await asyncio.gather(
                            self._broadcast_nodes({"type": "update_transaction", "data": transaction}),
                            self._broadcast_minners({"type": "update_block"})
                            )
                    case "get_balance":
                        if data["key"] == NODE_KEY:
                            print(f"retrieving balance of {data["wallet"]}")
                            balance = await self._verify_wallet_balance(data["wallet"])
                            await websocket.send(self.crypter.encrypt(json.dumps({"wallet": data["wallet"], "balance": balance}).encode()))
                    case "new_transaction":
                        if data["key"] == NODE_KEY:
                            print("a new transaction has been sent!")
                            transaction = data["transaction"]
                            transaction_hash = self._hash_json(transaction)
                            check_sign = self._verify_transaction(transaction)
                            balance = await self._verify_wallet_balance(transaction["sender"])
                            check_wallet_balance = False
                            if balance >= transaction["amount"]:
                                check_wallet_balance = True

                            add_transaction = True

                            print(f"HASH OF SHIT: {transaction_hash}")

                            if transaction["amount"] == 0:
                                add_transaction = False
                            if not check_sign:
                                print("invalid signature")
                                add_transaction = False

                            if transaction_hash in self.pending:
                                print("⚠️ Duplicate transaction rejected.")
                                add_transaction = False

                            if not check_wallet_balance:
                                print("not enough funds..")
                                add_transaction = False
   

                            if add_transaction:
                                print(f"REMAINING AMOUNT: {check_wallet_balance}")
                                print("valid signature!!!")
                                self.pending[transaction_hash] = transaction
                                await asyncio.gather(
                                self._broadcast_nodes({"type": "update_transaction", "data": transaction, "key": NODE_KEY}),
                                self._broadcast_minners({"type": "update_block"})
                                )
                                await websocket.send(self.crypter.encrypt(json.dumps({"amount": transaction["amount"], "sender": transaction["sender"], "receiver": transaction["receiver"], "status": "REDIRECT"}, sort_keys=True).encode()))
                            else:
                                await websocket.send(self.crypter.encrypt(json.dumps({"message": f"transaction failed, maybe cause of not enough funds?"}, sort_keys=True).encode()))

                    case "ping":
                        if data["key"] == NODE_KEY:
                            print(f"ping request from {request_ip}")
                            self.nodes.add(request_ip)
                            await websocket.send(b"")
                    case _:
                        pass
            except websockets.exceptions.ConnectionClosedError:
                print(f"❌ WebSocket connection with {request_ip} closed unexpectedly.")
                self.nodes.discard(request_ip)
            except websockets.exceptions.ConnectionClosedOK:
                print(f"✅ WebSocket connection with {request_ip} closed normally.")
                self.nodes.discard(request_ip)


        async with websockets.serve(handle_request, "0.0.0.0", 4200) as server:
            print("server is running")
            asyncio.create_task(self.prune_nodes())
            await server.wait_closed()

async def main():
    blockchain = Blockchain()
    await blockchain.database.drop_database("coin")
    await blockchain.sync()
    await blockchain.start_server()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
