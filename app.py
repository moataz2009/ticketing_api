from flask import Flask, json, request, jsonify, make_response
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import jwt
import datetime
import os
from zeep import Client


#initial app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sdWkq^jhe$2GHJaSsd@#$21D'

#init db
db = SQLAlchemy(app)
#init marshmallow (ma)
ma = Marshmallow(app)


# Ticket Model
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    sub_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    gender = db.Column(db.String(10))
    from_time = db.Column(db.String(100))
    to_time =  db.Column(db.String(100))
    ticket_date = db.Column(db.String(100))
    priority = db.Column(db.String(15))
    created_at = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    status = db.Column(db.String(15))
    reply = db.Column(db.Text)
    def __init__(self, type, sub_type, description, gender, from_time, to_time, ticket_date, priority, created_at, created_by, status, reply):
        self.type = type
        self.sub_type = sub_type
        self.description = description
        self.gender = gender
        self.from_time = from_time
        self.to_time = to_time
        self.ticket_date = ticket_date
        self.priority = priority
        self.created_at = created_at
        self.created_by = created_by
        self.status = status
        self.reply = reply

#ticket schema
class TicketSchema(ma.Schema):
    class Meta:
        fields = ('id', 'type', 'sub_type', 'description', 'gender', 'from_time', 'to_time', 'ticket_date', 'priority', 'created_at', 'created_by', 'status', 'reply')

#init schema 
ticket_schema   = TicketSchema()
tickets_schema  = TicketSchema(many = True)

@app.route('/login', methods=['POST'])
def login():

    client= Client("http://172.22.1.26/orgstructure/usersservice.asmx?wsdl").service.AuthinticationStatus(request.json['username'], request.json['password'])
    if client == True:
        
        getAllRoles = User_roles.query.filter_by(username = request.json['username']).all()
        result = usersRoles_schema.dump(getAllRoles)
        
        token = jwt.encode({'user': request.json['username'], 'roles': result, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300) }, app.config['SECRET_KEY'], algorithm="HS256")
        tokenDecode = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        
        return jsonify({'token': token, 'tokenDecode': tokenDecode})
    return jsonify({'status' : False})
 
   

#create ticket
@app.route('/ticket', methods=['POST'])
def add_ticket():
    type = request.json['type']
    sub_type = request.json['sub_type']
    description = request.json['description']
    gender = request.json['gender']
    from_time= request.json['from_time']
    to_time= request.json['to_time']
    ticket_date= request.json['ticket_date']
    priority= request.json['priority']
    created_at = request.json['created_at']
    created_by = request.json['created_by']
    status = "no"
    reply = ""

    new_ticket = Ticket(type, sub_type, description, gender, from_time, to_time, ticket_date, priority, created_at, created_by, status, reply)
    db.create_all()
    db.session.add(new_ticket)
    db.session.commit()

    return ticket_schema.jsonify(new_ticket)

@app.route('/ticket', methods=['GET'])
def get_tickets():
    all_tickets = Ticket.query.all()
    result = tickets_schema.dump(all_tickets)
    return jsonify(result)

@app.route('/my_ticket/<status>/', methods=['GET'])
def my_tickets(status):
    token = request.headers.get('authorization')

    try:
        tokenDecode = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        
    except:
        return jsonify({'message': 'Token Not valid', 'token': token})

    all_tickets = Ticket.query.filter_by(created_by = tokenDecode.get('user') ).filter_by(status = status) .all()
    result = tickets_schema.dump(all_tickets)
    return jsonify(result)

@app.route('/ticket/<id>', methods=['GET'])
def get_ticket(id):
    get_tickets = Ticket.query.get(id)
    return ticket_schema.jsonify(get_tickets)

@app.route('/ticket/<id>', methods=['DELETE'])
def delete_ticket(id):
    tickets = Ticket.query.get(id)
    if(tickets):
        db.session.delete(tickets)
        db.session.commit()

        return jsonify({ 'message' : 'Ticket id: (' + id + ') deleted successfully'})
    else:
        return jsonify({ 'message' : 'Ticket id: (' + id + ') notfound'})

@app.route('/ticket/<id>', methods=['PUT'])
def update_ticket(id):
    ticket = Ticket.query.get(id)
    type = request.json['type']
    sub_type = request.json['sub_type']
    description = request.json['description']
    gender = request.json['gender']
    from_time= request.json['from_time']
    to_time= request.json['to_time']
    ticket_date= request.json['ticket_date']
    priority= request.json['priority']
    status= request.json['status']
    reply= request.json['reply']


    created_by = request.json['created_by']

    #set new value
    ticket.type = type
    ticket.sub_type = sub_type
    ticket.description = description
    ticket.gender = gender
    ticket.from_time= from_time
    ticket.to_time= to_time
    ticket.ticket_date= ticket_date
    ticket.priority= priority
    ticket.status= status
    ticket.reply= reply

    db.session.commit()

    return ticket_schema.jsonify(ticket)

########################## User Section start #############################

# Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, username):
        self.username = username

#Users schema
class UesrSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username')

#init User schema
user_schema   = UesrSchema()
users_schema  = UesrSchema(many = True)

#Create users
@app.route('/user', methods=['POST'])
def add_user():
    username = request.json['username']

    new_user = Users(username)
    db.create_all()
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

#get all users
@app.route('/user', methods=['GET'])
def get_users():
    get_users = Users.query.all()
    return users_schema.jsonify(get_users)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = Users.query.get(id)
    if(user):
        db.session.delete(user)
        db.session.commit()

        return jsonify({ 'message' : 'user id: (' + id + ') deleted successfully'})
    else:
        return jsonify({ 'message' : 'user id: (' + id + ') notfound'})

###############################################################

#users roles
######################## User Roles Section start #############################

# Users Model
class User_roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    username =  db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)
    
    users = db.relationship('Users',
        backref=db.backref('user_roles', lazy=True))
    
    #db.Column(db.String(100))

    def __init__(self, username, role):
        self.username = username
        self.role = role

#Users schema
class User_rolesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'role')
        

#init User schema
userRoles_schema   = User_rolesSchema()
usersRoles_schema  = User_rolesSchema(many = True)

#Create and update users Roles
@app.route('/user-roles', methods=['POST'])
def add_userRoles():
    username = request.json['username']
    roles = request.json['roles']
    #jsonObject = json.loads(role)

    User_roles.query.filter_by(username = username).delete()    

    for role in roles:
        username = request.json['username']
        role = role['role']
        new_userRoles = User_roles(username, role )
        db.create_all()
        db.session.add(new_userRoles)
        db.session.commit()

    getAllRoles = User_roles.query.filter_by(username = username).all()
    result = usersRoles_schema.dump(getAllRoles)

    return jsonify(result)

#get all user Roles
@app.route('/user-roles/<username>', methods=['GET'])
def get_userRoles(username):
    getAllRoles = User_roles.query.filter_by(username = username).all()
    result = usersRoles_schema.dump(getAllRoles)

    return jsonify(result)


#Run Server
if __name__ == '__main__':
    app.run(debug=True)