from flask import Flask,render_template,redirect,request, flash, url_for
import matplotlib.pyplot as plt
import matplotlib
from flask_login import LoginManager, login_user,current_user,logout_user, login_required
from datetime import datetime
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.secret_key = 'My_secret_key'
db=SQLAlchemy()
db.init_app(app)

login_manager=LoginManager()
login_manager.init_app(app)

app.app_context().push()

class Admin(db.Model):
    __tablename__="admin"
    admin_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name=db.Column(db.String,unique=True,nullable=False)
    mobile=db.Column(db.Integer,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    venue= db.relationship("Venue", secondary="venuecreated")


class Venue(db.Model):
    __tablename__="venue"
    venue_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    venue_name = db.Column(db.String,nullable=False)
    place = db.Column(db.String,nullable=False)
    location = db.Column(db.String,nullable=False)
    Screen=db.Column(db.Integer,nullable=False)
    show=db.relationship("Show", backref='ven',secondary="showcreated")

class VenueCreated(db.Model):
    __tablename__="venuecreated"
    vc_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    cadmin_id=db.Column(db.Integer, db.ForeignKey("admin.admin_id"), nullable=False)
    cvenue_id=db.Column(db.Integer, db.ForeignKey("venue.venue_id"),nullable=False)

class Show(db.Model):
    __tablename__="show"
    show_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_name=db.Column(db.String,nullable=False)
    rating=db.Column(db.Integer,nullable=False)
    trailer=db.Column(db.String,nullable=True)
    movie_description=db.Column(db.String,nullable=True)
    timing = db.Column(db.DateTime(timezone=True), default=datetime.utcnow,nullable=False)
    tags = db.Column(db.String,nullable=False)
    screenNumber=db.Column(db.Integer,nullable=False)
    seats=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Integer,nullable=False)
    amount_recieved=db.Column(db.Integer,nullable=True)

class ShowCreated(db.Model):
    __tablename__="showcreated"
    sc_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    cshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)
    cvenue_id=db.Column(db.Integer, db.ForeignKey("venue.venue_id"),nullable=False)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name=db.Column(db.String,unique=True,nullable=False)
    mobile=db.Column(db.Integer,unique=True,nullable=False)
    city=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)

class ShowBooked(db.Model):
    sb_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    seats_booked=db.Column(db.Integer,nullable=False)
    showname=db.Column(db.String,nullable=False)
    showtime=db.Column(db.DateTime(timezone=True), default=datetime.utcnow,nullable=False)
    venuename=db.Column(db.String,nullable=False)
    venuelocation=db.Column(db.String,nullable=False)
    venueplace=db.Column(db.String,nullable=False)
    Total_price=db.Column(db.Integer,nullable=False)
    bshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)
    buser_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Rate(db.Model):
    r_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    rating=db.Column(db.Integer,nullable=False)
    showname=db.Column(db.String,nullable=False)
    review=db.Column(db.String,nullable=False)
    ruser_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)

#----------------------------------------------------------------------------------------#
@login_manager.user_loader
def user_loader(user_id):
    return User.query.filter_by(id=user_id).first()

#----------------------------------------------------------------------------------------#
@app.route('/',methods=["GET","POST"])
def home():
    return render_template("home.html")
#----------------------------------------------------------------------------------------#

@app.route('/admin',methods=["GET","POST"])
def admin():
    if request.method=="GET":
        return render_template("adminlogin.html")
    if request.method=="POST":
        name=str(request.form['admin_name'])
        pwd=str(request.form['password'])
        ad=Admin.query.filter(Admin.admin_name==name,Admin.password==pwd).first()
        if ad:
            id=ad.admin_id
            return redirect(url_for("admin_venue",id=id))
        else:
            flash('Invalid admin name or password','danger')
            return redirect(url_for('admin'))
#----------------------------------------------------------------------------------------#
        
