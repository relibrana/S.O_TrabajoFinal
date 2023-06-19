from flask import Flask, jsonify, request, render_template,session,url_for,redirect
from flask_cors import CORS
from flaskext.mysql import MySQL
import pymysql


# configuration
DEBUG = True


# initiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "super secret key"

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'support'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sistemas20.'
app.config['MYSQL_DATABASE_DB'] = 'MUSICA'
app.config['MYSQL_DATABASE_HOST'] = '44.202.64.152'
app.config['SESSION_TYPE'] = 'filesystem'
mysql.init_app(app)


# enable CORS
CORS(app, resources={r'/*':{'origins': '*'}})
#@app.route('/')
#def home():
    #session['loggedin']=False
    #return render_template('index.html',logged_in=session['loggedin'])

#@app.route('/index')
#def index():
    #if session['loggedin']:
     #return render_template('index.html',logged_in=session['loggedin'],user=session['username'])
    #else:
      #return render_template('index.html',logged_in=session['loggedin']  )
    
@app.route('/')
def home():
    return jsonify('Welcome to ThePeruvianRockArchive!')


@app.route('/login', methods =['GET', 'POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method=='POST':
        #username = request.form['username']
        #password = request.form['password']
        username = request.json['username']
        password = request.json['password']
        cursor.execute('SELECT * FROM Usuario WHERE username = % s AND password = % s', (username, password, ))
        account=cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username']=username
            #session['id']=account[0]
            return jsonify('User Found')

            #return redirect(url_for("index"))
        else:
            return jsonify('User not Found')
   # else:
        #return render_template('signIn.html')
    else:
         return jsonify('Please enter a user')
@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.json['name']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        
        sql = "INSERT INTO Usuario (name, username, password, email) VALUES (%s,%s, %s, %s)"
        val = (name,username, password, email)
        cursor.execute(sql, val)
        conn.commit()
        
    return jsonify("Successfully Registered")

        #return redirect(url_for("index"))
    #else:
        #return render_template('register.html')
    

#@app.route("/logout")
#def logout():
    #session.pop("username", None)
   # session['loggedin']=False
    #return redirect(url_for("index"))

@app.route('/update_username', methods=['GET','POST'])
def update_username():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
    
        old_username = request.json['old_username']
        new_username = request.json['new_username']

        query = "SELECT * FROM Usuario WHERE username = %s"
        cursor.execute(query, (new_username,))
        result = cursor.fetchone()
        if result is None:

            #render_template('usernameUpdate.html',user=session['username'])

            # update the username in the database
            query = "UPDATE Usuario SET username = %s WHERE username = %s"
            cursor.execute(query, (new_username, old_username))
            conn.commit()
            session['username']=new_username

            return jsonify('Username changed')

            #return redirect(url_for("index"))
        else:
            return jsonify('Username already exists')
    else:
        return jsonify('Change your username')
        #return render_template('usernameUpdate.html',user=session['username'])


#list artists
@app.route('/newArtists', methods=['GET'])
def get_newArtists():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CArtista, NArtista,TBiografia from Artista")
        artist_list = cursor.fetchall()
        return jsonify({
            'status':'success',
            'artists': artist_list
        })
    finally:
        cursor.close()
        conn.close()

    #if session['loggedin']:
       # return render_template('newArtist.html', artist_list=artist_list,logged_in=session['loggedin'],user=session['username'])
    #else: 
        #return render_template('newArtist.html', artist_list=artist_list,logged_in=session['loggedin'])

#add new artists
@app.route('/submit/newArtist', methods=['GET', 'POST'])
def add_newArtist():

    #if session['loggedin']:
        
    if request.method == 'POST':
        artistName = request.json['artistName']
        bio = request.json['bio']
        artist_q_album = 0
        #image=request.files['image'].read()
        image=None
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Artista (NArtista, TBiografia, QAlbumnes,image) VALUES (%s, %s, %s, %s)", (artistName, bio, artist_q_album,image))
        conn.commit()
        return jsonify('Artist submitted successfully')
    else:
        return jsonify('Error')
   # else:
        # return redirect(url_for("login"))
       

@app.route('/favorites/<id>', methods=['GET'])
def favorites(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Cancion.NCancion, Cancion.QDuration,Artista.NArtista,FavCancion.id from FavCancion INNER JOIN Cancion ON Cancion.CCancion = FavCancion.CCancion INNER JOIN Album ON Cancion.CAlbum=Album.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE FavCancion.id_usuario =%s",(id))
        song_list=cursor.fetchall()

        cursor.execute("SELECT Album.NAlbum, Artista.NArtista,FavAlbum.id from FavAlbum INNER JOIN Album ON Album.CAlbum= FavAlbum.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE FavAlbum.id_usuario =%s",(id))
        album_list=cursor.fetchall()
        return jsonify({
            'status':'success',
            'songs':song_list ,
            'album':album_list
        })
    finally:
        cursor.close()
        conn.close()
    #return render_template('favorites.html',song_list=song_list,user=session['username'],album_list=album_list)

@app.route('/delete/<id>',  methods=['POST','DELETE'])
def delete_FavoriteSong(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM FavCancion WHERE id=%s",(id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("favorites"))

@app.route('/deleteAlbum/<id>',  methods=['POST','DELETE'])
def delete_FavoriteAlbum(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM FavAlbum WHERE id=%s",(id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("favorites"))

@app.route('/add/<id>',  methods=['POST'])
def add_FavoriteSong(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    
        
    if session['loggedin']:
        query="SELECT * FROM FavCancion WHERE CCancion=%s"
        cursor.execute(query, (id))
        print(cursor.fetchone())
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO FavCancion(CCancion,id_usuario) VALUES (%s,%s)",(id,session['id']))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            return redirect(url_for("favorites"))
        return redirect(url_for("favorites"))
    else:
        return redirect(url_for('login'))


@app.route('/artist/addAlbum/<id>',  methods=['POST'])
def add_FavoriteAlbum(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO FavAlbum(CAlbum,id_usuario) VALUES (%s,%s)",(id,session['id']))
    conn.commit()
    cursor.close()
    conn.close()
    if session['loggedin']:
        return redirect(url_for("favorites"))
    else:
        return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search():
    conn = mysql.connect()
    cursor = conn.cursor()
    name = request.args.get('q')
    cursor.execute("SELECT Canciones.NCancion, Canciones.QDuration,Artista.NArtista,Canciones.CCancion from Canciones INNER JOIN Album ON Canciones.CAlbum=Album.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE Canciones.NCancion=%s",name)
    song_list=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('search.html',song_list=song_list,user=session['username'])


@app.route('/artist/<id>',methods=['GET'])
def artist(id):
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT NArtista,TBiografia from Artista  WHERE Artista.CArtista=%s",id)
    artist = cursor.fetchone()
    cursor.execute("SELECT CAlbum,NAlbum from Album WHERE CArtista=%s",id)
    album_list=cursor.fetchall()
    cursor.close()
    conn.close()
    if session['loggedin']:
        return render_template('artist.html',artist=artist, album_list=album_list,user=session['username'])
    else:
        return render_template('artist.html',artist=artist, album_list=album_list)


@app.route('/artists/<myArtist>/albums', methods=['GET'])
def get_album_by_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Album.NAlbum from Album JOIN Artista ON Album.CArtista = Artista.CArtista WHERE Artista.NArtista = %s", (myArtist))
        album_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'albums': album_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/artists/<myArtist>/songs', methods=['GET'])
def get_songs_by_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Canciones.NCancion, Canciones.QDuration, Album.NAlbum from Canciones JOIN Album ON Canciones.CAlbum = Album.CAlbum JOIN Artista ON Album.CArtista = Artista.CArtista WHERE Artista.NArtista = %s", (myArtist))
        song_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'songs': song_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()     

@app.route('/albums/<myAlbum>/songs', methods=['GET'])
def get_songs_by_album(myAlbum):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NCancion, QDuration FROM Canciones WHERE CAlbum = (SELECT CAlbum FROM Album WHERE NAlbum = %s)", (myAlbum))
        song_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'songs': song_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()   



@app.route("/delete/<myArtist>", methods=['DELETE'])
def delete_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Artista WHERE NArtista = %s", (myArtist))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message':"Successfully deleted!"})

@app.route("/update/<myArtist>", methods=['PUT'])
def update_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    artist_name = request.json['artistName']
    artist_bio = request.json['artistBio']
    if artist_bio is not '':
        cursor.execute("UPDATE Artista SET TBiografia = %s WHERE NArtista = %s", (artist_bio, myArtist))
    if artist_name is not '':
        cursor.execute("UPDATE Artista SET NArtista = %s WHERE NArtista = %s", (artist_name, myArtist))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Successfully modified!'})

if __name__ == '__main__':
    app.run(port=5000,debug=True)
