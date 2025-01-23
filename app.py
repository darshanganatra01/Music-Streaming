import flask
from flask import Flask,url_for,flash,get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, redirect, request,session
from flask_security import current_user, Security, SQLAlchemySessionUserDatastore, login_user,logout_user
from flask_security import UserMixin, RoleMixin, verify_password, login_required,roles_required,hash_password
import matplotlib.pyplot as plt
from sqlalchemy.exc import IntegrityError
import os
from flask_restful import Api,Resource

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appi.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
api = Api(app)
db.init_app(app)
app.app_context().push()
app.config['SECRET_KEY'] = "iamreallytired"
app.config['SECURITY_PASSWORD_HASH'] = "bcrypt"
app.config['SECURITY_PASSWORD_SALT'] = "bodyispaining"
app.config['SECURITY_REGISTRABLE'] = True
app.config['SECURITY_LOGIN_USER_TEMPLATE']="Login.html"



roles_users = db.Table("roles_users",
                      db.Column("user_id", db.Integer(), db.ForeignKey("user.uid")),
                      db.Column("role_id", db.Integer(), db.ForeignKey("role.id")))




class User(db.Model, UserMixin):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users"))
    crt_status = db.Column(db.Integer, default=1)


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)


class Songs(db.Model):
    __tablename__="songs"
    s_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_name=db.Column(db.String, nullable=False)
    s_singer=db.Column(db.String,db.ForeignKey(User.firstname))
    s_genre=db.Column(db.String, nullable=False)
    date=db.Column(db.String,nullable=False)
    singer_id=db.Column(db.Integer,db.ForeignKey(User.uid))



class Review(db.Model):
    __tablename__="review"
    rev_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    uid=db.Column(db.Integer,db.ForeignKey(User.uid))
    s_id=db.Column(db.Integer,db.ForeignKey(Songs.s_id))
    rev=db.Column(db.Integer)
    feedback=db.Column(db.String)
    singer_id=db.Column(db.Integer,db.ForeignKey(User.uid))


class Playlist(db.Model):
    __tablename__="playlist"
    playlist_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    playlist_name=db.Column(db.String,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey(User.uid))


class Splaylist(db.Model):
    __tablename__="s_playlist"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    pl_id=db.Column(db.Integer,db.ForeignKey(Playlist.playlist_id))
    s_id=db.Column(db.Integer,db.ForeignKey(Songs.s_id))


class Album(db.Model):
    __tablename__="album"
    album_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    album_name=db.Column(db.String,nullable=False)
    singer_id=db.Column(db.Integer,db.ForeignKey(User.uid))


class Salbum(db.Model):
    __tablename__="s_album"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    album_id=db.Column(db.Integer,db.ForeignKey(Album.album_id))
    song_id=db.Column(db.Integer,db.ForeignKey(Songs.s_id))


db.create_all()




user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)





