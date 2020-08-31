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
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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

@app.route('/download1excel')
def excel():
    count=People.query.all()
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    newDF = pd.DataFrame()
    newDF.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = "Sheet")
    workbook = writer.book
    worksheet = writer.sheets["Sheet"]
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
        worksheet.write(row, col+2,str(ele.dob)[0:10],header)
        worksheet.write(row, col+3,ele.color,header) 
        p="imageToSave"+str(row)+".png"
        with open(p, "wb") as fh:
            fh.write(ele.image)
        worksheet.insert_image(row,col+4,p,{'x_scale':0.5,'y_scale':0.5})
        row+=1
    workbook.close()
    output.seek(0)
    #for x in range(1,row):
        #os.remove("imageToSave"+str(x)+".png")
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
