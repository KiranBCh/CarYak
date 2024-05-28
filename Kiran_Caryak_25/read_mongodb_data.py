import pymongo
import argparse
from operator import itemgetter

name = "CarYak"
client = pymongo.MongoClient(f'mongodb://dbadmin:Tx5Yh9gYzq1@crawlerdbcluster.c3yhtms4nrye.us-east-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=/home/ubuntu/rds-combined-ca-bundle.pem')
db = client[name]

def readdata_mongodb(args):
    result = db["cars"].find({"batch_com": int(args.replace("args = ", ""))})
    return result

def olddata_mongodb(vin_number, source):
    result = db.cars.find({"vin_number": vin_number, "source": source, "success": "true"}, {"price": 1, "start_time": 1, "batch_com": 1}).sort([("start_time", 1)])
    raw_data = []
    newlist = []
    for data in result:
        raw_data.append({"OPrice": data.get("price", ""),
                             "ODate": str(data.get("start_time", "")),
                             "OBatchCom": str(data.get("batch_com", "999"))
                })
    if raw_data:
        newlist = sorted(raw_data, key=itemgetter('ODate'), reverse=True)[0]
    return newlist

def send_data_ui(args):
    final_offers1 = []
    data_raw = readdata_mongodb(args)
    for data in data_raw:
        final_offers = dict()
        final_offers.update({
            "trimList":None,
             "totalThread": None,
             "currentThread": None,
             "status": data.get("status", ""),
             "numberTries": data.get("numberTries", -1),
             "pythonMessage": None,
             "batchCom": data.get("batch_com"),
             "datetime": str(data.get("datetime")),
             "make": data.get("make", ""),
             "model": data.get("model"),
             "year": data.get("year"),
             "body_type": data.get("body_type"),
             "features": None,
             "price": str(data.get("price", 0.0)),
             "source": data.get("source"),
             "mileage": data.get("mileage"),
             "image_url": None,
             "trim": data.get("trim"),
             "condition": data.get("condition"),
             "vin_number": data.get("vin_number"),
             "success": data.get("success"),
             "ODate": "",
             "OBatchCom": "999",
             "activeOffer": str(False),
        })
        if data["success"] in "Already an active offer":
            old_results = olddata_mongodb(data["vin_number"], data["source"])
            if old_results:
                final_offers.update({
                    "price": str(old_results.get("OPrice", 0.0)),
                    "ODate": old_results.get("ODate", ""),
                    "OBatchCom": str(old_results.get("OBatchCom", "999")),
                    "activeOffer": str(True),
                })

        if data["source"] == "Driveway":
            if isinstance(data["source"], dict):
                final_offers.update({"condition": data["condition"]["overallCondition"] or ""})
            elif isinstance(data["source"], str):
                final_offers.update({"condition": data["condition"]})
        final_offers1.append(final_offers)
    print(final_offers1)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--batch_com",default="Please send batch_com number")
    args = parser.parse_args()
    if args.batch_com:
        send_data_ui(args.batch_com)
