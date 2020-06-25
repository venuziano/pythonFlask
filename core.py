from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import flash
from datetime import date

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
   if not 'isLogged' in session:
      return render_template("auth.html")

   return redirect("/dashboard")


@app.route("/userRegister")
def userRegister():
   return render_template("userRegister.html")

@app.route( '/createUser', methods = [ 'GET', 'POST' ])
def createUser():
   if request.method == 'POST':
      senha = request.form[ 'senha' ]
      usuario = request.form[ 'usuario' ]
      currently_date = date.today()

      cur = con.cursor()
      cur.execute("select * from users where mail = '" + usuario + "'")
      registro = cur.fetchall()

      if usuario == '' or senha == '':
         flash( 'E-mail ou senha invalidos!' )
      elif registro != []:
         flash( 'E-mail já cadastrado, utilize outro e-mail.' )
      elif registro == []:
         cur.execute( 'INSERT INTO users( mail, password, dt_created ) VALUES ( %s, %s, %s )', ( usuario, senha, currently_date ) )
         con.commit()
         flash( 'Cadastro realizado com sucesso!' )
      
   return render_template( 'userRegister.html' )

@app.route( '/deleteUser', methods = [ 'GET', 'POST' ] )
def deleteUser():
   if request.method == 'POST':
      print(request)
      usuario = request.form[ 'usuario' ]

      cur = con.cursor()
      cur.execute( "delete from users where mail = '" + usuario + "'")
      con.commit()
      #flash( 'Cadastro realizado com sucesso' )

      return redirect("/usersList")

@app.route( '/auth', methods = [ 'GET', 'POST' ])
def auth():
   if request.method == 'POST':
      usuario = request.form['email']
      senha = request.form['password']

      cur = con.cursor()
      cur.execute("select * from users where mail = '" + usuario + "'" + " and password = '" + senha + "'")
      registro = cur.fetchall()

      if registro:
         session['isLogged'] = True
         session['email'] = usuario
         session['senha'] = senha
         return redirect("/")
      else:
         flash("Credenciais inválidas, tente novamente.")
         return render_template("auth.html")

@app.route("/dashboard")
def dashboard():
   if not 'isLogged' in session:
      return render_template("auth.html")
   # endif

   cur = con.cursor()
   try:
      cur.execute("select count(*), dt_created from users group by dt_created order by dt_created")
   except:
      flash( 'Nenhum dado encontrado, tente novamente.' )

   entries_data = cur.fetchall()

   return render_template( "dashboard.html", entries_data = entries_data )


@app.route('/usersList')
def usersList():
   if not 'isLogged' in session:
      return render_template('auth.html')
   else:
      resultados = []
      cur = con.cursor()
      cur.execute( " select * from users" )
      resultados = cur.fetchall()
   if not resultados:
      flash( 'Nenhum usuário encontrado!' )
      return redirect('/')
   else:	
      return render_template( 'usersList.html', users_data = resultados )

@app.route("/logout")
def logout():
   session.pop('isLogged', None)
   session.pop('email', None)
   session.pop('password', None)
   return redirect('/')

if __name__ == "__main__" :
   app.secret_key = '\x91i(\xd0\xe1\x9d\x11\x94\xc2\x9ed<\xce\xc6\x1c4\x06s}F\xf5\xe4&\xd2'
   app.session_type = 'memcache'
   app.debug = True
   app.run(host='0.0.0.0', port=9000)
