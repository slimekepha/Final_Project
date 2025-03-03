import psycopg2



conn=psycopg2.connect(host="134.209.24.19", port="5432" ,user="birirkephas", database="birirkephas", password="12345")

cur=conn.cursor()