@app.route('/admin/create',methods=["GET","POST"])
def admincreate():
    if request.method=="GET":
        return render_template("admincreate.html")
    if request.method=="POST":
        name=str(request.form['admin_name'])
        mobile=str(request.form['mobile'])
        pwd=str(request.form['password'])

        ad = Admin.query.filter(or_(Admin.admin_name == name, Admin.mobile == mobile)).first()

        if ad:
            flash('admin name/mobile already exist','danger')
            return redirect(url_for('admincreate'))

        use=Admin(admin_name=name,mobile=mobile,password=pwd)
        db.session.add(use)
        db.session.commit()
        return redirect('/admin')
        
@app.route('/admin/venue/<id>')
def admin_venue(id):
    ad=Admin.query.filter_by(admin_id=id).first()
    ven=ad.venue
    if ven!=[]:
        s=[]
        for j in ven:
            sho=j.show
            s.append(sho)
        d={}
        for a in range(len(ven)):
            d[ven[a]]=s[a]
        return render_template("venuecreate.html",ven=d,id=id)
    else:
        return render_template("novenue.html",id=id)
#----------------------------------------------------------------------------------------#
        
@app.route('/admin/venue/create/<id>',methods=["GET","POST"])
def create_venue(id):
    if request.method=="GET":
        return render_template("venueform.html",id=id)
    if request.method=="POST":
        vname=request.form['venue_name']
        place=request.form['place']
        location=request.form['location']
        screen=request.form['screen']
        v=Venue(venue_name=vname,place=place,location=location,Screen=screen)
        db.session.add(v)
        db.session.commit()
        vid=v.venue_id
        vc=VenueCreated(cadmin_id=id,cvenue_id=vid)
        db.session.add(vc)
        db.session.commit()
        si="/admin/venue/"+str(id)
        return redirect(si)
#----------------------------------------------------------------------------------------#    


@app.route('/admin/venue/<a_id>/update/<v_id>',methods=["GET","POST"])
def update_venue(a_id,v_id):
    if request.method=="GET":
        ven=Venue.query.filter_by(venue_id=v_id).first()
        return render_template("updatevenue.html",ven=ven,id=a_id)
    if request.method=="POST":
        vname=request.form['venue_name']
        place=request.form['place']
        location=request.form['location']
        Venue.query.filter_by(venue_id=v_id).update({'venue_name':vname,'place': place,'location':location})
        db.session.commit()
        si="/admin/venue/"+str(a_id)
        return redirect(si)
#----------------------------------------------------------------------------------------#
    
@app.route('/admin/venue/<a_id>/delete/<v_id>',methods=["GET","POST"])
def delete_venue(a_id,v_id):
    if request.method=='GET':
        return render_template('confirmvenuedelete.html',a_id=a_id,v_id=v_id)
    if request.method=='POST':
        v=Venue.query.filter_by(venue_id=v_id).first()
        show=v.show
        for i in show:
            db.session.delete(i)
        ShowCreated.query.filter_by(cvenue_id=v_id).delete()
        VenueCreated.query.filter_by(cvenue_id=v_id).delete()
        Venue.query.filter_by(venue_id=v_id).delete()
        db.session.commit()
        si="/admin/venue/"+str(a_id)
        return redirect(si)       
#----------------------------------------------------------------------------------------#

