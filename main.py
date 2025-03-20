from flask import Flask,render_template,request,redirect,flash,session,url_for
from functools import wraps

from database import conn,cur
from datetime import datetime
from flask_bcrypt import Bcrypt


app=Flask(__name__)

app=Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'ghhuudkks'

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' not in session:
            flash('You must first login')
            next_url=request.url
            return redirect(url_for("login", next=next_url))
        return f(*args, **kwargs)
    return protected


@app.route("/")
@login_required
def home():
    return render_template("index.html")

cur.execute("CREATE TABLE IF NOT EXISTS products(id SERIAL PRIMARY KEY, name VARCHAR(100), buying_price NUMERIC(14,2), stock_quantity INTEGER, selling_price NUMERIC(14,2))")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id SERIAL PRIMARY KEY, pid INTEGER REFERENCES products(id), quantity INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
conn.commit()

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
def logout():
    return render_template("login.html")


@app.route("/contact-us")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url=request.args.get('next')
    print("-------------hjgggg-------fdxds", next_url)
    if request.method == "POST":
        email_address = request.form["emailaddress"]
        password = request.form["password"]

        cur.execute("SELECT id FROM users WHERE emailaddress='{}'". format(email_address))
        email_exists=cur.fetchone()

        if email_exists is None:
           print("----------not print-------")
           flash('email does not exist, try to register if you dont have an account')
           return redirect("/login")
        else:
            cur.execute("SELECT password FROM users WHERE emailaddress='{}'".format(password))
            hash_pass=cur.fetchone()[0]
            pass_bool=bcrypt.check_password_hash(hash_pass, password)

            if pass_bool == False:
                flash("Invalid Credentials")
                return redirect("/login")
            else:
                print("--------sssssdddd----dddd", request.form['next_url'])
                next_url=request.form["next_url"]
                session['email']=email_address
                if next_url == "None":
                    return redirect("/dashboard")
                else:
                    url="/"+next_url.split('/')[-1]
                    return redirect(url)
    return render_template("login.html", next_url=next_url)

@app.route("/products", methods=["GET","POST"])
@login_required
def products():
    if request.method == "GET":
        cur.execute("SELECT*FROM products")
        products=cur.fetchall()
        print(products)
        return render_template("products.html", products=products)
    else:
         name=request.form["name"]
         buying_price=float(request.form['buyingPrice'])
         selling_price=float(request.form["sellingPrice"])
         stock_quantity=int(request.form["stockQuantity"])
         query_insert="insert into products(name,buying_price,selling_price,stock_quantity)"\
         "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)
         cur.execute(query_insert)
         conn.commit()
         return redirect('/products')


@app.route("/sales", methods=["GET", "POST"])
# @login_required
def sales():
      if request.method == "GET":
         cur.execute("SELECT * FROM sales")
         sales=cur.fetchall(),
       
         cur.execute("SELECT * FROM products")
         products=cur.fetchall()
         
         return render_template("sales.html",sales=sales, products=products)
      else:
          pid=request.form["pid"]
          quantity=request.form["quantity"]
          query_make_sale="insert into sales(pid,quantity,created_at)"\
          "values({},{},now())".format(pid,quantity)
          cur.execute(query_make_sale)
          conn.commit()
          return redirect('/sales')



@app.route("/dashboard")
# @login_required
def dashboard():
    cur.execute("SELECT products.name, sum(sales.quantity*products.selling_price) from sales join products on products.id=sales.pid group by products.name;")
    salesperproduct=cur.fetchall()

    x=[]
    y=[]
    for i in salesperproduct:
        x.append(i[0])
        y.append(float(i[1]))
    cur.execute("SELECT products.name, sum(sales.quantity*products.selling_price) from sales join products on products.id=sales.pid group by products.name;")
    profit_result=cur.fetchall()
    return render_template("dashboard.html", x=x, y=y, profit_result=profit_result)



    
  





# if __name__=="__main__":
#     app.run()

