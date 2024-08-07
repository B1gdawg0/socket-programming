import json

STATUS_CODE = {
    200: "OK",
    201: "Created",
    400: "Login failure",
    401: "Bad Request",
    402: "Username is already use",
    403: "Register failure",
    404: "Not Found",
    405: "Undefind error",
    500: "Internal Server Error"
}

COMMAND = {
    "/LOGIN": 800,
    "/LOGOUT": 801,
    "/REGISTER":802,
    "/DISCONNECT": 803,
}

def create_request(command, data=""):
    if (command in COMMAND):
        return json.dumps({
            "command_status":COMMAND[command],
            "command":command,
            "data":data
        })
    return json.dumps({400, command, data})

def parse_request(request):
    if request:
        request = json.loads(request)
        command_status = request["command_status"]
        command = request["command"]
        data = request["data"]
        return command_status, command, data
    return 405, STATUS_CODE[405], ""

def create_message(code, data=""):
    if (code in STATUS_CODE):
        return json.dumps(
            {
            "status_code": code,
            "status_message": STATUS_CODE[code],
            "data": data
            }
        )
    return json.dumps({"status_code":405, "status_message":STATUS_CODE[405], "data":data})

def parse_message(message):
    if message:
        message = json.loads(message)
        code = message["status_code"]
        status_message = message["status_message"]
        data = message["data"]
        
        return code, status_message, data
    return 405, STATUS_CODE[405], ""