@app.route('/admin/show/<a_id>/<v_id>',methods=["GET","POST"])
def show(a_id,v_id):
    if request.method=="GET":
        return render_template("showform.html",admin_id=a_id,venue_id=v_id)
    if request.method=="POST":
        showname=request.form["show_name"]
        rate=int(request.form["rating"])
        time=request.form["timing"]
        timing_value = datetime.strptime(str(time), '%Y-%m-%dT%H:%M')
        ti=str(timing_value)
        tags=request.form["tags"]
        seats=request.form["seats"]
        screen=request.form["screen"]
        trailer=request.form["trailer"]
        trailer="https://www.youtube.com/embed/"+str(trailer[17:])
        movie_description=request.form["movie description"]
        price=request.form["price"]
        if not price.isnumeric() or not seats.isnumeric():
            flash('Price and Seats must be in numbers')
            return redirect(url_for('show',a_id=a_id,v_id=v_id))
        ven=Venue.query.filter_by(venue_id=v_id).first()
        show=ven.show
        sname=[]
        tim=[]
        for s in show:
            sname.append(s.show_name)
            tim.append(s.timing.strftime('%Y-%m-%d %H:%M:%S'))
        if sname!=[] and tim!=[]:
            if showname in sname and ti not in tim:
                s=Show(show_name=showname,rating=rate,timing=timing_value,tags=tags,trailer=trailer,movie_description=movie_description,screenNumber=screen,seats=seats,price=price)
                db.session.add(s)
                db.session.commit()
                s_id=s.show_id
                sc=ShowCreated(cshow_id=s_id,cvenue_id=v_id)
                db.session.add(sc)
                db.session.commit()
                si="/admin/venue/"+str(a_id)
                return redirect(si)
            if showname not in sname:
                s=Show(show_name=showname,rating=rate,timing=timing_value,tags=tags,trailer=trailer,movie_description=movie_description,screenNumber=screen,seats=seats,price=price)
                db.session.add(s)
                db.session.commit()
                s_id=s.show_id
                sc=ShowCreated(cshow_id=s_id,cvenue_id=v_id)
                db.session.add(sc)
                db.session.commit()
                si="/admin/venue/"+str(a_id)
                return redirect(si)  

            else:
                flash('time already exist','danger')
                return redirect(url_for('show',a_id=a_id,v_id=v_id))
        else:
            s=Show(show_name=showname,rating=rate,timing=timing_value,tags=tags,trailer=trailer,movie_description=movie_description,screenNumber=screen,seats=seats,price=price)
            db.session.add(s)
            db.session.commit()
            s_id=s.show_id
            sc=ShowCreated(cshow_id=s_id,cvenue_id=v_id)
            db.session.add(sc)
            db.session.commit()
            si="/admin/venue/"+str(a_id)
            return redirect(si)  
#----------------------------------------------------------------------------------------#        
              
@app.route('/admin/show/<a_id>/update/<s_id>',methods=["GET","POST"])
def update_show(a_id,s_id):
    if request.method=="GET":
        sho=Show.query.filter_by(show_id=s_id).first()
        return render_template("showupdate.html",show=sho,id=a_id)
    if request.method=="POST":
        showname=request.form["show_name"]
        rate=int(request.form["rating"])
        screennum=int(request.form["snumber"])
        tags=request.form["tags"]
        price=request.form["price"]
        if not price.isnumeric():
            flash('Price value must be in numbers')
            return redirect(url_for('update_show',a_id=a_id,s_id=s_id))
        Show.query.filter_by(show_id=s_id).update({'show_name':showname,'rating': rate,'screenNumber':screennum,'tags':tags,'price':price})
        db.session.commit()
        si="/admin/venue/"+str(a_id)
        return redirect(si)
    else:
        return "<h1>time already exist</h1>"
#----------------------------------------------------------------------------------------#
            


@app.route('/admin/show/<a_id>/delete/<s_id>',methods=["GET","POST"])
def delete_show(a_id,s_id):
    if request.method=='GET':
        return render_template('confirmshowdelete.html',a_id=a_id,s_id=s_id)
    if request.method=='POST':
        ShowCreated.query.filter_by(cshow_id=s_id).delete()
        Show.query.filter_by(show_id=s_id).delete()
        db.session.commit()
    si="/admin/venue/"+str(a_id)
    return redirect(si)
#----------------------------------------------------------------------------------------#

