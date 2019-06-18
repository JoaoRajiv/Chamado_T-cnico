import psycopg2, psycopg2.extras
from Banco.Conexao import Conexao
from flask import g, render_template, request, redirect, url_for, session, flash
from app import app

@app.before_request
def before_request():
    g.db = Conexao.criar_conexao()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def index(): 
    cur=g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':    
        cur.execute("SELECT * FROM usuario")
        usuario = cur.fetchall()
        matricula = request.form['matricula']
        senha = request.form['senha']
        cur.execute(f"SELECT nome FROM usuario WHERE matricula ILIKE '{request.form['matricula']}'")
        nomes = cur.fetchone()
        session['nome'] = nomes[0]
        cur.execute(f"SELECT type FROM usuario WHERE matricula ILIKE '{request.form['matricula']}'")
        tipo = cur.fetchone()
        session['tipo'] = tipo[0]
        cur.close()
        for x in usuario:
            if (x[0] == matricula and x[1] == senha and x[3] == 'Admin'):
                return redirect(url_for('menuadmin', session_nome=session['nome'], session_tipo=session['tipo']))
            elif (x[0] == matricula and x[1] == senha and x[3] == 'Tecnico'):
                return redirect(url_for('menutec', session_nome=session['nome'], session_tipo=session['tipo']))
            elif (x[0] == matricula and x[1] == senha and x[3] == 'Professor'):
                return redirect(url_for('menuprof', session_nome=session['nome'], session_tipo=session['tipo']))   
    return render_template('login.html')

@app.route('/menuadm')
def menuadmin():
    session_nome = ''
    if 'nome' in session:
        session_nome = session['nome']
    session_tipo = ''
    if 'tipo' in session:
        session_tipo = session['tipo']

    return render_template('menu-admin.html', session_nome=session_nome, session_tipo=session_tipo)

@app.route('/menutec')
def menutec():
    session_nome = ''
    if 'nome' in session:
        session_nome = session['nome']    
    session_tipo = ''
    if 'tipo' in session:
        session_tipo = session['tipo']

    return render_template('menu-tec.html', session_nome=session_nome, session_tipo=session_tipo)

@app.route('/menuprof')
def menuprof():
    session_nome = ''
    if 'nome' in session:
        session_nome = session['nome']
    session_tipo = ''
    if 'tipo' in session:
        session_tipo = session['tipo']
    
    return render_template('menu-prof.html', session_nome=session_nome, session_tipo=session_tipo)

@app.route('/cadastrousuario', methods=['GET', 'POST'])
def cadastrarusu():
    if request.method == "POST":
        cur=g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"INSERT INTO usuario (matricula, nome, senha, type) VALUES ('{request.form['matricula']}', '{request.form['nome']}', '{request.form['senha']}', '{request.form['tipo']}')")
        return redirect(url_for('menuadmin'))
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM usuario")
    usuarios = cur.fetchall()
    cur.close()

    return render_template('cadastro.html', usuarios=usuarios)

@app.route('/historico')
def historico():
    session_tipo = ''
    if 'tipo' in session:
        session_tipo = session['tipo']

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM historico")
    historico = cur.fetchall() 
    
    return render_template('historico.html', historico=historico, tipo=session_tipo)

@app.route('/cadastrarambiente', methods=['GET', 'POST'])
def cadastroamb():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        cur.execute(f"INSERT INTO ambientes(ambiente) VALUES ('{request.form['amb']}')")
        cur.close()
        return redirect(url_for('menuadmin'))

    return render_template('cadastrarambiente.html')

@app.route('/chamadas', methods=['GET', 'POST'])
def chamadas():    
    session_nome = ''
    if 'nome' in session:
        session_nome = session['nome']
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM chamada")
    chamadas = cur.fetchall()
    if len(chamadas)==0:
        return redirect(url_for('semchamada'))
    chamada=chamadas[0]
    idchamada=chamada[0]
    cur.close
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM historico")    
    Id = cur.fetchall()        
    if request.method == 'POST':            
        if  len(Id) == 0:
            cur.execute("SELECT * FROM chamada")
            chamadas = cur.fetchall()
            chamada=chamadas[0]
            idchamada=chamada[0]
            cur.close 
            cur.execute(f"DELETE FROM chamada WHERE idchamada = '{idchamada}'")  
            cur.execute(f"INSERT INTO historico (id, professorh, ambienteh, defeitoh) VALUES ('{1}', '{chamada[1]}', '{chamada[2]}', '{chamada[3]}')") 
            cur.close  
            return redirect(url_for('menutec'))      
        else:
            num = Id[-1:] 
            ultimo = num[0]
            numero = ultimo[0]
            cur.execute(f"DELETE FROM chamada WHERE idchamada = '{idchamada}'")  
            cur.execute(f"INSERT INTO historico (id, professorh, ambienteh, defeitoh) VALUES ('{numero+1}', '{chamada[1]}', '{chamada[2]}', '{chamada[3]}')") 
            cur.close
            return redirect(url_for('menutec'))
    
    return render_template('chamadas.html', chamadas=chamadas)

@app.route('/fazerchamada', methods=['GET', 'POST'])
def fazer_chamada():
    session_nome = ''
    if 'nome' in session:
        session_nome = session['nome']
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT ambiente FROM ambientes")
    ambientes=cur.fetchall()
    if request.method == 'POST':
        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT idchamada FROM chamada")
        iD = cur.fetchall()
        num = iD[-1:]
        if len(num) == 0:
            cur.execute(f"INSERT INTO chamada(idchamada, professor, ambiente, defeito) VALUES ('{1}','{session_nome}','{request.form['amb']}', '{request.form['problem']}')")     
            return redirect(url_for('menuprof'))
        else:    
            ultimo = num[0]
            numero = ultimo[0]       
            cur.execute(f"INSERT INTO chamada(idchamada, professor, ambiente, defeito) VALUES ('{numero+1}','{session_nome}','{request.form['amb']}', '{request.form['problem']}')")     
            return redirect(url_for('menuprof'))
    return render_template('fazerchamado.html', ambientes=ambientes)

@app.route('/semchamada')
def semchamada():
    return render_template('semchamada.html')