from flask import Flask,render_template,request,redirect,flash

from database import conn,cur
from datetime import datetime

app=Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

cur.execute("CREATE TABLE IF NOT EXISTS products(id SERIAL PRIMARY KEY, name VARCHAR(100), buying_price NUMERIC(14,2), stock_quantity INTEGER, selling_price NUMERIC(14,2))")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id SERIAL PRIMARY KEY, pid INTEGER REFERENCES products(id), quantity INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
conn.commit()

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact-us")
def contact():
    return render_template("contact.html")

@app.route("/products", methods=["GET","POST"])
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

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email_address=request.form["emailaddress"]
        password= request.form["password"]

        query_login= "SELECT id from users where email_address = '{}' and password= '{}'".format(email_address,password)
        cur.execute(query_login)
        row=cur.fetchone()

        if row is None:
            flash("Invalid credentials")
            return render_template("login.html")
        else:
            return redirect("/dashboard.html")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        cur.execute("SELECT* FROM users")
        users=cur.fetchall()
        return render_template("register.html", users=users)
    else:
        username=request.form["username"]
        email_address=request.form["email"]
        password=request.form["password"]

        query_insert_user="INSERT INTO users(username,emailaddress,password) values(%s,%s,%s) RETURNING id;"
        cur.execute(query_insert_user)
        conn.commit()
        return redirect('/')






app.run(debug=True)