@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("Login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        useri = User.query.filter_by(email=email).first()

        if useri is None:
            flash("You're not a user please register as a user","notauser")
            return redirect("/register")
        elif verify_password(password, useri.password):
            login_user(useri)
            return  redirect("/udash")
        else:
            flash(" Your Password is incorrect","falsepass")
            return redirect("/")
        



@app.route("/register", methods=["GET", "POST"])
def signup():
    user=current_user
    if request.method == "GET":
        return render_template("Signup.html")
    else:
        try:
            email1 = request.form.get("email")
            password1 = request.form.get("password")
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            user = user_datastore.create_user(email=email1, password=hash_password(password1), firstname=first_name, lastname=last_name)
            db.session.commit()
            return redirect("/")
        
        except IntegrityError as e:

            flash("This Email is Already in use try using a Diffrent one","uniquemail")
            return redirect("/register")
        



@app.route("/udash",methods=["GET","POST"])
@login_required
def udash():
    if request.method=="GET":
        user=current_user
        u=user.uid
        su=Songs.query.all()
        plist=Playlist.query.filter_by(user_id=u)
        albs=Album.query.all()
        latestsng=list(su)
        latestsng.reverse()
        return render_template("Udash.html",lo=su,plist=plist,albs=albs,latestsng=latestsng,user=current_user)
    data=request.form.get("search")
    if data!=" " and data!="  ":
        results = db.session.query(Songs).filter(Songs.s_name.ilike(f'%{data}%')).all()
        resultsal = db.session.query(Album).filter(Album.album_name.ilike(f'%{data}%')).all()
        resultsgen = db.session.query(Songs).filter(Songs.s_genre.ilike(f'%{data}%')).all()
        result = db.session.query(User).filter(User.firstname.ilike(f'%{data}%')).all()
        resultscrt=[]
        for i in result:
            if "creator" in i.roles:
                resultscrt.append(i)

        return render_template("search.html",results=results,resultsal=resultsal,resultsgen=resultsgen
                                ,resultscrt=resultscrt,data=data)
    else:
        results=[]
        resultsal=[]
        resultsgen=[]
        resultscrt=[]
        return render_template("search.html",results=results,resultsal=resultsal,resultsgen=resultsgen
                                ,resultscrt=resultscrt,data=data)
        


plt.switch_backend('agg')

@app.route("/adash",methods=["GET","POST"])
@roles_required("admin")
def adash():
    songs_data = db.session.query(Songs.s_name, db.func.avg(Review.rev)).\
        join(Review, Songs.s_id == Review.s_id).\
        group_by(Songs.s_id).all()
    

    if request.method=="POST":
        d=request.form.get("search")
        return redirect(url_for("adminsearch",d=d))

    
    if songs_data:
    
        song_names, avg_reviews = zip(*songs_data)


        # Create a new figure and axis for the first plot
        fig, ax = plt.subplots()
        ax.bar(song_names, avg_reviews, color='skyblue', width=0.2)
        ax.set_xlabel('Songs')
        ax.set_ylabel('Reviews')
        ax.set_title('Histogram of Songs and Reviews')
        ax.set_ylim(0,5)


        # Save the first plot
        plot = "static/plt.png"
        fig.savefig(plot)
        plt.close(fig)  # Close the figure to release resources

        singers_data = db.session.query(User.firstname, db.func.avg(Review.rev)).\
        join(Songs, Songs.singer_id == User.uid).\
        join(Review, Songs.s_id == Review.s_id).\
        group_by(User.uid).all()

            
        # Process the data for plotting 
        singers, reviews = zip(*singers_data)

        # Create a new figure and axis for the second plot
        fig, ax = plt.subplots()
        ax.plot(singers,reviews, marker='o', linestyle='-', color='orange')  # Use 'marker' and 'linestyle' for style
        ax.set_xlabel('Singer IDs')
        ax.set_ylabel('Average Reviews')
        ax.set_title('Line Graph of Singers and Average Reviews')
        ax.set_ylim(0,5)

        # Save the second plot
        plot1 = "static/plt2.png"
        fig.savefig(plot1)
        plt.close(fig)  # Close the figure to keep things clean



    user=current_user
    a=Songs.query.all()
    b=Album.query.all()
    c=User.query.all()
    al=len(list(a))
    bl=len(list(b))
    cl=len(list(c))
    crcount=0
    role="creator"
    for i in c:
        if role in i.roles:
            crcount+=1

    l=[]
    for i in a:
        if i.s_genre not in l:
            l.append(i.s_genre)
    gl=len(l)
    
    return render_template("Adash.html",user=user,al=al,bl=bl,crcount=crcount,cl=cl,gl=gl,d=songs_data)





@app.route("/creator", methods=["GET", "POST"])
def creator():

    user = current_user
        
    if user.crt_status == 0:
        return render_template("Blacklisted.html")  #message when user is blacklisted

    if user.crt_status == 1 and any(role.name == 'creator' for role in user.roles): 
        
        scount=len(list(Songs.query.filter_by(singer_id=user.uid)))
        alcount=len(list(Album.query.filter_by(singer_id=user.uid)))

        data=db.session.query(Review.s_id,db.func.avg(Review.rev).label('average_rev')).\
        filter(Review.singer_id == user.uid).group_by(Review.s_id).\
        order_by(db.func.avg(Review.rev).desc()).all()
        l=[]
        for i in data:
            d=Songs.query.get(i[0])
            l.append(d)

        ld=Songs.query.all()
        
           
        alb=Album.query.filter_by(singer_id=user.uid)
        print(alb)
        return render_template("Cdash.html",alb=alb,l=l,data=data,scount=scount,alcount=alcount,user=user)
    
    else:
        return redirect("/addcreator")
    


@app.route("/addcreator",methods=["GET","POST"])
@login_required
def addcreator():
    if request.method=="GET":
        return render_template("Addcrt.html")
    
    else:
        user=current_user
        data=Role.query.get(2)
        user.roles.append(data)
        db.session.commit()
        flash("You're a creator now!!!","creator")
        return redirect("/creator") 
    


@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method=="GET":
        return render_template("admin.html")
    

    else:
        
        email = request.form.get("email")
        password = request.form.get("password")
        useri = User.query.filter_by(email=email).first()


        if useri is None:
            flash("Incorrect email id entered please try again!!","nodata")
            return redirect("/admin")
        elif verify_password(password, useri.password) and any(role.name == 'admin' for role in useri.roles) :
            login_user(useri)
            user=current_user
            return redirect("/adash")
        else:
            flash("Invalid EmailID or Password!!!","notadmin")
            return redirect("/admin") 
          


@app.route("/upload",methods=["GET","POST"])
@login_required
def upload():
    user=current_user
    albs=Album.query.filter_by(singer_id=user.uid)
    if request.method=="GET":
        return render_template("Upload.html",albs=albs)
    else:
        name=request.form.get("title")
        singer=user.firstname
        file=request.files.get("file")
        genre=request.form.get("genre")
        date=request.form.get("release_date")
        albid=request.form.get("select_album")
        sid=user.uid
        data=Songs(s_name=name,s_singer=singer,s_genre=genre,date=date,singer_id=sid)
        db.session.add(data)
        db.session.commit()
        obj=Salbum(song_id=data.s_id,album_id=albid)
        db.session.add(obj)
        db.session.commit()
        file.save('./static/'+str(data.s_id)+'.mp3')

        flash("Song Uploaded Successfully","addsong")
        return redirect("/creator")
    


@app.route("/play/<id>",methods=["GET","POST"])
@login_required
def play(id):
    user=current_user
    sing=Songs.query.get(id)
    d=Review.query.filter_by(uid=user.uid,s_id=id).first()
    d2=Review.query.filter_by(s_id=id)
    count=0
    sum=0
    for i in d2:
        sum=i.rev
        count+=1
    if count==0:
        avgrev=None
    else:
        avgrev=sum/count
    return render_template("play.html",song=sing,user=user,d=d,avgrev=avgrev)
    
        


@app.route("/viewsongs",methods=["GET","POST"])
@login_required
def viewsongs():
    sing=Songs.query.all()
    return render_template("viewsongs.html",s=sing)



@app.route("/review/<s_id>/<singer_id>",methods=["GET","POST"])
@login_required
def review(s_id,singer_id):
    user=current_user
    sing=Songs.query.get(s_id) #object for doing review
    d=Review.query.filter_by(uid=user.uid,s_id=s_id).first() #object to check review is done or not
    if request.method=="GET":
        if d is None:
            return render_template("Review.html",song=sing)
        else:
            check=d.rev
            return render_template("Review.html",song=sing,rev=check)
    elif d is None:
        uid=user.uid
        sid=s_id
        singid=singer_id
        rev=request.form.get("rev")
        data=Review(uid=uid,s_id=sid,rev=rev,singer_id=singid)
        db.session.add(data)
        db.session.commit()
        flash("Review submitted Successfulllly!")
        return redirect(url_for("play",id=sid))
    else:
        data=Review.query.filter_by(s_id=s_id,uid=user.uid).first()
        data.rev=request.form.get("rev")
        db.session.commit()
        flash("Review submitted Successfulllly!")    
        return redirect(url_for("play",id=s_id))





@app.route("/genresongs/<gen>",methods=["GET","POST"])
@login_required
def genresongs(gen):
    s=Songs.query.all()
    return render_template("Genresongs.html",gen=gen,s=s)



@app.route("/viewgenres",methods=["GET","POST"])
@login_required
def viewgenres():
    sing=Songs.query.all()
    l=[]
    for i in sing:
        if i.s_genre not in l:
            l.append(i.s_genre)
    return render_template("Viewgenres.html",s=sing,l=l)



@app.route("/crtplaylist",methods=["GET","POST"])
@login_required
def crtplaylist():
    user=current_user
    if request.method=="GET":
        return render_template("crtplaylist.html")
    else:
        name=request.form.get("playlistname")
        uid=user.uid
        checkdup=Playlist.query.filter_by(playlist_name=name,user_id=uid).first()
        if checkdup is None:
            data=Playlist(playlist_name=name,user_id=uid)
            db.session.add(data)
            db.session.commit()
            flash("Added Succesfully!!")
            return redirect("/viewplaylist")
        else:
            flash("Please use a diffrent name","newplst")
            return redirect("/crtplaylist") 
    
    

@app.route("/viewplaylist",methods=["GET","POST"])
@login_required
def viewplaylist():
    user=current_user
    ptable=Playlist.query.filter_by(user_id=user.uid).all()
    return render_template("viewplaylist.html",ptable=ptable)



@app.route("/plistsongs/<plid>",methods=["GET","POST"])
@login_required
def plistsongs(plid):
    plist=Splaylist.query.filter_by(pl_id=plid).all()
    song=Songs.query.all()
    showplst=Playlist.query.get(plid)
    return render_template("plistsongs.html",plist=plist,song=song,showplst=showplst,plid=plid)
    


@app.route("/removeplistsong/<plid>/<id>")
@login_required
def removeplistsong(id,plid):
    obj=Splaylist.query.get(id)
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for("plistsongs",plid=plid))




