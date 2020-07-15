from flask import *
import json
from flask_sqlalchemy import SQLAlchemy
import base64 

app = Flask('jsgrid-playground', template_folder='.')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://gusree:gunaSREE1@@db4free.net:3306/gusree_12'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Person(db.Model):
    Roll = db.Column(db.String(3), primary_key=True)
    Name= db.Column(db.String(45))
    Branch = db.Column(db.String(5))
    Section= db.Column(db.Integer)
    Year= db.Column(db.Integer)
    Semester= db.Column(db.Integer)
    Version= db.Column(db.Integer)

    def __init__(self,a,b,c,d,e,f,g):
        self.Roll = a
        self.Name = b
        self.Branch=c
        self.Section=d
        self.Year=e
        self.Semester=f
        self.Version=g

class Itemcount(db.Model):
    count= db.Column(db.Integer,primary_key=True)
    def __init__(self,a):
        self.count = a
#converts a row to dict
def convertrow_to_dict(x):
    d=dict()
    d['Roll number']=x.Roll
    d['Name']=x.Name
    d['Branch']=x.Branch
    d['Section']=x.Section
    d['Year']=x.Year
    d['Semester']=x.Semester
    d['Version']=x.Version
    return d

class People(db.Model):
    name = db.Column(db.String(80), nullable=False)
    email = db. Column(db.String(250), nullable=False,primary_key = True)
    dob=db.Column(db.String(12), nullable=False)
    color=db.Column(db.String(8), nullable=False)
    image =db.Column(db.LargeBinary, nullable = False)
    version= db.Column(db.Integer)
    def __init__(self,a,b,c,d,e,f):
        self.name=a
        self.email=b 
        self.dob=c 
        self.color=d
        self.image=e
        self.version=f

class Countitem(db.Model):
    count= db.Column(db.Integer,primary_key=True)
    def __init__(self,a):
        self.count = a
#converts a row to dict
def convert_row_to_dict(x):
    d=dict()
    d['Name']=x.name
    d['Email']=x.email
    d['Date of birth']=x.dob
    d['Color']=x.color
    d['Photo']=str(base64.encodebytes(x.image))
    d['Version']=x.version
    return d

@app.route('/DataHandler', methods=['GET',])
def getdata():
    #print(request.json['pageIndex'])
    print(request.json)
    my_dict=request.args
    for key in my_dict:
        print(key,my_dict[key])
    print(request.url)
    print(request.query_string)
    i=(int(request.args['pageIndex'])-1)*int(request.args['pageSize'])
    j=i+int(request.args['pageSize'])
    count=People.query.slice(i,j).all()
    #converting rows brought from database to list of dicts
    arr=list(map(convert_row_to_dict,count))
    ct=Countitem.query.all()
    #print(arr,ct[0].count)
    return jsonify({'data':arr,'itemsCount':ct[0].count})


@app.route('/DataHandler', methods=['PUT',])
def updatedata():
    print(request.json)
    print(request.query_string)
    """
    1.Access roll number,name,branch,section,year,semester,version
    2.Retrive row say x from database having roll number same as from request
    3.If the version number of x and from request matches,increment version number 
       and update row in database
       For eg:Roll number:529 Name:x Section:CSE Year:1 Semester:1 Version:1 -from request
       Roll number:529 Name:x Section:ECE Year:1 Semester:1 Version:1-database retrieved
       Using update query update in database 
       Row in database should be
       Roll number:529 Name:x Section:CSE Year:1 Semester:1 Version:2
       Return jsonify of above row 
       this shold be returned
     { "Branch": "5", "Name": "5", "Roll Number": "5", "Section": 5, "Semester": 5, "Version": 1, "Year": 5}
    4.If version number is not equal return jsonify({'Sucess':"Try again"})   
       """
    l={'Date of birth':'dob','Email':'email','Name':'name','Photo':'image','Color':'color','Version':'version'}
    old_row=request.json['old']
    new_row=request.json['new']
    person = People.query.filter_by(email=old_row['Email']).first()
    if person.version==old_row['Version']:
        to_update=dict()
        for x in old_row.keys():
            if(x!='Email'):
                if(x=='Version'):
                    to_update[l[x]]=old_row[x]+1
                else:
                    if(old_row[x]!=new_row[x]):
                        to_update[l[x]]=new_row[x]
        People.query.filter_by(email=old_row['Email']).update(to_update)
        db.session.commit()
        new_row['Version']=to_update['version']
        return new_row
    else:
        return Response(json.dumps({'Status': 'Version mismatch,try again'}), status=422, mimetype="application/json")


@app.route('/datahandler', methods=['POST',])
def insertdata():
    print(request.json)
    print(request.query_string)
    if request.method == 'POST':
        name=request.form['username']
        email=request.form['email']
        dob=request.form['dob']
        color=request.form['favcolor']
        img=request.files['avatar'].read()
        #print(dob,color,img)
        new_person=People(name,email,str(dob),str(color),img,1)
        try:
            db.session.add(new_person)
            db.session.commit()
            return render_template('modal.html')
        except:
            return Response(json.dumps({'Status': 'Image cant be proccessed,change image'}), status=422, mimetype="application/json")

    """
    1.Retrieve roll number,name,branch,section,year,semester from request
    2.Set version 1
    3.Insert in database for eg
    Roll number:529 Name:x Section:CSE Year:1 Semester:1 Version:1
    4.Return jsonify of above row in dict form
    this shold be returned
     { "Branch": "5", "Name": "5", "Roll Number": "5", "Section": 5, "Semester": 5, "Version": 1, "Year": 5}
    5.if primary key violated return jsonify({'Sucess':"Error "})
    """
    '''per_dict=request.json
    roll1=per_dict['Roll number']
    name=per_dict['Name']
    branch=per_dict['Branch']
    section=per_dict['Section']
    year=per_dict['Year']
    semester=per_dict['Semester']
    per_dict['Version']=1
    new_person = Person(roll1,name,branch,section,year,semester,1)
    try:
        db.session.add(new_person)
        db.session.commit()
        print(per_dict)
        return jsonify(per_dict)
    except:
        return Response(json.dumps({'Status': 'Roll number already there'}), status=422, mimetype="application/json")'''

@app.route('/DataHandler', methods=['DELETE',])
def deletedata():
    """
    1.Retrieve roll number,name,branch,section,year,semester,version from request
    2.Delete the row from database using roll number
    3.Return jsonify of above row
    c"""
    
    person_row=request.json
    email=person_row['Email']
    person = People.query.filter_by(email=email).first()
    db.session.delete(person)
    db.session.commit()
    data=convert_row_to_dict(person)
    return jsonify(data)



@app.route("/")
def index():
    return render_template("modal.html")

if __name__ == '__main__':
    app.run(port=5000,debug=True)
