from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import botocore
import boto3
import sys , os
from werkzeug.utils import secure_filename
import random

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] =  16 * 1024 * 1024 # 4 * 1024 4 Kb limit ## 16 * 1024 * 1024   # 16 MB
app.config['DEBUG'] = True

app.secret_key ='GHJYUJHN89kkP'

MYREGION = ""
USERS3 = ""

@app.route('/')
def index():
  return render_template('index.html')


##
##************************************************************
##

@app.route('/task1', methods=['GET','POST'])
def get_tasks():
  msg = ""
  task = 1
  type= 2
  global  MYREGION

  if request.method == 'POST':
    result = request.form
    bname = result['bname']
    region = result['region']    
  
    try: 
      s3user = check_credentials()      
      '''
      ACL='private'//'public-read'//'public-read-write'//'authenticated-read'
      us-east-1 <-- Home Region
      '''
      if region == MYREGION:
            s3user.create_bucket(ACL='public-read',Bucket=bname)
      else:      
        s3user.create_bucket(ACL='public-read',Bucket=bname,CreateBucketConfiguration={'LocationConstraint': region})
            
      flash(u'Bucket Created Sucessfully','success')        
      return redirect(request.url)         

    except botocore.exceptions.ClientError as error:      
      msg = error.response['Error']['Code']
      flash(msg,'error')        
      return redirect(request.url) 

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
##


@app.route('/task2', methods=['GET'])
def get_task2():
  task = 2
  s3user = check_credentials()
  response = s3user.list_buckets()  
  data = response['Buckets']  
  mdata = {"task":task,"response":data,"length":len(data)} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
##




@app.route('/task3', methods=['POST','GET'])
def get_task3():
  task = 3   
  msg = ""  

  if request.method == 'POST':     
    try:   
      bname = request.form['bname'] 
      file = request.files['file']   
     # bytes = file.read()
      
      if file.filename == '':
        flash(u'No selected file','error')        
        return redirect(request.url)     

      elif file and allowed_file(file.filename):       
        filename1 = secure_filename(file.filename)
        r1 = random.randint(1, 999999) 
        fname = str(r1)+'_'+filename1
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))

        f1 = app.config['UPLOAD_FOLDER'] +'/'+fname
        
        with open(f1, "rb") as f:
          buff = f.read()

        #print(buff) 
        
        ################################
        '''Access control list
          response = client.put_object(
            ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
            Body=b'bytes'|file,
            Bucket='string',   
            Key='string',   
          )
        ''' 
        s3user = check_credentials()             
        #response = s3user.put_object(ACL='public-read',Body=filename,Bucket=bname,Key=filename)
        response = s3user.put_object(ACL='public-read',Body=buff,Bucket=bname,Key=fname)
        #print(response)
        ################################
        flash(u'File successfully uploaded','success')        
        return redirect(request.url)    

      else:
        flash(u'File upload fails due to invalid extensions','error')        
        redirect(request.url)

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
## 
@app.route('/task4', methods=['POST','GET'])
def get_task4():
  task = 4   
  msg = ""  

  if request.method == 'POST':     
    try:   
      sbname = request.form['sbname'] 
      dbname = request.form['dbname'] 
      fname = request.form['fname']    
      s3user = check_credentials()  
      '''
      response = client.copy_object(
      ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
      Bucket='destination bucket',  
      CopySource='string' or {'Bucket': 'string', 'Key': 'string', 'VersionId': 'string'},    
      Key='string',    
      StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE',    
      )
      '''    
      response = s3user.copy_object(
        Bucket=dbname,
        CopySource='/'+sbname+'/'+fname,
        Key= fname,
      )
      flash("Copied Sucessfully",'success')  
      redirect(request.url)  

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)    

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
##

@app.route('/task5', methods=['POST','GET'])
def get_task5():
  task = 5  

  if request.method == 'POST':  
    try:      
      path = request.form['pathname']+'/'  ##  "e:/upld1"
      bname = request.form['bname'] 
      s3user = check_credentials()  
      dirs = os.listdir( path )
      for filename in dirs:
        with open(path+filename,'rb') as f:
          data = f.read() 

        response = s3user.put_object(ACL='public-read',Body=data,Bucket=bname,Key=filename)

      flash(u'All Files successfully uploaded from this directory','success')        
      return redirect(request.url)   

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
##

