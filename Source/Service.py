import http.server, json
import logging, traceback, random
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from datetime import datetime, timedelta

class MyHTTPHandler(http.server.BaseHTTPRequestHandler):
    db = TinyDB('./virtualenv/Source/htt.json') #, storage=CachingMiddleware(JSONStorage))
    dbTable = db.table('OTPEngine')

    server_version = 'BasHTTP/1.9'
    sys_version = 'BasCGI/7.9'

    def _set_OK_headers(self):
        self.send_response(200, message="Successfully Processed")
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_FAILED_headers(self):
        self.send_response(500, message="Failed to process")
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_FAILED_headers()
        self.wfile.write(b'{"errorCode": "500", "errorMessage": "Service Not Available"}')
    
    def generateRandom(self, length=6):
        angka = random.randint(0, 999999999)
        hasil = str(format(angka, '09'))
        return hasil[len(hasil)-length:]

    def saveToDB(self, data):
        OtpRecord = Query()
      #  self.dbTable.insert(data)
        self.dbTable.upsert(data, 
            (OtpRecord.ApplicationId == data["ApplicationId"]) 
            & (OtpRecord.OTPIdentifier == data["OTPIdentifier"])) 
    
    def queryFromDB(self, data):
        OtpRecord = Query()
        identifier = data["OTPIdentifier"]
        applicationId = data["ApplicationId"]

        result = self.dbTable.search((OtpRecord.ApplicationId == applicationId) 
            & (OtpRecord.OTPIdentifier == identifier))
        if len(result) > 0: 
            return result[0]
        else:
            return None
    
    def updateToDB(self, data):
        OtpRecord = Query()
      #  self.dbTable.insert(data)
        self.dbTable.update(data, 
            (OtpRecord.ApplicationId == data["ApplicationId"]) 
            & (OtpRecord.OTPIdentifier == data["OTPIdentifier"])) 
    
    def moveToDefault(self, data):
        OtpRecord = Query()
        self.dbTable.remove( 
            (OtpRecord.ApplicationId == data["ApplicationId"]) 
            & (OtpRecord.OTPIdentifier == data["OTPIdentifier"])) 
        self.db.insert(data)

    def do_POST(self):
        lpath = str(self.path)
        contentLength = int(self.headers['Content-Length'])
        payload = self.rfile.read(contentLength)
        self.log_message('Path: %s Payload: %s', lpath, payload)

        try:
            jsondata = json.loads(payload)      
            #self.log_message(" JSONData: %s", jsondata)

            if lpath.startswith('/create'):
                applicationId = jsondata["ApplicationId"]
                duration = jsondata["OTPDuration"]
                length = jsondata["OTPLength"]
                identifier = jsondata["OTPIdentifier"]

                otp = self.generateRandom(length)

                self._set_OK_headers()
                respon = {'ApplicationId': applicationId,
                'OTPIdentifier': identifier,
                'OTPValue': otp,
                'errorCode': '200' }

                self.log_message('Path: %s Response: %s', lpath, respon)
                
                self.wfile.write(json.dumps(respon).encode())

                sekarang = datetime.now()
                internalData = {'RequestTime': sekarang.isoformat(),
                'Duration': duration,
                'ExpiryTime': (sekarang + timedelta(seconds=duration)).isoformat(),
                'ValidationRetries': 0}
                
                jsondata.update(respon)
                jsondata.update(internalData)
                
                self.saveToDB(data=jsondata)

                return

            elif lpath.startswith('/validate'):
                self._set_OK_headers()
                respon = {"OTPResult": "OTP Not Found", "errorCode": "404"}

                result = self.queryFromDB(jsondata)
                #self.log_message('Recorded: %s', result)
                if result==None: 
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return

                sekarang = datetime.now()
                expiry = datetime.fromisoformat(result["ExpiryTime"])
                if sekarang > expiry:
                    respon = {"OTPResult": "OTP Expired",  "errorCode": "403"}
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return
                
                validRetry = result.get("ValidationRetries")
                if validRetry == None:
                    respon.update({"ValidationRetries": 1})
                else:
                    respon.update({"ValidationRetries": validRetry+1})
                
                if respon["ValidationRetries"] > result.get("MaxValidation"):
                    respon.update({"OTPResult": "OTP Maximum Validation Reached", "errorCode": "402"})
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return
                
                if jsondata.get("OTPChallenge") == result.get("OTPValue"):
                    respon.update({"OTPResult": "OTP Valid", "errorCode": "200"})
                else:
                    respon.update({"OTPResult": "OTP Not Valid", "errorCode": "401"})
                respon.update(jsondata)
                
                self.log_message('Path: %s Response: %s', lpath, respon)
                self.wfile.write(json.dumps(respon).encode())

                result.update(respon)
                self.saveToDB(result)

                return

            elif lpath.startswith('/use'):
                self._set_OK_headers()
                respon = {"OTPResult": "OTP Not Found", "errorCode": "404"}

                result = self.queryFromDB(jsondata)
                #self.log_message('Recorded: %s', result)
                if result==None: 
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return

                sekarang = datetime.now()
                expiry = datetime.fromisoformat(result["ExpiryTime"])
                if sekarang > expiry:
                    respon = {"OTPResult": "OTP Expired", "errorCode": "403"}
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return
                
                validRetry = result.get("ValidationRetries")
                if validRetry == None:
                    respon.update({"ValidationRetries": 1})
                else:
                    respon.update({"ValidationRetries": validRetry+1})
                
                if respon["ValidationRetries"] > result.get("MaxValidation"):
                    respon.update({"OTPResult": "OTP Maximum Validation Reached", "errorCode": "402"})
                    respon.update(jsondata)
                    self.wfile.write(json.dumps(respon).encode())
                    return
                
                if jsondata.get("OTPChallenge") == result.get("OTPValue"):
                    respon.update({"OTPResult": "OTP Valid", "errorCode": "200"})
                    result.update({"UsedTime": datetime.now().isoformat()})
                else:
                    respon.update({"OTPResult": "OTP Not Valid", "errorCode": "401"})
                respon.update(jsondata)
                
                self.log_message('Path: %s Response: %s', lpath, respon)
                self.wfile.write(json.dumps(respon).encode())

                respon.update(result)
                
                self.moveToDefault(respon)

                return

        except Exception as ex:
            self._set_FAILED_headers()
            self.log_message('Exception occurs: %s', ex)
            self.wfile.write(b'{"errorCode": "500", "errorMessage": "Payload or Service failed "}')
            traceback.print_tb(ex.__traceback__)
        else:
            self._set_FAILED_headers()
            self.wfile.write(b'{"errorCode": "500", "errorMessage": "Payload or Service failed"}')
        
def run(server_class=http.server.ThreadingHTTPServer, handler_class=MyHTTPHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print("Starting service at "+str(port))
    httpd.serve_forever()        

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