@app.route("/addtoplaylist/<sid>",methods=["GET","POST"])
@login_required
def addtoplaylist(sid):
    user=current_user
    plist=Playlist.query.filter_by(user_id=user.uid)
    if request.method=="GET":
        return render_template("addtoplaylist.html",plist=plist,sid=sid)
    else:
        val=request.form.get("select_playlist")
        pl=Splaylist.query.filter_by(pl_id=val,s_id=sid).first()
        if pl is None:
            data=Splaylist(pl_id=val,s_id=sid)
            db.session.add(data)
            db.session.commit()
            flash("Song Added Successfully!!!")
            return redirect(url_for("play",id=sid))
        else:
            flash("Song Already There!!!")
            return redirect(url_for("addtoplaylist",sid=sid))




@app.route("/removeplaylist/<plid>",methods=["GET","POST"])
@login_required
def removeplaylist(plid):
    user=current_user
    plist=Playlist.query.filter_by(playlist_id=plid).first()
    pslid=Splaylist.query.filter_by(pl_id=plid)
    db.session.delete(plist)
    for i in pslid:
        db.session.delete(i) 
    db.session.commit()
    return redirect("/viewplaylist")



@app.route("/albmsongs/<albmid>",methods=["GET","POST"])
@login_required
def albmsongs(albmid):
    alb=Salbum.query.filter_by(album_id=albmid).all()
    song=Songs.query.all()
    showalb=Album.query.get(albmid)
    return render_template("albmsongs.html",song=song,alb=alb,showalb=showalb)    



