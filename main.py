from fastapi import FastAPI
import requests
from multiprocess import Process
import certifi
import motor
import motor.motor_asyncio
from bson import ObjectId
from random import choice

app = FastAPI()

username = "ideahack_2023" #"mongo"
password = "ideahack_2023"
mongo_db_connection_string = "mongodb+srv://" \
                             "{username}:{password}@cluster0.6wlzcsu.mongodb.net".format(username=username, password=password)

client = motor.motor_asyncio.AsyncIOMotorClient(mongo_db_connection_string, tlsCAFile=certifi.where())
db = client.debt24

print(db.list_collection_names())
# hardcoded for demonstrational purposes:
# bidwinner_entry_filter = { "_id": ObjectId("651f981f9404c50bc36d243b") }
object_id = "651f981f9404c50bc36d243b"

n_lenders = 3

def notify_nth_lender(n, amount, use_case, loan_time):
    url = f"https://ideahack2023-bank-c90e27b6acbe.herokuapp.com/{n}?amount={amount}&use_case={use_case}&loan_time={loan_time}"
    response = requests.post(url)
    return response.json()['interest_rate']

def auction_process(amount, use_case, loan_time):
    result = [notify_nth_lender(i, amount, use_case, loan_time) for i in range(n_lenders)]
    candidates = [i for i, c in enumerate(result) if c == min(result)]
    candidate = choice(candidates)
    print(db['offers'].update_one({"new_id": 0 }, {"$set": { "bidwinner": candidate } }))

@app.post("/request_credit")
async def request_credit(amount :int, use_case :str, loan_time :int):
    print(f"user request for {amount}$ credit (number of installments: {loan_time} months, purpose: {use_case}")
    Process(target=auction_process, args=(amount,use_case,loan_time)).start()
    return 200

@app.get("/auction_status")
async def auction_status():
    offer = await db['offers'].find_one({ "new_id": 0 })
    return { 'offer' : offer['bidwinner']  }

