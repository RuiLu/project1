#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
FindYa

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""


from datetime import *
import time
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
    price = float(request.form['price'])
    description = request.form['description']
    quantity = int(request.form['quantity'])
    picture = request.form['picture']
    i = datetime.datetime.now()
    date = i.isoformat()
    userid = session['userid']
    parameters = (name, price, description, quantity, date, picture, userid)
    try:
      g.conn.execute('INSERT INTO goods(name,price,description,quantity,date,picture,userid) VALUES (%s,%s,%s,%s,%s,%s,%s)', parameters)
      return redirect('/main')
    except Exception as e:
      error = 'Invalid input, try again.'
      return render_template('sell.html', error = error)
  return render_template('sell.html')


@app.route('/setting', methods=['GET', 'POST'])
def setting():
  error = None
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    parameters = (username, password, name, phone, address, session['userid'])
    
    try:
      sql = 'UPDATE user_account SET username = %s, password = %s, name = %s, phone = %s, address = %s WHERE userid = %s'
      g.conn.execute(sql, parameters)
      return redirect('/main')
    except:
      error = "Updata failed"
      return render_template('setting.html', error = error)
    
  userid = session['userid']
  cursor = g.conn.execute("SELECT * FROM user_account WHERE userid = %s", userid)
  info = []
  for result in cursor:
    info.append(result['userid'])
    info.append(result['username'])
    info.append(result['password'])
    info.append(result['name'])
    info.append(result['phone'])
    info.append(result['address'])
    info.append(result['rating'])
  cursor.close();
  print info[0],info[1],info[2],info[3],info[4],info[5],info[6]
  print len(info)
  context = dict(data = info)
  return render_template('setting.html', **context)

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

'''
@app.route('/order', methods=['GET','POST'])
def order():
  error=None
  order=None
  userid=session['userid']
  order_list=search_order(userid)
 

  content=dict(data=order_list, error=error, order_status=order)
  return render_template('order.html', **content)
'''

@app.route('/order',methods=['GET','POST'])
def order_status():
  print 'do it'
  error=None
  order=None 
  userid=session['userid']
  order_list=search_order(userid)
   
  print request.method
  if request.method=='POST':
    orderid=request.form.get('id','')
    if orderid!='':
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
      print 'seem there exists this order'
  
      print tot
      if tot==1:
        if userid_is_correct:
          cursor=g.conn.execute('select goodid, quantity from order_detail where orderid=%s',parameters)
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

@app.route('/product', methods=['GET', 'POST'])
def product():
  error = None
  if request.method == 'POST':
    search = request.form['search']
    minAmount = request.form['min']
    maxAmount = request.form['max']
    seller = request.form['seller']

    if search != '' and minAmount != '' and maxAmount != '' and seller != '':
      
      search = '%' + search + '%'
      mi = float(minAmount)
      ma = float(maxAmount)

      if mi > ma:
        error = 'Maximal price should not smaller than minimum price.'
        return render_template('product.html', error=error)

      cursor = g.conn.execute('SELECT userid FROM user_account WHERE name = %s', seller)
      uid = []
      for result in cursor:
        uid.append(result['userid'])

      if len(uid) == 0:
        error = 'Invaid seller name'
        return render_template('product.html', error=error)
      parameters = (search, mi, ma, uid[0])
      cursor = g.conn.execute('SELECT * FROM goods WHERE name LIKE %s AND price >= %s AND price <= %s AND userid = %s', parameters)
      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    elif search != '' and  minAmount == '' and maxAmount == '' and seller != '':
      cursor = g.conn.execute('SELECT userid FROM user_account WHERE name = %s', seller)
      uid = []
      for result in cursor:
        uid.append(result['userid'])

      if len(uid) == 0:
        error = 'Invaid seller name'
        return render_template('product.html', error=error)
      print uid[0]
      search = '%' + search + '%'
      parameters = (search, uid[0])
      cursor = g.conn.execute('SELECT * FROM goods WHERE name LIKE %s AND userid = %s', parameters)
      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    elif search == '' and seller == '' and minAmount != '' and maxAmount != '': 
      mi = float(minAmount)
      ma = float(maxAmount)

      if mi > ma:
        error = 'Maximal price should not smaller than minimum price.'
        return render_template('product.html', error=error)
      parameters = (mi, ma)
      cursor = g.conn.execute('SELECT * FROM goods WHERE price >= %s AND price <= %s', parameters)
      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    elif seller == '' and search != '' and minAmount != '' and maxAmount != '':
      mi = float(minAmount)
      ma = float(maxAmount)
      search = '%' + search + '%'
      if mi > ma:
        error = 'Maximal price should not smaller than minimum price.'
        return render_template('product.html', error=error)
      parameters = (search, mi, ma)
      cursor = g.conn.execute('SELECT * FROM goods WHERE name LIKE %s and price >= %s AND price <= %s', parameters)

      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    elif search != '' and minAmount == '' and maxAmount == '' and seller == '':
      search = '%' + search + '%'
      cursor = g.conn.execute('SELECT * FROM goods WHERE name LIKE %s', search)
   
      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    elif search == '' and minAmount == '' and maxAmount == '' and seller != '':
      cursor = g.conn.execute('SELECT userid FROM user_account WHERE name = %s', seller)
      uid = []
      for result in cursor:
        uid.append(result['userid'])

      if len(uid) == 0:
        error = 'Invaid seller name'
        return render_template('product.html', error=error)
      cursor = g.conn.execute('SELECT * FROM goods WHERE userid = %s', uid[0])
      goods = []
      for res in cursor:
        items = []
        for i in range(0, 8):
          print res[i]
          items.append(res[i])
        cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
        name = []
        for result in cur:
          name.append(result['name'])
          items.append(result['name'])
        goods.append(items)

      if len(goods) == 0:
        error = 'nothing...'
        return render_template('product.html', error=error)
      context = dict(goods = goods)
      return render_template('product.html', **context)
    else:
      error = 'Invalid search...'
      return render_template('product.html', error = error)

  else:
    cursor = g.conn.execute('select * from goods')
    goods = []
    for res in cursor:
      items = []
      for i in range(0, 8):
        items.append(res[i])
      cur = g.conn.execute('SELECT user_account.name FROM user_account, goods WHERE user_account.userid = %s', res[7])
      name = []
      for result in cur:
        name.append(result['name'])
        items.append(result['name'])
      goods.append(items)

    cursor.close()
    cur.close();

    context = dict(goods=goods)
    return render_template('product.html', **context)