@app.route("/viewalbums",methods=["GET","POST"])
@login_required
def viewalbums():
    user=current_user
    albm=Album.query.filter_by(singer_id=user.uid).all()
    return render_template("Viewalbums.html",albm=albm)



@app.route("/removealbmsong/<albid>/<id>")
@login_required
def removealbmsong(id,albid):
    obj=Salbum.query.get(id)
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for("albmsongs",albmid=albid))


@app.route("/crtalbum",methods=["GET","POST"])
@login_required
def crtalbum():
    user=current_user
    if request.method=="GET":
        return render_template("crtalbum.html")
    else:
        name=request.form.get("albumname")
        uid=user.uid
        checkdup=Album.query.filter_by(album_name=name,singer_id=uid).first()
        if checkdup is None:
            data=Album(album_name=name,singer_id=uid)
            db.session.add(data)
            db.session.commit()
            flash("Added Successfully!!")
            return redirect("/viewalbums")
        else:
            flash("Please use a diffrent Album name","crtalbum")
            return redirect("/crtalbum") 
        


@app.route("/crtsongs")
@login_required
def crtsongs():
    user=current_user
    data=Songs.query.filter_by(singer_id=user.uid).all()
    return render_template("crtsongs.html",data=data)



@app.route("/removefromcrt/<sid>")
@login_required
def removefromcrt(sid):
    song=Songs.query.get(sid)
    if song:
        # Delete
        if os.path.exists('./static/'+str(sid)+'.mp3'):
            os.remove('./static/'+str(sid)+'.mp3')
    db.session.delete(song)
    db.session.query(Splaylist).filter_by(s_id=sid).delete()
    db.session.query(Salbum).filter_by(song_id=sid).delete()
    db.session.query(Review).filter_by(s_id=sid,singer_id=song.singer_id).delete()
    db.session.commit()
    return redirect("/crtsongs")



@app.route("/creatorplay/<id>")
@login_required
def creatorplay(id):

    count=0
    sum=0
    user=current_user
    sing=Songs.query.get(id)
    d=Review.query.filter_by(s_id=id)
    for i in d:
        count=count+1
        sum=sum+i.rev
    if count==0:
        avgrev=None
    else:
        avgrev=sum/count
    return render_template("creatorplay.html",song=sing,avgrev=avgrev)

    