@app.route('/summary/<id>')
def summary(id):
    a=Admin.query.filter_by(admin_id=id).first()
    v=a.venue
    ven=[i.venue_name for i in v]
    s=[]
    for i in v:
        s.append(i.show)
    det=[]
    for j in s:
        de=[]
        for k in j:
            sname = k.show_name
            samnt = k.amount_recieved
            if samnt is not None:
                de.append([sname, samnt])
        det.append(de)
    d={}
    for i in range(len(ven)):
        d[ven[i]]=det[i]
    for key, values in d.items():
        x_values = [val[0] for val in values]
        y_values = [val[1] for val in values]
        matplotlib.use('Agg')
        plt.clf()
        plt.bar(x_values, y_values, color='b')
        plt.xlabel('Title')
        plt.ylabel('Amount Recived')
        plt.title(f'{key}')
        plt.savefig("static/"+f"{key}.png")
    return render_template('summary.html',plot_data=ven,id=id)
#----------------------------------------------------------------------------------------#        

@app.route('/user',methods=["GET","POST"])
def user():
    if request.method=="GET":
        return render_template("userlogin.html")
    if request.method=="POST":
        name=str(request.form['user_name'])
        pwd=str(request.form['password'])
        ad=User.query.filter(User.user_name==name,User.password==pwd).first()
        if ad:
            login_user(ad)
            return redirect('/user/venue')
        else:
            flash('invaild username/password')
            return redirect(url_for('user'))
#----------------------------------------------------------------------------------------#        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/user')
#----------------------------------------------------------------------------------------#

@app.route('/user/create',methods=["GET","POST"])
def usercreate():
    if request.method=="GET":
        return render_template("usercreate.html")
    if request.method=="POST":
        name=str(request.form['user_name'])
        mobile=str(request.form['mobile'])
        city=str(request.form['city'])
        pwd=str(request.form['password'])

        users=User.query.filter(or_(User.user_name==name,User.mobile==mobile)).first()

        if users:
            flash('user name/mobile already exist ','danger')
            return redirect(url_for('usercreate'))


        use=User(user_name=name,mobile=mobile,city=city,password=pwd)
        db.session.add(use)
        db.session.commit()
        return redirect('/user')
#----------------------------------------------------------------------------------------#

@app.route('/user/venue')
@login_required
def user_venue():
    id=current_user.id
    now = datetime.now()
    user=User.query.filter_by(id=id).first()
    city=user.city
    ven=Venue.query.filter_by(place=city).all()
    if ven:
        s = []
        for venue in ven:
            shows = venue.show
            sorted_shows = sorted(shows, key=lambda x: x.timing)
            s.append(sorted_shows)
        d = {}
        for a in range(len(ven)):
            d[ven[a]]=s[a]
        return render_template("venuebook.html",ven=d,id=id,now=now)
    else:
        return render_template("noshow.html",id=id)
#----------------------------------------------------------------------------------------#

@app.route('/user/show/book/<v_id>/<s_id>',methods=['GET','POST'])
@login_required
def user_book(v_id,s_id):
    u_id=current_user.id
    if request.method=="GET":
        seats=Show.query.filter_by(show_id=s_id).first()
        return render_template("showbook.html",v_id=v_id,seats=seats)
    if request.method=="POST":
        Num= request.form['NOS']
        Tprice=request.form['Tprice']
        vn=Venue.query.filter_by(venue_id=v_id).first()
        vname=vn.venue_name
        vplace=vn.place
        vlocation=vn.location
        sh=Show.query.filter_by(show_id=s_id).first()
        s_name=sh.show_name
        stime=sh.timing
        sb=ShowBooked(seats_booked=int(Num),Total_price=int(Tprice),showname=s_name,showtime=stime,venuename=vname,venueplace=vplace,venuelocation=vlocation,bshow_id=s_id,buser_id=u_id)
        db.session.add(sb)
        show=Show.query.filter_by(show_id=s_id).first()
        if int(show.seats)< int(Num):
            flash('that many seats are not availabe','danger')
            return redirect(url_for('user_book',s_id=s_id,v_id=v_id))
        if show.amount_recieved is None:
            show.amount_recieved=int(Tprice)
        else:
            show.amount_recieved+=int(Tprice)
        show.seats-=int(Num)
        db.session.commit()
        return redirect(url_for("user_ticket",s_id=s_id))
