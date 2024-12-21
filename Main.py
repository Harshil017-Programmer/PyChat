from flask import *
from flask_socketio import *
from string import *
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Harshil@1234'
socketio = SocketIO(app)

rooms = {}

def GUC(Length):
    while True:
        Code = ""
        for _ in range(Length):
            Code += random.choice(ascii_uppercase)

        if Code not in rooms:
            break
    return Code

@app.route("/",methods=["POST","GET"])

def Home():
    session.clear()
    if request.method == "POST":
        Name = request.form.get("name")
        Code = request.form.get("code")
        Join = request.form.get("join",False)
        Create = request.form.get("create",False)

        if not Name:
            return render_template("Home.html",Error="Please Enter a Name.",Code=Code,Name=Name)
        
        if Join != False and not Code:
            return render_template("Home.html",Error="Please Enter a Room Code.",Code=Code,Name=Name)

        Room = Code
        if Create != False:
            Room = GUC(4)
            rooms[Room] = {"Members":0,"Messages":[]}
        elif Code not in rooms:
            return render_template("Home.html",Error="Room Does Not Exist.",Code=Code,Name=Name)
        
        session["Room"] = Room
        session["Name"] = Name
        return redirect(url_for("Room"))
    

    return render_template("Home.html")

@app.route("/Room")
def Room():
    Room = session.get("Room")
    if Room is None or session.get("Name") is None or Room not in rooms:
        return redirect(url_for("Home"))
    
    return render_template("Room.html")

@socketio.on("connect")
def connect(auth):
    Room = session.get("Room")
    Name = session.get("Name")
    if not Room or not Name:
        return
    if Room not in rooms:
        leave_room(Room)
        return
    
    join_room(Room)
    send({"Name":Name,"message":"has joined the Room."},to=Room)
    rooms[Room]["Members"] += 1
    print(f"{Name} joined Room {Room}")

@socketio.on("disconnect")
def disconnect():
    Room = session.get("Room")
    Name = session.get("Name")
    leave_room(Room)

    if Room in rooms:
        rooms[Room]["Members"] -= 1
        if rooms[Room]["Members"] <= 0:
            del rooms[Room]

    send({"Name":Name,"message":"has left the Room."},to=Room)
    print(f"{Name} has left Room {Room}")

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",port=5000,debug=True)