@app.route("/addtoalbum/<sid>" , methods=["GET","POST"])
@login_required
def addtoalbum(sid):
    user=current_user
    album=Album.query.filter_by(singer_id=user.uid)
    albsong=Salbum.query.filter_by(song_id=sid)
    if request.method=="GET":
        return render_template("addtoalbum.html",album=album,sid=sid,albsong=albsong)
    else:
        val=request.form.get("select_album")
        pl=Salbum.query.filter_by(song_id=sid).first()
        if pl is not None:
            pl.album_id=val
            db.session.commit()
            flash("Added Successfully!!!!","addtoalb")
            return redirect(url_for("creatorplay",id=sid))
        else:
            data=Salbum(album_id=val,song_id=sid)
            db.session.add(data)
            db.session.commit()
            flash("Added Successfully","addtoalb")
            return redirect(url_for("creatorplay",id=sid))
        



@app.route("/changesongdata/<sid>", methods=["GET","POST"])
@login_required
def changesongdata(sid):
    user=current_user
    albs=Album.query.filter_by(singer_id=user.uid)
    albson=Salbum.query.filter_by(song_id=sid).first()
    album_id = albson.album_id
    selector=Album.query.get(album_id)
    songobj=Songs.query.get(sid)
    if request.method=="GET":
        return render_template("Changesongdata.html",sid=sid,albson=albson,songobj=songobj,albs=albs,selector=selector)
    else:
        name=request.form.get("title")
        albumi=request.form.get("select_album")
        genre=request.form.get("genre")
        if albson is None:
            obj=Salbum(album_id=albumi,song_id=sid)
            db.session.add(obj)
        else:
            albson.album_id=albumi
        songobj.s_name=name
        songobj.s_genre=genre
        f=request.files.get("file")
        if f.filename!="":
            f.save('./static/'+str(songobj.s_id)+'.mp3')
        db.session.commit()
        flash("Updated Successfully!!!","updtsng")
        return redirect("/crtsongs")
    



@app.route("/removealbum/<albumid>")
@login_required
def removealbum(albumid):
    data=Album.query.get(albumid)
    db.session.query(Salbum).filter_by(album_id=albumid).delete()
    db.session.delete(data)
    db.session.commit()
    return redirect("/viewalbums")



@app.route("/uploadalbum",methods=["GET","POST"])
@login_required
def uploadalbum():
    user=current_user
    if request.method=="GET":
        return render_template("Uploadalbum.html")
    else:
        albumn=request.form.get("albumname")
        uid=user.uid
        checkdup=Album.query.filter_by(album_name=albumn,singer_id=uid).first()
        if checkdup is None:
            data=Album(album_name=albumn,singer_id=uid)
            db.session.add(data)
            db.session.commit()
            flash("Added successfully!!","upldalb")
            return redirect("/upload") #flash message that album added successfully
        else:
            flash("Please Choose A diffrent Album Name","unqalb")
            return redirect("/uploadalbum") #flash message that u have to change your album name
        


@app.route("/userviewalb")
@login_required
def userviewalb():
    albs=Album.query.all()
    return render_template("userviewalb.html",albs=albs)


@app.route("/Suserviewalb/<albid>")
@login_required
def Suserviewalb(albid):
    songal=Salbum.query.filter_by(album_id=albid).all()
    song=Songs.query.all()
    showalb=Album.query.get(albid)
    return render_template("Suserviewalb.html",songal=songal,song=song,showalb=showalb)



@app.route("/adminsongs")
@roles_required("admin")
def adminsongs():
    data=Songs.query.all()
    return render_template("Adminsongs.html",data=data)




@app.route("/deleteadminsng/<sid>")
@roles_required("admin")
def deleteadminsng(sid):
    song=Songs.query.get(sid)
    db.session.query(Splaylist).filter_by(s_id=sid).delete()
    db.session.query(Salbum).filter_by(song_id=sid).delete()
    db.session.query(Review).filter_by(s_id=sid,singer_id=song.singer_id).delete()
    if song:
        # Delete
        if os.path.exists('./static/'+str(sid)+'.mp3'):
            os.remove('./static/'+str(sid)+'.mp3')
    db.session.delete(song)
    db.session.commit()
    return redirect("/adminsongs")


    
@app.route("/adminplay/<sid>")
@roles_required("admin")
def adminplay(sid):
    count=0
    sum=0
    sing=Songs.query.get(sid)
    d=Review.query.filter_by(s_id=sid)
    for i in d:
        count=count+1
        sum=sum+i.rev
    if count==0:
        avgrev=None
    else:
        avgrev=sum/count
    return render_template("Adminplay.html",song=sing,avgrev=avgrev,d=d)
    


@app.route("/adminalbums")
@roles_required("admin")
def adminalbums():
    alb=Album.query.all()
    return render_template("Adminalbums.html",alb=alb)



