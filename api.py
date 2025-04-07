from fastapi import FastAPI, HTTPException, Request
import json
from pydantic import BaseModel
import asyncio
import uvicorn
import ecdsa
import websockets
import time
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import hashlib
from cryptography.fernet import Fernet

load_dotenv()



NODE_KEY = os.getenv("NODE_KEY")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY").encode()

crypter = Fernet(ENCRYPT_KEY)

STORED_KEYS = {"596986a4c18db14e525e5cd447b339dcc520895d89e3209559fcee14500cc221d8293255837c0b977ec33b4cb6147f084ea1bfa7100ac239192b73fdfaa454e9": {"private_key":"3c5a4f6fea46d9d9a3c34a80e52dd8cbb825d67705c670954b08981a6de35973", "passcode": "0f478e67792ec74e381aa125fad3f8331ddf3b941daa212272f10dd887cfa194"}}

USERNAME_LOOKUP = {"de3p": "596986a4c18db14e525e5cd447b339dcc520895d89e3209559fcee14500cc221d8293255837c0b977ec33b4cb6147f084ea1bfa7100ac239192b73fdfaa454e9"}


class Settings(BaseSettings):
    openapi_url: str = ""
settings = Settings()
app = FastAPI(openapi_url=settings.openapi_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sign_transaction(private_key, transaction_obj):
	transaction = transaction_obj
	private_obj = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
	transaction["signature"] = private_obj.sign(json.dumps(transaction_obj, sort_keys=True).encode()).hex()
	return transaction



async def send_transaction(private_key, p):
	async with websockets.connect("ws://localhost:4200") as websocket:
		transaction = {"sender": p["sender"], "receiver": p["receiver"], "amount": p["amount"], "timestamp": str(time.time())}

		signed_transaction = sign_transaction(private_key, transaction)

		message = {"type": "new_transaction", "transaction": signed_transaction, "key": NODE_KEY}

		await websocket.send(crypter.encrypt(json.dumps(message).encode()))
		message_encrypted = await websocket.recv()
		message = crypter.decrypt(message_encrypted)
		data = json.loads(message)

		return data



async def request_balance(pub_key):
	async with websockets.connect("ws://localhost:4200") as websocket:

		message = {"type": "get_balance", "key": NODE_KEY, "wallet": pub_key}

		await websocket.send(crypter.encrypt(json.dumps(message).encode()))
		message_encrypted = await websocket.recv()
		message = crypter.decrypt(message_encrypted)
		data = json.loads(message)

		return data



class SendCoin(BaseModel):
	amount: int
	sender: str
	receiver: str
	passcode: str
@app.post("/send_coin")
async def send_coin(data: SendCoin):

	sender_key = USERNAME_LOOKUP.get(data.sender, data.sender)

	receiver_key = USERNAME_LOOKUP.get(data.receiver, data.receiver)


	r = {
		"amount": data.amount,
		"sender" : sender_key,
		"receiver": receiver_key,
		"passcode": data.passcode
	}
	try:
		if STORED_KEYS[sender_key]["passcode"] == hashlib.sha256(data.passcode.encode()).hexdigest():

			result = await send_transaction(STORED_KEYS[sender_key]["private_key"], r)
			return result
		return {"message": "incorrect passcode!"}
	except:
		raise HTTPException(status=401)
	

class Register(BaseModel):
	passcode: str
	username: str
@app.post("/register")
async def register(data: Register):
	try:
		private = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

		private_key = private.to_string().hex()
		public_key = private.verifying_key.to_string().hex()


		if data.username in USERNAME_LOOKUP:
			return {"status": "username already exist"}

		STORED_KEYS[str(public_key)] = {"private_key":str(private_key), "passcode": hashlib.sha256(data.passcode.encode()).hexdigest()}
		USERNAME_LOOKUP[str(data.username)] = str(public_key)
		return {"key": str(public_key), "status": "OK"}
	except:
		raise HTTPException(status=401)


@app.get("/balance/{wallet}")
async def register(wallet: str):
	try:
		wallet_key = USERNAME_LOOKUP.get(wallet, wallet)

		result = await request_balance(wallet_key)
		return result
	except:
		raise HTTPException(status=401)


async def main():
	config = uvicorn.Config(app, host="0.0.0.0", port=5000)
	server = uvicorn.Server(config)
	print("server is running...")
	await server.serve()


if __name__ == "__main__":
	asyncio.run(main())