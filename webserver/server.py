#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""


import datetime
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, session, request, render_template, g, redirect, \
                  Response, flash, url_for 

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = '\xd2\x87\x9c\x19\xd9}\x85\xcf\xb4\xc3\x18\xf3\n\xce\xcb\x8e;}SR\x88\xef\xd1\xd2'

#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://rl2784:TYJBWZ@w4111db.eastus.cloudapp.azure.com/rl2784"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
# @app.route('/')
# def main():
#   """
#   request is a special object that Flask provides to access web request information:

#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

#   See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
#   """

  # DEBUG: this is debugging code to see what request looks like
  # print request.args


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT * FROM user_account")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  # return render_template("index.html", **context)
  # return render_template("signin.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
  error = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    rating = int(request.form['rating'])
    parameters = (username, password, name, phone, address, rating)
    try:
      g.conn.execute('INSERT INTO user_account(username,password,name,phone,address,rating) VALUES(%s,%s,%s,%s,%s,%s)', parameters)
      
      return redirect('/')
    except Exception as e:
      error = "Invalid input, try others."
      return render_template('signup.html', error = error)
  return render_template("signup.html")

@app.route('/signout')
def signout():
  session.pop('userid', None)
  return redirect('/')

@app.route('/main')
def main():
  sql = 'SELECT username, name, phone, address, rating FROM user_account ' + \
        'WHERE userid = %s'
  cursor = g.conn.execute(sql, session['userid'])
  names = []
  for result in cursor:
    names.append(result['username'])  # can also be accessed using result[0]
    names.append(result['name'])
    names.append(result['phone'])
    names.append(result['address'])
    names.append(result['rating'])
  cursor.close()

  context = dict(data = names)
  return render_template('index.html', **context)

# main page is login page
@app.route('/', methods=['GET', 'POST'])
def signin():
  error = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    isCorrect = False
    cur = g.conn.execute("SELECT userid, username, password from user_account")
    for res in cur:
      if res[1] == username and res[2] == password:
        isCorrect = True
	session['userid'] = res[0]
        break
    cur.close()
    if isCorrect:
      return redirect('/main')
    else:
      error = 'Invalid username or password, try again.'
  return render_template('signin.html', error = error)

@app.route('/sell', methods=['GET','POST'])
def sell():
  error = None
  if request.method == 'POST':
    name = request.form['name']
    print name
    price = int(request.form['price'])
    print price
    description = request.form['description']
    print description
    quantity = int(request.form['quantity'])
    print quantity
    picture = request.form['picture']
    print picture
    i = datetime.datetime.now()
    date = i.isoformat()
    userid = session['userid']
    print date
    parameters = (name, price, description, quantity, date, picture, userid)
    try:
      g.conn.execute('INSERT INTO goods(name,price,description,quantity,date,picture,userid) VALUES (%s,%s,%s,%s,%s,%s,%s)', parameters)
      return redirect('/main')
    except Exception as e:
      error = 'Invalid input, try again.'
      return render_template('sell.html', error = error)
  return render_template('sell.html')

# @app.route('/buy', methods=['GET', 'POST'])
# def buy():
#   error = None
#   if request.method == 'POST':
#     search = request.form['search']
#     minAmount = int(request.form['min'])
#     maxAmount = int(request.form['max'])
#     seller = request.form['seller']
#     print search, minAmount, maxAmount, seller
#   return render_template('buy.html')

def search_order(userid):
  print 'before search'
  parameters=(userid)
  cursor=g.conn.execute('select orderid, orderdate, state, totalprice from order_list where userid=%s',userid)
  order_list=[]
  for res in cursor:
    order=[]
    for att in res:
      order.append(att)
    order_list.append(order)

  cursor.close()
  print 'search order finished'
  return order_list

@app.route('/order', methods=['GET','POST'])
def order():
  error=None
  order=None
  userid=session['userid']
  order_list=search_order(userid)
 

  content=dict(data=order_list, error=error, order_status=order)
  return render_template('order.html', **content)

@app.route('/order_state',methods=['GET','POST'])
def order_status():
  print 'do it'
  error=None
  order=None 
  userid=session['userid']
  order_list=search_order(userid)
   
  print request.method
  if request.method=='POST':
    print 'in_if'
    orderid=request.form['id']
    print orderid
    print userid
    userid_is_correct=true
    tot=0
    parameters=(orderid)




    cursor=g.conn.execute('select userid from order_list where orderid=%s',parameters)
    for res in cursor:
      if res[0]!=userid:
        error='You cannot inquire an order which does not belong to you!'
        print error
        userid_is_correct=false
      else:
        tot=tot+1
    cursor.close()
  
    print tot
    if tot==1:
      if userid_is_correct:
        cursor=g.conn.execute('select gooid, quantity from order_detail where orderid=%s',parameters)
        order=[]
        for res in cursor:
          goods=[]
          for a in res:
            goods.append(a)
          order.append(goods)
    else:
      error='Invalid order ID!'
      print error
      
  
  content=dict(data=order_list, error=error, order_status=order)
  return render_template('order.html', **content)




if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