@app.route("/adminalbumsng/<aid>")
@roles_required("admin")
def adminalbumsng(aid):
    alb=Salbum.query.filter_by(album_id=aid)
    song=Songs.query.all()
    showalb=Album.query.get(aid)
    return render_template("Adminalbumsng.html",song=song,alb=alb,showalb=showalb)    



@app.route("/adminremovealb/<aid>")
@roles_required("admin")
def adminremovealb(aid):
    data=Album.query.get(aid)
    db.session.query(Salbum).filter_by(album_id=aid).delete()
    db.session.delete(data)
    db.session.commit()
    return redirect("/adminalbums")


@app.route("/admincreators")
@roles_required("admin")
def admincreators():
    d=User.query.all()
    e="creator"
    l=[]
    for i in d:
        if e in i.roles:
            l.append(i)
    return render_template("Admincreators.html",l=l)



@app.route("/crtstatus/<uid>/<num>",methods=["GET","POST"])
@roles_required("admin")
def crtstatus(uid,num):
    if request.method=="POST":
        data=User.query.get(uid)
        data.crt_status=num
        db.session.commit()
        return redirect(url_for("creatorprofile",uid=uid)) 
    


@app.route("/creatorprofile/<uid>")
@roles_required("admin")
def creatorprofile(uid):
    scount=len(list(Songs.query.filter_by(singer_id=uid)))
    alcount=len(list(Album.query.filter_by(singer_id=uid)))
    s=User.query.get(uid)
    data1=Album.query.filter_by(singer_id=uid).all()
    data2=Songs.query.filter_by(singer_id=uid).all()
    count=0
    sum=0
    data3=Review.query.filter_by(singer_id=uid)
    for i in data3:
        count=count+1
        sum=sum+i.rev
    if count==0:
        avgrev=None
    else:
        avgrev=sum/count


    return render_template("Creatorprofile.html",scount=scount,alcount=alcount,s=s,data1=data1,data2=data2,uid=uid,avgrev=avgrev)




@app.route("/topsongs")
@login_required
def topsongs():
   
    l=db.session.query(Review.s_id,db.func.avg(Review.rev).label('average_rev')).group_by(Review.s_id).order_by(db.func.avg(Review.rev).desc()).all()
    data=[]
    for i in l:
        d=Songs.query.get(i[0])
        data.append(d)
    return render_template("Topsongs.html",data=data,l=l)



@app.route("/admingenresongs/<gen>",methods=["GET","POST"])
@roles_required("admin")
def admingenresongs(gen):
    s=Songs.query.all()
    return render_template("Admingenresongs.html",gen=gen,s=s)




@app.route("/admingenres",methods=["GET","POST"])
@roles_required("admin")
def admingenres():
    sing=Songs.query.all()
    l=[]
    for i in sing:
        if i.s_genre not in l:
            l.append(i.s_genre)
    return render_template("Admingenres.html",s=sing,l=l)



@app.route('/seesearchsong/<crtid>')
@login_required
def seesearchsong(crtid):
    data = Songs.query.filter_by(singer_id = crtid).all()
    return render_template('Seesearchsong.html',data=data)



@app.route('/seesearchalbum/<crtid>')
@login_required
def seesearchalbum(crtid):
    data = Album.query.filter_by(singer_id = crtid).all()
    return render_template('Seesearchalbum.html',data=data)



    
@app.route("/adminsearch/<d>")
@roles_required("admin")
def adminsearch(d):
    if d!=" " and d!="  ":
        results = db.session.query(Songs).filter(Songs.s_name.ilike(f'%{d}%')).all()
        result = db.session.query(User).filter(User.firstname.ilike(f'%{d}%')).all()
        resultscrt=[]
        for i in result:
            if "creator" in i.roles:
                resultscrt.append(i)
        resultsal = db.session.query(Album).filter(Album.album_name.ilike(f'%{d}%')).all()
        resultsgen = db.session.query(Songs).filter(Songs.s_genre.ilike(f'%{d}%')).all()
        return render_template("Adminsearch.html",results=results,resultscrt=resultscrt,d=d,resultsal=resultsal,resultsgen=resultsgen)
    else:  
        results=[]
        resultsal=[]
        resultsgen=[]
        resultscrt=[]
        return render_template("Adminsearch.html",results=results,resultsal=resultsal,resultsgen=resultsgen
                                ,resultscrt=resultscrt,d=d)
        



