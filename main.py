from flask import Flask,render_template,request,redirect

from database import conn,cur
from datetime import datetime

app=Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


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
    # cur.execute()



    
  





# if __name__=="__main__":
#     app.run()



app.run(debug=True)


print("hello")