@app.route('/addToCart', methods=['POST', 'GET'])
def addToCart():
  print 'add'
  error = None
  if request.method == 'POST':
    number = int(request.form.get('number'))
    goodid = int(request.form.get('name'))
    me = session['userid']
    print me, goodid, number
    parameters = (me,goodid,number)
    try:
      g.conn.execute('INSERT INTO cart_detail VALUES (%s,%s,%s)', parameters)
      print 'insert succeed'
      return redirect('cart')
    except:
      print 'insert fails'
      error = 'fail to add to cart...'
      return render_template('product.html', error = error)
    return redirect('product')
  return redirect('/product')


@app.route('/cart', methods=['GET', 'POST'])
def cart():
  print 'begin_cart'
  error=None
  error2=None
  data=[]
  billinginfo=[]
  uid=session['userid']
  tot=0
  total=0
  goods=set()
  bills=set()


  cursor = g.conn.execute('SELECT g.goodid, g.name, g.price, c.quantity from cart_detail c, goods g where g.goodid=c.goodid and c.userid=%s',uid)
  print '*** first sql search successfully finished ***'
  for res in cursor:
    tot=tot+1
    good=[]
    goods.add(res[0])
    good.append(res[0])
    good.append(res[1])
    good.append(res[3])
    price=float(res[2])*int(res[3])
    good.append(str(price))
    total=total+price
    data.append(good)
  cursor.close()
  print 'cursor closed'
  cursor = g.conn.execute('SELECT billingid, billingaddress, cardno from billinginfo where userid=%s',uid)
  print '*** second sql search successfully finished ***'
  
  for res in cursor:
    bill=[]
    bills.add(res[0])
    for a in res:
      bill.append(a)
    billinginfo.append(bill)
  cursor.close()
  print 'finish sql search'

 
 
  if request.method=='POST':
    print 'get a POST'
    goodid=request.form.get('goodid','')
    billid=request.form.get('billingid','')

    if goodid!='':
      print goods
      print 'goodid=%s' %goodid
      if int(goodid) in goods:
        try:
          parameters=(uid,goodid)
          print 'Try to delete'
          print 'DELETE FROM cart_detail WHERE userid=%s AND goodid=%s' %parameters
          cursor=g.conn.execute('DELETE FROM cart_detail WHERE userid=%s AND goodid=%s',parameters)
          print 'sql delete finish'
          cursor.close()
          return redirect('/cart')
        except:
          error='Fail to delete!'
          print error
      else:
        error='Goodid not found in cart!'
        print error

    elif billid!='':
      print 'billid=%s'  %billid
      if tot==0:
        error2='The cart is empty!'
      else:
        print bills
        new_id=g.conn.execute('SELECT nextval(\'order_list_orderid_seq\')')
        a=new_id.fetchone()
        new_id.close()
        if int(billid) in bills:
          try:
            print a[0]
            print 'try to form a new order'
            t=date.today()
            print t
            parameters=(a[0],uid,int(billid),t,'pending','%.2f'%total)
            print 'parameters formed'
            print 'Insert into order_list values(%s,%s,%s,\'%s\',\'%s\',%s);'%parameters
           
            cursor=g.conn.execute('Insert into order_list values(%s,%s,%s,%s,%s,%s);',parameters)
            cursor.close()
            
            print 'Is that ok?'
          except Exception as e:
            print e
            error2='fail to form order!'
            print error2
          for each in data:
            parameters=(a[0],each[0],each[2])
            g.conn.execute('Insert into order_detail values(%s,%s,%s);',parameters)
          g.conn.execute('Delete from cart_detail where userid=%s',uid)
          return redirect('/cart')
          
        else:
          error2='This is not your billing!'
          print error2
        
    print 'ready to work'   
  

  print 'maybe finished?'
  content=dict(data=data,Billinginfo=billinginfo, error=error, error2=error2, total='%.2f' %total)
  return render_template('cart.html',**content)

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
