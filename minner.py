import websockets
import asyncio
import json
import time
import hashlib
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()

MINNER_KEY = os.getenv("MINNER_KEY")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY").encode()

class Minner():
	def __init__(self, node_ip):
		self.server = node_ip
		self.is_minning = False
		self.current_block = None
		self.crypter = Fernet(ENCRYPT_KEY)

	async def _get_block(self):
		async with websockets.connect(f"ws://{self.server}:4200") as websocket:
			await websocket.send(self.crypter.encrypt(json.dumps({"type": "request_mine", "key": MINNER_KEY}).encode()))
			message_encrypted = await websocket.recv()
			print(message_encrypted)
			message = self.crypter.decrypt(message_encrypted).decode()
			print(message)
			if message != "NONE":
				print("WE ARE MINNING BABY")
				data = json.loads(message)
				self.current_block = data
				self.is_minning = True
			else:
				print("not minning rn")
				self.is_minning = False
				current_block = None
				await asyncio.sleep(1)

	def _hash_block(self, block):
		block_string = json.dumps(block,sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()


	async def _submit_block(self, block):
		async with websockets.connect(f"ws://{self.server}:4200") as websocket:
			await websocket.send(self.crypter.encrypt(json.dumps({"type": "submit_block", "block": block, "key": MINNER_KEY}).encode()))
			print(block)
			print("blocked submitted")


	async def mine(self):
		while True:
			if not self.is_minning:
				await asyncio.sleep(1)
				continue

			number = 0
			while self.is_minning:
				number += 1
				block = self.current_block
				block["timestamp"] = int(time.time())
				block["nonce"] = number
				block_hash = self._hash_block(block)
				if block_hash[:5] == "00000":
					if self.is_minning:
						await self._submit_block(block)
						await self._get_block()
						break
				await asyncio.sleep(0)

	async def start_server(self):
		async def handle_request(websocket):
			print("connection received")
			message_encrypted = await websocket.recv()
			message = self.crypter.decrypt(message_encrypted)

			data = json.loads(message)
			request_ip = websocket.remote_address[0]
			if "type" in data:
				print(data)
				match data["type"]:
					case "update_block":
						self.is_minning = False
						await self._get_block()
					case _:
						pass

		async with websockets.serve(handle_request, "0.0.0.0", 9090) as server:
			await asyncio.sleep(3)
			asyncio.create_task(self._get_block())
			await asyncio.sleep(3)
			asyncio.create_task(self.mine())
			print("server has started")
			await server.wait_closed()

if __name__ == "__main__":
	# asyncio.run(test())
	minner = Minner("170.187.181.247")
	asyncio.run(minner.start_server())