#----------------------------------------------------------------------------------------#
@app.route('/user/ticket/<s_id>')
def user_ticket(s_id):
    id=current_user.id
    show=Show.query.filter_by(show_id=s_id).first()
    snum=show.screenNumber
    sbd=ShowBooked.query.filter(ShowBooked.buser_id==id,ShowBooked.bshow_id==s_id).all()
    if sbd:
        return render_template('ticket.html',sbd=sbd,snum=snum)
    else:
        return render_template('noticket.html')

@app.route('/user/show/details/<s_name>/')
def show_details(s_name):
    show=Show.query.filter_by(show_name=s_name).first()
    rate=Rate.query.filter_by(showname=s_name).all()
    name=[]
    for r in rate:
        r_id=r.ruser_id
        user=User.query.filter_by(id=r_id).first()
        name.append(user.user_name)
    d={}
    for i in range(len(name)):
        d[name[i]]=rate[i]
    return render_template("aboutshow.html",show=show,rate=d)


@app.route('/user/bookings')
@login_required
def user_booked():
    id=current_user.id
    sbd=ShowBooked.query.filter_by(buser_id=id).all()
    if sbd!=[]:
        show=[]
        for i in sbd:
            show.append(i.bshow_id)
        rat={}
        for i in sbd:
            s_id=i.bshow_id
            s=Show.query.filter_by(show_id=s_id).first()
            if s:
                sn=s.show_name
                r=Rate.query.filter(Rate.ruser_id==id,Rate.rshow_id==s_id).first()
                if r:
                    if sn not in rat:
                        rat[sn]=r.rating
                    else:
                        rat[sn]+=r.rating/2
                if not r:
                    if sn not in rat:
                        rat[sn]=0
        d={}
        for l in show:
            sh=Show.query.filter_by(show_id=l).first()
            if sh:
                venu=sh.ven
                if not venu:
                    return render_template("noshowbooked.html",id=id)

                for i in venu:
                    if i not in d:
                        d[i]=[sh]
                    else:
                        d[i]+=[sh]
        return render_template("showbooked.html",ven=d,id=id,rate=rat)
    else:
        return render_template("noshowbooked.html",id=id)
#----------------------------------------------------------------------------------------#
    
@app.route('/user/search',methods=['GET','POST'])
@login_required
def search():
    id=current_user.id
    if request.method=='POST':
        movie_name=request.form['movie']
        city=request.form['city']
        now = datetime.now()
        user=User.query.filter_by(id=id).first()
        usercity=user.city
        if movie_name and not city:
            ven=Venue.query.filter_by(place=usercity).all()
            if ven:
                s = []
                for venue in ven:
                    shows = venue.show
                    sorted_shows = sorted(shows, key=lambda x: x.timing)
                    s.append(sorted_shows)
                d = {}
                for a in range(len(ven)):
                    d[ven[a]]=s[a]
                return render_template("showsearchedbymovie.html",ven=d,id=id,movie=movie_name,now=now)
            else:
                return render_template("noshow.html",id=id)
        elif city and not movie_name:
            ven=Venue.query.filter_by(place=city).all()
            if ven:
                s = []
                for venue in ven:
                    shows = venue.show
                    sorted_shows = sorted(shows, key=lambda x: x.timing)
                    s.append(sorted_shows)
                d = {}
                for a in range(len(ven)):
                    d[ven[a]]=s[a]
                return render_template("showsearchedbycity.html",ven=d,id=id,city=city)
            else:
                return render_template("noshow.html",id=id)
        elif movie_name and city:
            ven=Venue.query.all()
            if ven:
                s = []
                for venue in ven:
                    shows = venue.show
                    sorted_shows = sorted(shows, key=lambda x: x.timing)
                    s.append(sorted_shows)
                d = {}
                for a in range(len(ven)):
                    d[ven[a]]=s[a]
                return render_template("showsearchedbymovieandcity.html",ven=d,id=id,city=city,movie=movie_name)
            else:
                return render_template("noshow.html",id=id)
        
        elif not movie_name or not city:
            return render_template('typeerror.html',id=id)
        else:
            return render_template("noshow.html",id=id)
