from flask import *
import json
from flask_sqlalchemy import SQLAlchemy
import base64 
import xlsxwriter
from PIL import Image
from io import BytesIO
import os
import pandas as pd
app = Flask('jsgrid-playground', template_folder='.')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://gusree:gunaSREE1@@db4free.net:3306/gusree_12'
#'mysql+pymysql://admin:gunaSREE1*@flaskfinale.csp5sayedzk7.us-east-1.rds.amazonaws.com:3306/sample'
#'mysql+pymysql://gusree:gunaSREE1@@db4free.net:3306/gusree_12'
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
db.create_all()
@app.route('/download1excel')
def excel():
    count=People.query.all()
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    newDF = pd.DataFrame()
    newDF.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = "Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    header = workbook.add_format({'align': 'center'})
    worksheet.set_default_row(100)
    worksheet.set_column(0, 5, 25)
    worksheet.write(0,0,"Name",header) 
    worksheet.write(0,1,"Email",header) 
    worksheet.write(0,2,"Date of Birth",header) 
    worksheet.write(0,3,"Color",header) 
    worksheet.write(0,4,"Profile pic",header) 
    row=1
    col=0
    for ele in count:
        #l=[ele.name,ele.email,str(ele.dob)[0:10],ele.color]
        worksheet.write(row, col,ele.name,header) 
        worksheet.write(row, col+1,ele.email,header) 
        worksheet.write(row,col+2,str(ele.dob)[0:10],header)
        worksheet.write(row, col+3,ele.color,header) 
        p="imageToSave"+str(row)+".png"
        with open(p, "wb") as fh:
            fh.write(ele.image)
        worksheet.insert_image(row,col+4,p,{'x_scale':0.5,'y_scale':0.5,'x_offset':7,'y_offset':7,'positioning':1})
        row+=1
    workbook.close()
    output.seek(0)
    for x in range(1,row):
        os.remove("imageToSave"+str(x)+".png")
    return send_file(output, attachment_filename="testing.xlsx", as_attachment=True)

@app.route('/DataHandler', methods=['GET',])
def getdata():
    #print(request.json['pageIndex'])
    print(request.json)
    my_dict=request.args
    fname=None 
    fmail=None
    for key in my_dict:
        print(key,my_dict[key])
        if(key=='Name'):
            fname=my_dict[key]
        if(key=='Email'):
            fmail=my_dict[key]
    print(request.url)
    print(request.query_string)
    i=(int(request.args['pageIndex'])-1)*int(request.args['pageSize'])
    j=i+int(request.args['pageSize'])
    '''if(fname!=None and fmail!=None):
        filter_spec = [{'field': 'name', 'op': '==', 'value':fname}]
        filter_spec = [{'field': 'email', 'op': '==', 'value':fmail}]
        filtered_query = apply_filters(query, filter_spec)
        result = filtered_query.all()
        count=People.query.slice(i,j).filter(and_(name=fname,email=fmail))'''
    if fname!='':
        count=People.query.filter_by(name=fname).slice(i,j)
    elif fmail!='':
        count=People.query.filter_by(email=fmail).slice(i,j)
    else:
        count=People.query.slice(i,j).all()
    #converting rows brought from database to list of dicts
    arr=list(map(convert_row_to_dict,count))
    ct=Countitem.query.all()
    #print(arr,ct[0].count)
    return jsonify({'data':arr,'itemsCount':ct[0].count})



@app.route('/datahandler2', methods=['POST',])
def updatedata2():
    print(request)
    print(request.form)
    if request.method=="POST":
        new_version=request.form['version2']
        new_name=request.form['username2']
        new_mail=request.form['email2']
        new_dob=request.form['dob2']
        new_color=request.form['favcolor2']
        new_pic=request.files['avatar2'].read()
        try:
            person = People.query.filter_by(email=new_mail).first()
            print(person.version)
            print(new_version)
            if person.version==int(new_version):
                print('Yes')
                to_update=dict()
                if new_name!=person.name:
                    to_update['name']=new_name
                if new_dob!=person.dob:
                    to_update['dob']=new_dob
                if new_color!=person.color:
                    to_update['color']=new_color
                if len(new_pic)>0 and new_pic!=person.image:
                    to_update['image']=new_pic
                if len(to_update)>0:
                    try:
                        to_update['version']=int(new_version)+1
                        People.query.filter_by(email=new_mail).update(to_update)
                        db.session.commit()
                    except:
                        pass 
                #return render_template("modal.html")
                return redirect(url_for('index'))
        except:
            print('Cant load person from data table')
        else:
            print('No')
            return Response(json.dumps({'Status': 'Version mismatch,try again'}), status=422, mimetype="application/json")

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
                elif(x=='Photo'):
                    print(type(new_row[x]))
                    #img=new_row[x][22:]
                    #to_update[l[x]]=base64.b64decode(img) 
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
            return render_template("modal.html")
            #return redirect(url_for('index'))
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
    print(request)
    print(request.query_string)
    print(request.url)
    person_row=request.json
    email=person_row['Email']
    person = People.query.filter_by(email=email).first()
    print(person)
    db.session.delete(person)
    db.session.commit()
    data=convert_row_to_dict(person)
    return jsonify(data)



@app.route("/")
def index():
    return render_template("modal.html")

if __name__ == '__main__':
    app.run()