@app.route("/deletesearchsong/<mid>/<d>")
@roles_required("admin")
def deltesearchsong(mid,d):
    song=Songs.query.get(mid)
    if song:
        # Delete
        if os.path.exists('./static/'+str(mid)+'.mp3'):
            os.remove('./static/'+str(mid)+'.mp3')
    db.session.delete(song)
    db.session.query(Splaylist).filter_by(s_id=mid).delete()
    db.session.query(Salbum).filter_by(song_id=mid).delete()
    db.session.query(Review).filter_by(s_id=mid,singer_id=song.singer_id).delete()
    db.session.commit()
    return redirect(url_for("adminsearch",d=d))



@app.route("/deletesearchalbum/<albid>/<d>")
@roles_required("admin")
def deletesearchalbum(albid,d):
    data=Album.query.get(albid)
    db.session.query(Salbum).filter_by(album_id=albid).delete()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("adminsearch",d=d))



@app.route("/adminsearchdltal/<albid>/<uid>")
@roles_required("admin")
def adminsearchdltal(albid,uid):
    data=Album.query.get(albid)
    db.session.query(Salbum).filter_by(album_id=albid).delete()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("creatorprofile",uid=uid))



@app.route("/adminsearchdlts/<sngid>/<uid>")
@roles_required("admin")
def adminsearchdeletesng(sngid,uid):
    song=Songs.query.get(sngid)
    if song:
        # Delete
        if os.path.exists('./static/'+str(sngid)+'.mp3'):
            os.remove('./static/'+str(sngid)+'.mp3')
    db.session.delete(song)
    db.session.query(Splaylist).filter_by(s_id=sngid).delete()
    db.session.query(Salbum).filter_by(song_id=sngid).delete()
    db.session.query(Review).filter_by(s_id=sngid,singer_id=song.singer_id).delete()
    db.session.commit()
    return redirect(url_for("creatorprofile",uid=uid))




@app.route("/addnewalbtochange/<sngid>",methods=["GET","POST"])
@login_required
def addnewalbtochange(sngid):
    user=current_user
    if request.method=="GET":
        return render_template("Addnewalbtochange.html",s=sngid)
    else:
        albumn=request.form.get("albumname")
        uid=user.uid
        checkdup=Album.query.filter_by(album_name=albumn,singer_id=uid).first()
        if checkdup is None:
            data=Album(album_name=albumn,singer_id=uid)
            db.session.add(data)
            db.session.commit()
            flash("Added Successfully","upldalb")
            return redirect(url_for("addtoalbum",sid=sngid)) #flash message that album added successfully
        else:
            flash("Please use a diffrent Album Name")
            return redirect(url_for("addnewalbtochange",sngid=sngid)) #flash message that u have to change your album name
        



@app.route("/addnewplttochange/<sngid>",methods=["GET","POST"])
@login_required
def addnewplttochange(sngid):
    user=current_user
    if request.method=="GET":
        return render_template("Addnewplttochange.html",sngid=sngid)
    else:
        name=request.form.get("playlistname")
        uid=user.uid
        checkdup=Playlist.query.filter_by(playlist_name=name,user_id=uid).first()
        if checkdup is None:
            data=Playlist(playlist_name=name,user_id=uid)
            db.session.add(data)
            db.session.commit()
            flash("Added Successfully","upldplst")
            return redirect(url_for("addtoplaylist",sid=sngid))
        else:
            flash("Please use a diffrent Playlist Name")
            return redirect(url_for("addnewplttochange",sngid=sngid)) #flash message that u have to change your playlist name





@app.route("/updateplstname/<plit>",methods=["GET","POST"])
@login_required
def updateplstname(plit):
    user=current_user
    if request.method=="GET":
        return render_template("updateplstname.html",plit=plit)
    else:
        data=request.form.get("plstname")
        check=Playlist.query.get(plit)
        check1=Playlist.query.filter_by(playlist_name=data,user_id=user.uid).first()
        if check1 is not None :
            flash("Please Choose a diffrent name!")
            return redirect(url_for("updateplstname",plit=plit))
        else:
            check.playlist_name=data
            db.session.commit()
            flash("Changed Successfully!!")
            return redirect(url_for("plistsongs",plid=plit))
        





@app.route("/updatealbname/<albid>",methods=["GET","POST"])
@login_required
def updatealbname(albid):
    user=current_user
    if request.method=="GET":
        return render_template("updatealbname.html",albid=albid)
    else:
        data=request.form.get("albmname")
        check=Album.query.get(albid)
        check1=Album.query.filter_by(album_name=data,singer_id=user.uid).first()
        if check1 is not None:
            flash("Please Choose a diffrent name!")
            return redirect(url_for("updatealbname",albid=albid))
        else:
            check.album_name=data
            db.session.commit()
            flash("Changed Successfully!!")
            return redirect(url_for("albmsongs",albmid=albid))