@app.route('/task6', methods=['POST','GET'])
def get_task6():
  task = 6  
  if request.method == 'POST':  
    try:           
      bname = request.form['bname'] 
      fname = request.form['fname'] 
      dname = request.form['dname'] + '/' 
      s3user = check_credentials()        
      
      s3user.download_file(bname, fname, dname+fname)

      flash(u'File successfully downloaded from bucket','success')        
      return redirect(request.url)   

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)

##
##************************************************************
## 

@app.route('/task7', methods=['POST','GET'])
def get_task7():
  task = 7  
  if request.method == 'POST':  
    try:           
      bname = request.form['bname']      
      dname = request.form['dname'] + '/' 
      s3user = check_credentials()              
      
      list = s3user.list_objects(Bucket=bname)['Contents']
      #print(list)
      for myfiles in list:
        f_name = myfiles['Key']          
        #print(f_name)
        s3user.download_file(bname, f_name, dname+f_name)

      flash(u'All files successfully downloaded from bucket','success')        
      return redirect(request.url)   

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)  

##
##************************************************************
## 

@app.route('/task8', methods=['POST','GET'])
def get_task8():
  task = 8  
  data = False  
  length = 0  

  if request.method == 'POST':  
    try:           
      bname = request.form['bname']     
      s3user = check_credentials()              
      response = s3user.list_objects(Bucket=bname)
      
      if 'Contents' in response:
        data = response['Contents']  
        length = len(data)         
      else :       
        data = True

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task,"data":data,"length":length} 
  return render_template('s3.html',mdata = mdata)  

##
##************************************************************
## 

@app.route('/task9', methods=['POST','GET'])
def get_task9():
  task = 9

  if request.method == 'POST':  
    try:           
      bname = request.form['bname']     
      fname = request.form['fname']   
      s3user = check_credentials()
      response = s3user.delete_object(
                    Bucket=bname,
                    Key=fname 
                )                  
      flash(u'file deleted  successfully','success')        
      return redirect(request.url)  

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)    

##
##************************************************************
## 

@app.route('/task10', methods=['POST','GET'])
def get_task10():
  task = 10
  if request.method == 'POST':  
    try:           
      bname = request.form['bname']      
      s3user = check_credentials()    
      response = s3user.delete_bucket(Bucket=bname)      
      flash(u'bucket deleted  successfully','success')        
      return redirect(request.url)  

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)   

##
##************************************************************
## 

@app.route('/task11', methods=['POST','GET'])
def get_task11():
  task = 11

  if request.method == 'POST':  
    try:           
      bname = request.form['bname']    
      s3user = check_credentials() 
      response = s3user.list_objects(Bucket=bname)      
      if 'Contents' in response:
        data = response['Contents']  
        for d1 in data:        
          s3user.delete_object(Bucket=bname,Key=d1['Key'])    
      s3user.delete_bucket(Bucket=bname)   
      
      flash(u'Bucket deleted  successfully','success')        
      return redirect(request.url)  

    except botocore.exceptions.ClientError as error: 
      flash(error.response['Error']['Code'],'error')  
      redirect(request.url)

    except Exception as e:
      flash(e,'error')  
      print(e)
      redirect(request.url)  

  mdata = {"task":task} 
  return render_template('s3.html',mdata = mdata)   
##
##************************************************************
##
#   
def check_credentials():  
  global  USERS3
  global  MYREGION
  filename = 'credentials.txt' 
  if USERS3 == "":           
    lineList = list()
    with open(filename) as f:
      for line in f:
        y = line.split(':')
        lineList.append(y[1].rstrip("\n").strip())     
        
    MYREGION = lineList[0]    
    user1 = boto3.client('s3',
                          region_name = lineList[0],
                          aws_access_key_id = lineList[1],
                          aws_secret_access_key = lineList[2],
                          )
    USERS3 =  user1                   
    return user1
  else :         
    return USERS3                  
     
##
##************************************************************
##

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




############################
if __name__ == '__main__':
  app.run(debug=True)
############################







#pip install flask
# pip install boto3