#----------------------------------------------------------------------------------------#       

@app.route('/user/venueshows/<v_id>')
@login_required
def user_venueshows(v_id):
    id=current_user.id
    now = datetime.now()
    ven=Venue.query.filter_by(venue_id=v_id).all()
    if ven!=[]:
        s = []
        for venue in ven:
            shows = venue.show
            sorted_shows = sorted(shows, key=lambda x: x.timing)
            s.append(sorted_shows)
        d = {}
        for a in range(len(ven)):
            d[ven[a]]=s[a]
        return render_template("venueshows.html",ven=d,id=id,now=now)
    else:
        return render_template("noshow.html",id=id)
#----------------------------------------------------------------------------------------#

@app.route('/user/profile',methods=['GET','POST'])
@login_required
def user_profile():
    if request.method=="GET":
        id=current_user.id
        user=User.query.filter_by(id=id).first()
        return render_template('userprofile.html',user=user)
    if request.method=="POST":
        id=current_user.id
        name=str(request.form['user_name'])
        mobile=str(request.form['mobile'])
        city=str(request.form['city'])
        pwd=str(request.form['password'])
        user=User.query.filter_by(id=id).first()
        user.user_name=name
        user.mobile=mobile
        user.city=city
        user.password=pwd
        db.session.commit()
        return redirect('/user')
#----------------------------------------------------------------------------------------#

@app.route('/user/show/rate/<s_id>',methods=['GET','POST'])
@login_required
def rate(s_id):
    u_id=current_user.id
    if request.method=='GET':
        return render_template('rateform.html',u_id=u_id,s_id=s_id)
    if request.method=='POST':
        if 'rating' not in request.form or 'review' not in request.form:
            flash('please fill the rating and comments')
            return redirect(url_for('rate',u_id=u_id,s_id=s_id))  
        else:
            rate=int(request.form['rating'])
            review=request.form['review']
            sh=Show.query.filter_by(show_id=s_id).first()
            sn=sh.show_name
            shb=Rate(rating=rate,review=review,showname=sn,ruser_id=u_id,rshow_id=s_id)
            db.session.add(shb)
            sh.rating=(sh.rating+rate)//2
            db.session.commit()
            return redirect(url_for('user_booked'))
#----------------------------------------------------------------------------------------#

@app.route('/user/tagsearch/<tag>')
@login_required
def tag_search(tag):
    id=current_user.id
    now = datetime.now()
    user=User.query.filter_by(id=id).first()
    city=user.city
    ven=Venue.query.filter_by(place=city).all()
    if ven!=[]:
        s = []
        for venue in ven:
            shows = venue.show
            sorted_shows = sorted(shows, key=lambda x: x.timing)
            s.append(sorted_shows)
        d = {}
        for a in range(len(ven)):
            d[ven[a]]=s[a]
    return render_template('tagsearch.html',tag=tag,ven=d,now=now)
#----------------------------------------------------------------------------------------#

@app.route('/user/ratesearch/<rating>')
@login_required
def rate_search(rating):
    id=current_user.id
    rate=int(rating[0])
    now = datetime.now()
    user=User.query.filter_by(id=id).first()
    city=user.city
    ven=Venue.query.filter_by(place=city).all()
    if ven!=[]:
        s = []
        for venue in ven:
            shows = venue.show
            sorted_shows = sorted(shows, key=lambda x: x.timing)
            s.append(sorted_shows)
        d = {}
        for a in range(len(ven)):
            d[ven[a]]=s[a]
    return render_template('ratesearch.html',now=now,ven=d,rating=rate)
#----------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------#

if __name__=="__main__":
    app.run(debug=True)