@app.route("/logoutuser")
@login_required
def logoutuser():
    logout_user()
    flash("logged out successfully")
    return redirect("/")


@app.route("/adminusers",methods=["GET","POST"])
@roles_required("admin")
def adminusers():
    data=User.query.all()
    return render_template("Adminusers.html",data=data)



#API


class SongApi(Resource):
    def get(self):
        sid = request.get_json().get('sid')
        song = Songs.query.get(sid)
        if song is None:
            return 'song not found',404
        return {
            'id':song.s_id,
            'name':song.s_name,
            'singer':song.s_singer,
            'genre':song.s_genre
        },200
    


    def post(self):
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        name=request.form.get("title")
        singer=user.firstname
        file=request.files.get("file")
        genre=request.form.get("genre")
        date=request.form.get("release_date")
        albid=request.form.get("select_album")
        sid=user.uid
        data=Songs(s_name=name,s_singer=singer,s_genre=genre,date=date,singer_id=sid)
        db.session.add(data)
        db.session.commit()
        obj=Salbum(song_id=data.s_id,album_id=albid)
        db.session.add(obj)
        db.session.commit()
        file.save('./static/'+str(data.s_id)+'.mp3')
        return {'song_id':data.s_id},200
    


    def put(self):
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        sid = request.form.get('song_id')
        albs=Album.query.filter_by(singer_id=user.uid)
        albson=Salbum.query.filter_by(song_id=sid).first()
        songobj=Songs.query.get(sid)
        name=request.form.get("title")
        albumi=request.form.get("select_album")
        genre=request.form.get("genre")
        if albson is None:
            obj=Salbum(album_id=albumi,song_id=sid)
            db.session.add(obj)
        else:
            albson.album_id==albumi
        songobj.s_name=name
        songobj.s_genre=genre
        f=request.files.get("file")
        if f.filename!="":
                f.save('./static/'+str(songobj.s_id)+'.mp3')
        db.session.commit()
        return {'msg':'Song Updated Successfully!!!'},200
    


    def delete(self):
        sid = request.get_json().get('sid')
        song=Songs.query.get(sid)
        db.session.query(Splaylist).filter_by(s_id=sid).delete()
        db.session.query(Salbum).filter_by(song_id=sid).delete()
        db.session.query(Review).filter_by(s_id=sid,singer_id=song.singer_id).delete()
        if song is None:
            return 'Song not found',404
        if song:
            if os.path.exists('./static/'+str(sid)+'.mp3'):
                os.remove('./static/'+str(sid)+'.mp3')
        db.session.delete(song)
        db.session.commit()
        return {'msg':'Song Removed Successfully!!!'},200


class PlaylistApi(Resource):

    def get(self):
        playlist_id = request.get_json().get('playlist_id')
        playlist = Playlist.query.get(playlist_id)
        if playlist is None:
            return 'playlist not found',404
        return {
            'playlist_id':playlist.playlist_id,
            'playlist_name':playlist.playlist_name,
            'user_id':playlist.user_id
        },200
    

    def post(self):
        user_id=request.get_json().get("user_id")
        name=request.get_json().get("name")
        data=Playlist(playlist_name=name,user_id=user_id)
        db.session.add(data)
        db.session.commit()
        return {'msg':'Playlist Added Succesfully!!'},200
    
    
    def put(self):
        user_id=request.get_json().get("user_id")
        playlist_id=request.get_json().get("playlist_id")
        name=request.get_json().get("name")
        playlist = Playlist.query.get(playlist_id)
        if playlist is None:
            return 'playlist not found',404
        playlist.playlist_name = name
        playlist.user_id = user_id
        db.session.commit()
        return {'msg':'Playlist Updated Succesfully!!'},200
    

    def delete(self):
        playlist_id=request.get_json().get("playlist_id")
        playlist = Playlist.query.get(playlist_id)
        if playlist is None:
            return 'playlist not found',404
        db.session.delete(playlist)
        pslid=Splaylist.query.filter_by(pl_id=playlist_id)
        for i in pslid:
            db.session.delete(i) 
            db.session.commit()
        return {'msg':'Playlist Removed Succesfully!!'},200



api.add_resource(SongApi,'/api/song')
api.add_resource(PlaylistApi,'/api/playlist')


if __name__ == '__main__':
    app.run(debug=True)









 
#check all the routes admin
