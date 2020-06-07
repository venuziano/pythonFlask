# Autores: Rafael, Luis, Guilherme
#
#

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import flash

import psycopg2

try:
   con = psycopg2.connect(
         host='localhost',
         database='postgres',
         user='postgres',
         password='postgres'
)
except:
   print("Erro ao conectar-se ao banco de dados, tente novamente.")

app = Flask(__name__)

@app.route("/")
def main():
   if not 'estalogado' in session:
      return render_template("auth.html")

   return redirect("/info")


@app.route("/userRegister")
def userRegister():
   return render_template("userRegister.html")

@app.route('/createUser', methods=['GET', 'POST'])
def cadastrousuario():
   if request.method == 'POST':
      senha = request.form['senha']
      usuario = request.form['usuario']

      if usuario == '' or senha == '':
         flash('E-mail ou senha invalidos!')
      else:
         cur = con.cursor()
         cur.execute("INSERT INTO users(mail, password) VALUES (%s,%s)", (usuario,senha))
         con.commit()
         flash('Cadastro realizado com sucesso')
      
   return render_template('userRegister.html')

@app.route("/auth", methods=['GET', 'POST'])
def auth():
   if request.method == 'POST':
      usuario = request.form['email']
      senha = request.form['password']

      cur = con.cursor()

      cur.execute("select * from users where mail = '" + usuario + "'" + " and password = '" + senha + "'")
   
      registro = cur.fetchall()

      if registro:
         session['estalogado'] = True
         session['email'] = usuario
         session['senha'] = senha
         flash("Login realizado com sucesso")
      else:
         flash("Credenciais inválidas, tente novamente.")
      return redirect("/")

   return render_template("auth.html")

@app.route("/info")
def info():
   if not 'estalogado' in session:
      return render_template("auth.html")
   # endif

   cur = con.cursor()
   try:
      cur.execute("select date, resource, value, mem from data where resource = 'cpu/mem' order by  id desc limit 15")
   except:
      flash("Nenhum dado encontrado, tente novamente.")

   entries_data = cur.fetchall()

   return render_template("dashboard.html", entries_data=entries_data)

@app.route('/listausu')
def listausu():
   if not 'estalogado' in session:
      return render_template('auth.html')
   else:
      resultados = []
      cur = con.cursor()
      cur.execute(" select * from users")
      resultados = cur.fetchall()
   if not resultados:
      flash('No results found!')
      return redirect('/')
   else:	
      return render_template('listausuarios.html', data_usuarios=resultados)

@app.route("/logout")
def logout():
   session.pop('estalogado', None)
   session.pop('email', None)
   session.pop('password', None)
   flash("Deslogin realizado com sucesso")
   return redirect('/')

if __name__ == "__main__" :
   app.secret_key = '\x91i(\xd0\xe1\x9d\x11\x94\xc2\x9ed<\xce\xc6\x1c4\x06s}F\xf5\xe4&\xd2'
   app.session_type = 'memcache'
   app.debug = True
   app.run(host='0.0.0.0', port=9001)