@app.route("/update-product", methods=["POST"])
def updateproduct():
    id=request.form["id"]
    name=request.form["name"]
    buying_price=float(request.form['buyingPrice'])
    selling_price=float(request.form["sellingPrice"])
    stock_quantity=int(request.form["stockQuantity"])
    query_update="UPDATE products SET name = '{}', buying_price = {}, selling_price = {}, stock_quantity = {} WHERE id = {};".format(name, buying_price, selling_price, stock_quantity, id)
    cur.execute(query_update)
    conn.commit()
    return redirect("/products")

@app.route("/update-stock", methods=["POST"])
def updatestock():
    id=request.form["id"]
    pid=request.form["pid"]
    quantity=int(request.form["quantity"])
    created_at=datetime.now()
    query_stock_update="UPDATE stock SET quantity = %s, created_at = NOW() WHERE id = %s"
    cur.execute(query_stock_update, (quantity,created_at, id))
    conn.commit()
    return redirect("/stock")


    
@app.route("/register", methods=["GET","POST"])
# @login_required
def register():
    if request.method =="GET":
        cur.execute('SELECT*FROM USERS;')
        allusers=cur.fetchall()
        return render_template('register.html', allusers=allusers)

        
        
    else:
        username=request.form['username']
        email_address=request.form['email']
        password=request.form['password']

        query_check_email="SELECT id FROM users WHERE emailaddress='{}'".format(email_address)
        cur.execute(query_check_email)
        users=cur.fetchone()

        print(f'{users} is the user')

        if not users is None:
            flash("Email exists!!")
            return render_template('register.html')
        else:
            password=request.form['password']
            confirmpassword=request.form['confirmpassword']
            if confirmpassword != password:
                flash('Passwords do not match!!')
                return redirect("/register")
            else:
                hashed_pass=bcrypt.generate_password_hash(password).decode('utf-8')
                query_insert_user="INSERT INTO users(username,emailaddress,password)"\
                    "values('{}','{}','{}')".format(username,email_address,hashed_pass)
                
                cur.execute(query_insert_user)
                conn.commit()
                return redirect("/login")


    # if request.method == "GET":
    #     cur.execute("SELECT* FROM users")
    #     users=cur.fetchall()
    #     return render_template("register.html", users=users)
    # else:
    #     username=request.form["username"]
    #     email_address=request.form["email"]
    #     password=request.form["password"]
    #     hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

    #     query_insert_user="INSERT INTO users(username,emailaddress,password) values(%s,%s,%s) RETURNING id;"
    #     print(f'{hash_password} is the hashed password')
    #     cur.execute(query_insert_user)
    #     conn.commit()
    #     return redirect('/login')
    

@app.route("/expenses", methods=["GET", "POST"])
# @login_required
def expenses():
    if request.method=="GET":
        cur.execute("SELECT * FROM PURCHASES ORDER BY purchase_date DESC")
        expenses=cur.fetchall()
        return render_template("expenses.html", expenses=expenses)
    else:
        expense_category = request.form["expense_category"] 
        description = request.form["description"]
        amount = int(request.form["amount"]) 

        query_create_expense="INSERT INTO purchases(expense_category, description, amount, purchase_date)"\
                        "VALUES('{}','{}',{}, now())".format(expense_category,description,amount)
        cur.execute(query_create_expense)
        conn.commit()
        return redirect("/expenses")

@app.route("/stock", methods=["GET", "POST"])
# @login_required
def stock():
    if request.method=="GET":
        cur.execute("SELECT stock.id, products.name, stock.quantity, stock.created_at FROM stock join products on products.id=stock.pid")
        stock=cur.fetchall()
        cur.execute("SELECT * FROM products ORDER BY name ASC")
        products=cur.fetchall()
        return render_template("stock.html", stock=stock, products=products)
    else:
        pid=request.form["pid"]
        quantity=request.form["quantity"]
        query_update_stock="INSERT INTO stock(quantity, pid,created_at)"\
                            "VALUES({},{},now())".format(quantity,pid)
        cur.execute(query_update_stock)
        conn.commit()
        return redirect("/stock")





app.run(debug=True)

