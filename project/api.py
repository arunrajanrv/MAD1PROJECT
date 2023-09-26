from flask import Flask, make_response
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_



# ----------- Configurations --------------------------------------------------------#
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
api = Api(app)
CORS(app)
#----------------------------------------------------------------------------------------#



# ----------- Models -----------------------------------------------------------#
class Show(db.Model):
    __tablename__="show"
    show_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_name=db.Column(db.String,nullable=False)
    rating=db.Column(db.Integer,nullable=False)
    timing = db.Column(db.DateTime(timezone=True), default=datetime.utcnow,nullable=False)
    tags = db.Column(db.String,nullable=False)
    screenNumber=db.Column(db.Integer,nullable=False)
    seats=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Integer,nullable=False)
    amount_recieved=db.Column(db.Integer,nullable=True)

class Admin(db.Model):
    __tablename__="admin"
    admin_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name=db.Column(db.String,unique=True,nullable=False)
    mobile=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    venue= db.relationship("Venue", backref="adminn", secondary="venuecreated")

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

class ShowCreated(db.Model):
    __tablename__="showcreated"
    sc_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    cshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)
    cvenue_id=db.Column(db.Integer, db.ForeignKey("venue.venue_id"),nullable=False)

class User(db.Model):
    id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name=db.Column(db.String,unique=True,nullable=False)
    mobile=db.Column(db.String,unique=True,nullable=False)
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


# ----------- Exception Handling ------------------------------------------------------------#
class NotFoundError(HTTPException):
    def __init__(self, status_code, message=''):
        self.response = make_response(message, status_code)

class NotGivenError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

#----------------------------------------------------------------------------------------#


# ----------- Output Feilds -----------
admin_fields = {
    "admin_id": fields.Integer,
    "admin_name": fields.String,
    "mobile": fields.String,
    "password": fields.String
}
#----------------------------------------------------------------------------------------#
user_fields = {
    "id": fields.Integer,
    "user_name": fields.String,
    "mobile": fields.String,
    "city": fields.String,
    "password": fields.String
}
#----------------------------------------------------------------------------------------#
venue_fields = {
    "venue_id": fields.Integer,
    "venue_name": fields.String,
    "place": fields.String,
    "location": fields.String,
    "Screen": fields.String
}
#----------------------------------------------------------------------------------------#
show_fields = {
    "show_id": fields.Integer,
    "show_name": fields.String,
    "rating": fields.Integer,
    "timings": fields.DateTime(dt_format='rfc822'),
    "tags": fields.String,
    "screen number": fields.Integer,
    "seats": fields.Integer,
    "price": fields.Integer,
    "amount_recieved":fields.Integer
}
#----------------------------------------------------------------------------------------#
showbook_fields={
    "sb_id": fields.Integer,
    "seats_booked": fields.Integer,
    "showname": fields.String,
    "showtime": fields.DateTime(dt_format='rfc822'),
    "venuename": fields.String,
    "venueplace": fields.String,
    "venueloaction": fields.String,
    "Total_price": fields.Integer,
    "bshow_id": fields.Integer,
    "buser_id": fields.Integer
}
#----------------------------------------------------------------------------------------#
rate_fields={
    "r_id": fields.Integer,
    "rating": fields.Integer,
    "review": fields.String,
    "showname": fields.String,
    "ruser_id": fields.Integer,
    "rshow_id": fields.Integer
}
#----------------------------------------------------------------------------------------#
# ----------- Parsers -------------------------------------------------------------------#
admin_parse = reqparse.RequestParser()
admin_parse.add_argument("admin_name")
admin_parse.add_argument("mobile")
admin_parse.add_argument("password")
#----------------------------------------------------------------------------------------#
venue_parse = reqparse.RequestParser()
venue_parse.add_argument("venue_name")
venue_parse.add_argument("place")
venue_parse.add_argument("location")
venue_parse.add_argument("screen")
#----------------------------------------------------------------------------------------#
show_parse = reqparse.RequestParser()
show_parse.add_argument("showname")
show_parse.add_argument("ratings")
show_parse.add_argument("timings")
show_parse.add_argument("tags")
show_parse.add_argument("screen_number")
show_parse.add_argument("seats")
show_parse.add_argument("price")
show_parse.add_argument("amount_recieved")

#----------------------------------------------------------------------------------------#
user_parse = reqparse.RequestParser()
user_parse.add_argument("user_name")
user_parse.add_argument("mobile")
user_parse.add_argument("password")
user_parse.add_argument("city")
#----------------------------------------------------------------------------------------#
showbook_parse = reqparse.RequestParser()
showbook_parse.add_argument("NOS")
#----------------------------------------------------------------------------------------#
rate_parse = reqparse.RequestParser()
rate_parse.add_argument("rating")
rate_parse.add_argument("review")

# ----------- APIs ----------------------------------------------------------------------#

class VenueAPI(Resource):

    @marshal_with(venue_fields)
    def get(self, venue_id):
        venue = Venue.query.filter(Venue.venue_id == venue_id).first()

        if venue:
            return venue
        else:
            raise NotFoundError(status_code=404)
   
    @marshal_with(venue_fields)
    def put(self, venue_id):
       
        ven = Venue.query.filter(Venue.venue_id == venue_id).first()

        if ven is None:
            raise NotFoundError(status_code=404)
        
       
        args =venue_parse.parse_args()
        venue_name = args.get("venue_name", None)
        place = args.get("place", None)
        location = args.get("location", None)
        screen = args.get("screen", None)

        
        if venue_name is None:
            raise NotGivenError(status_code=400, error_code="VENUE001", error_message="Venue Name is required")
        
        
        if place is None:
            raise NotGivenError(status_code=400, error_code="VENUE002", error_message="place is required")
        
        if location is None:
            raise NotGivenError(status_code=400, error_code="VENUE003", error_message="Location is required")
        
        if screen is None:
            raise NotGivenError(status_code=400, error_code="VENUE004", error_message="Number of Screen is required")
        else:
            ven.venue_name = venue_name
            ven.place = place
            ven.location = location
            ven.Screen = screen
            db.session.commit()
            return ven,201
        

    
    def delete(self, venue_id):
        
        ven = Venue.query.filter(Venue.venue_id == venue_id).scalar()
        sc = ShowCreated.query.filter_by(cvenue_id=venue_id).scalar()
        vc = VenueCreated.query.filter_by(cvenue_id=venue_id).scalar()
        

      
        if ven is None or vc is None:
            raise NotFoundError(status_code=404)

        try:
            if sc:
                db.session.delete(sc)
            db.session.delete(vc)
            db.session.delete(ven)
            db.session.commit()
            return "successfully deleted", 200
        except Exception as e:
            db.session.rollback()
            return f"Error deleting show: {str(e)}", 500
        

  
    @marshal_with(venue_fields)
    def post(self,admin_id):
        
        args =venue_parse.parse_args()
        venue_name = args.get("venue_name", None)
        place = args.get("place", None)
        location = args.get("location", None)
        screen = args.get("screen", None)

       
        if venue_name is None:
            raise NotGivenError(status_code=400, error_code="VENUE001", error_message="Venue Name is required")
        
        
        if place is None:
            raise NotGivenError(status_code=400, error_code="VENUE002", error_message="place is required")
        
        if location is None:
            raise NotGivenError(status_code=400, error_code="VENUE003", error_message="Location is required")
        
        if screen is None:
            raise NotGivenError(status_code=400, error_code="VENUE004", error_message="screen is required")
        
        ven = Venue.query.filter(Venue.venue_name == venue_name,Venue.place == place,Venue.location == location).first()

     
        if ven is None:
            ven = Venue(venue_name = venue_name, place = place,location=location, Screen=screen)
            db.session.add(ven)
            db.session.commit()
            vid=ven.venue_id
            vc=VenueCreated(cadmin_id=admin_id,cvenue_id=vid)
            db.session.add(vc)
            db.session.commit()
            return ven, 201

       
        else:
            raise NotFoundError(status_code=409)
#----------------------------------------------------------------------------------------#
class ShowAPI(Resource):

   
    def get(self ,show_id):
        show = Show.query.filter(Show.show_id == show_id).first()

        if show:
            return {
                    "show_id": show.show_id,
                    "show_name": show.show_name,
                    "rating": show.rating,
                    "timings": show.timing.strftime('%d/%m/%Y %I:%M %p'),
                    "tags": show.tags,
                    "screen number": show.screenNumber,
                    "seats": show.seats,
                    "price": show.price,
                    "amount_recieved": show.amount_recieved
                    }
        else:
            raise NotFoundError(status_code=404)
   
    def put(self, show_id):
       
        show = Show.query.filter(Show.show_id == show_id).first()

        if show is None:
            raise NotFoundError(status_code=404)
        
        args = show_parse.parse_args()
        show_name = args.get("showname", None)
        ratings = args.get("ratings", None)
        tags = args.get("tags", None)
        screenNumber = args.get("screen_number", None)
        seats = args.get("seats", None)
        price = args.get("price", None)

        
        if show_name is None:
            raise NotGivenError(status_code=400, error_code="SHOW001", error_message="show_name is required")
        
        
        if ratings is None:
            raise NotGivenError(status_code=400, error_code="SHOW002", error_message="ratings is required")
        
        if tags is None:
            raise NotGivenError(status_code=400, error_code="SHOW003", error_message="tags is required")
        
        if screenNumber is None:
            raise NotGivenError(status_code=400, error_code="SHOW004", error_message="screen number is required")
        
        if seats is None:
            raise NotGivenError(status_code=400, error_code="SHOW005", error_message="seats is required")
        
        if price is None:
            raise NotGivenError(status_code=400, error_code="SHOW006", error_message="Price is required")
        else:
            show.show_name = show_name
            show.ratings=ratings
            show.tags=tags
            show.screenNumber=screenNumber
            show.price=price
            show.seats=seats
            db.session.commit()
    
            return {
                    "show_id": show.show_id,
                    "show_name": show.show_name,
                    "rating": show.rating,
                    "timings": show.timing.strftime('%d/%m/%Y %I:%M %p'),
                    "tags": show.tags,
                    "screen number": show.screenNumber,
                    "seats": show.seats,
                    "price": show.price,
                    "amount_recieved": show.amount_recieved
                    }
        
    def delete(self, show_id):
        show = Show.query.filter_by(show_id=show_id).scalar()
        cshow = ShowCreated.query.filter_by(cshow_id=show_id).scalar()

        if show is None or cshow is None:
            raise NotFoundError(status_code=404)

        try:
            db.session.delete(show)
            db.session.delete(cshow)
            db.session.commit()
            return "successfully deleted", 200
        except Exception as e:
            db.session.rollback()
            return f"Error deleting show: {str(e)}", 500

        
    def post(self,venue_id):
        
        args = show_parse.parse_args()
        show_name = args.get("showname", None)
        ratings = args.get("ratings", None)
        timings = args.get("timings", None)
        tags = args.get("tags", None)
        screenNumber = args.get("screen_number", None)
        seats = args.get("seats", None)
        price = args.get("price", None)

        if show_name is None:
            raise NotGivenError(status_code=400, error_code="SHOW001", error_message="show_name is required")

        if ratings is None:
            raise NotGivenError(status_code=400, error_code="SHOW002", error_message="ratings is required")

        if timings is None:
            raise NotGivenError(status_code=400, error_code="SHOW003", error_message="timings is required")

        if tags is None:
            raise NotGivenError(status_code=400, error_code="SHOW004", error_message="tags is required")

        if screenNumber is None:
            raise NotGivenError(status_code=400, error_code="SHOW005", error_message="screen number is required")

        if seats is None:
            raise NotGivenError(status_code=400, error_code="SHOW006", error_message="seats is required")

        if price is None:
            raise NotGivenError(status_code=400, error_code="SHOW007", error_message="price is required")

        timing_value = datetime.strptime(str(timings), '%Y-%m-%dT%H:%M')
        ti = str(timing_value)
        ven = Venue.query.filter_by(venue_id=venue_id).first()
        show = ven.show
        sname = []
        tim = []
        for s in show:
            sname.append(s.show_name)
            tim.append(s.timing.strftime('%Y-%m-%d %H:%M:%S'))
        if sname != [] and tim != []:
            if show_name in sname and ti not in tim:
                s = Show(show_name=show_name, rating=ratings, timing=timing_value, tags=tags, screenNumber=screenNumber, seats=seats, price=price)
                db.session.add(s)
                db.session.commit()
                s_id = s.show_id
                sc = ShowCreated(cshow_id=s_id,cvenue_id=venue_id)
                db.session.add(sc)
                db.session.commit()
                s={
                    "show_id": s.show_id,
                    "show_name": s.show_name,
                    "rating": s.rating,
                    "timings": s.timing.strftime('%d/%m/%Y %I:%M %p'),
                    "tags": s.tags,
                    "screen number": s.screenNumber,
                    "seats": s.seats,
                    "price": s.price,
                    "amount_recieved": s.amount_recieved
                    }
                return s, 201
            if show_name not in sname:
                s = Show(show_name=show_name, rating=ratings, timing=timing_value, tags=tags, screenNumber=screenNumber, seats=seats, price=price)
                db.session.add(s)
                db.session.commit()
                s_id = s.show_id
                sc = ShowCreated(cshow_id=s_id,cvenue_id=venue_id)
                db.session.add(sc)
                db.session.commit()
                s={
                    "show_id": s.show_id,
                    "show_name": s.show_name,
                    "rating": s.rating,
                    "timings": s.timing.strftime('%d/%m/%Y %I:%M %p'),
                    "tags": s.tags,
                    "screen number": s.screenNumber,
                    "seats": s.seats,
                    "price": s.price,
                    "amount_recieved": s.amount_recieved
                    }
                return s, 201
            else:
                raise NotGivenError(status_code=400, error_code="SHOW008", error_message="time already exist")
        else:
            s = Show(show_name=show_name, rating=ratings, timing=timing_value, tags=tags, screenNumber=screenNumber, seats=seats, price=price)
            db.session.add(s)
            db.session.commit()
            s_id = s.show_id
            sc = ShowCreated(cshow_id=s_id,cvenue_id=venue_id)
            db.session.add(sc)
            db.session.commit()
        s={
            "show_id": s.show_id,
            "show_name": s.show_name,
            "rating": s.rating,
            "timings": s.timing.strftime('%d/%m/%Y %I:%M %p'),
            "tags": s.tags,
            "screen number": s.screenNumber,
            "seats": s.seats,
            "price": s.price,
            "amount_recieved": s.amount_recieved
            }
        return s, 201
#----------------------------------------------------------------------------------------#
class AdminAPI(Resource):
    @marshal_with(admin_fields)
    def get(self,admin_id):
        admin=Admin.query.filter_by(admin_id=admin_id).first()
        if admin:
            return admin
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(admin_fields)
    def post(self):
        args = admin_parse.parse_args()
        admin_name=args.get("admin_name")
        mobile=args.get("mobile")
        pswd=args.get("password")

        

        if admin_name is None:
            raise NotGivenError(status_code=400, error_code="ADMIN001", error_message="Admin_name is required")

        if mobile is None:
            raise NotGivenError(status_code=400, error_code="ADMIN002", error_message="Mobile Number is required")

        if pswd is None:
            raise NotGivenError(status_code=400, error_code="ADMIN003", error_message="Password is required")
        

        
        ad=Admin.query.filter(or_(Admin.admin_name==admin_name,Admin.mobile==mobile)).first()

        if ad:
            raise NotFoundError(status_code=409)

        
        else:
            ad=Admin(admin_name=admin_name,mobile=mobile,password=pswd)
            db.session.add(ad)
            db.session.commit()
            return ad, 200
#----------------------------------------------------------------------------------------#        
class UserAPI(Resource):

    @marshal_with(user_fields)
    def get(self,user_id):
        user=User.query.filter_by(id=user_id).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(user_fields)
    def put(self,user_id):
        args = user_parse.parse_args()
        user_name=args.get("user_name")
        mobile=args.get("mobile")
        pswd=args.get("password")
        city=args.get("city")

        users=User.query.filter(User.user_name==user_name,User.mobile==mobile).first()
        
        if user_name is None:
            raise NotGivenError(status_code=400, error_code="USER001", error_message="User_name is required")

        if mobile is None:
            raise NotGivenError(status_code=400, error_code="USER002", error_message="Mobile Number is required")

        if pswd is None:
            raise NotGivenError(status_code=400, error_code="USER003", error_message="Password is required")
        
        if users:
            raise NotGivenError(status_code=400, error_code="USER004", error_message="User_name or mobile already exist")
        
        us=User.query.filter_by(id=user_id).first()
        if us:
            us.user_name=user_name
            us.mobile=mobile
            us.password=pswd
            us.city=city
            db.session.commit()
            return us, 200
        
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(user_fields)
    def post(self):
        args = user_parse.parse_args()
        user_name=args.get("user_name")
        mobile=args.get("mobile")
        city=args.get("city")
        pswd=args.get("password")

        if user_name is None:
            raise NotGivenError(status_code=400, error_code="USER001", error_message="User_name is required")

        if mobile is None:
            raise NotGivenError(status_code=400, error_code="USER002", error_message="Mobile Number is required")

        if pswd is None:
            raise NotGivenError(status_code=400, error_code="USER003", error_message="Password is required")
        
        us=User.query.filter(or_(User.user_name==user_name,User.mobile==mobile)).first()
        if us:
            raise NotFoundError(status_code=409)

        
        else:
            us=User(user_name=user_name,mobile=mobile,city=city,password=pswd)
            db.session.add(us)
            db.session.commit()
            return us, 201
#----------------------------------------------------------------------------------------#
class ShowbookedAPI(Resource):

    def get(self,user_id,show_id):
        sb=ShowBooked.query.filter(ShowBooked.bshow_id==show_id,ShowBooked.buser_id==user_id).first()

        if sb:
            sbd={
            "sb_id": sb.sb_id,
            "seats_booked": sb.seats_booked,
            "showname": sb.showname,
            "showtime": sb.showtime.strftime('%d/%m/%Y %I:%M %p'),
            "venuename": sb.venuename,
            "venueplace": sb.venueplace,
            "venueloaction": sb.venuelocation,
            "Total_price": sb.Total_price,
            "bshow_id": sb.bshow_id,
            "buser_id": sb.buser_id
            }
            return sbd, 200
        else:
            raise NotFoundError(status_code=404)
        

    def post(self,show_id,user_id,venue_id):
        args=showbook_parse.parse_args()
        Num= args.get('NOS')
       
        if Num is None:
            raise NotGivenError(status_code=400, error_code="SHOWBOOKED001", error_message="Number of seats is required")

        show=Show.query.filter_by(show_id=show_id).first()
        if not show:
            raise NotFoundError(status_code=404)
        price=show.price
        Tprice=int(price)*int(Num)
        vn=Venue.query.filter_by(venue_id=venue_id).first()
        vname=vn.venue_name
        vplace=vn.place
        vlocation=vn.location
        s_name=show.show_name
        stime=show.timing
        sb=ShowBooked(seats_booked=int(Num),Total_price=int(Tprice),showname=s_name,showtime=stime,venuename=vname,venueplace=vplace,venuelocation=vlocation,bshow_id=show_id,buser_id=user_id)
        db.session.add(sb)
        

        if int(show.seats)< int(Num):
            raise NotGivenError(status_code=400, error_code="SHOWBOOKED002", error_message="That many seats are not available")
        
        if show.amount_recieved is None:
            show.amount_recieved=int(Tprice)
        else:
            show.amount_recieved+=int(Tprice)
        show.seats-=int(Num)
        db.session.commit()
        sbd={
            "sb_id": sb.sb_id,
            "seats_booked": sb.seats_booked,
            "showname": sb.showname,
            "showtime": sb.showtime.strftime('%d/%m/%Y %I:%M %p'),
            "venuename": sb.venuename,
            "venueplace": sb.venueplace,
            "venueloaction": sb.venuelocation,
            "Total_price": sb.Total_price,
            "bshow_id": sb.bshow_id,
            "buser_id": sb.buser_id
        }
        return sbd, 200
#----------------------------------------------------------------------------------------#
class RateAPI(Resource):

    @marshal_with(rate_fields)
    def post(self,user_id,show_id):

        args=rate_parse.parse_args()
        rate=int(args.get('rating'))
        review=args.get('review')
        if rate is None:
            raise NotGivenError(status_code=400, error_code="RATE001", error_message="Rating is required")
        if review is None:
            raise NotGivenError(status_code=400, error_code="RATE002", error_message="Review is required")
        
        rat=Rate.query.filter(Rate.ruser_id==user_id,Rate.rshow_id==show_id).first()
        if rat:
            raise NotGivenError(status_code=400, error_code="RATE003", error_message="your rating and review already exist for this show")
        else:
            sh=Show.query.filter_by(show_id=show_id).first()
            if sh:
                sn=sh.show_name
                shb=Rate(rating=rate,review=review,showname=sn,ruser_id=user_id,rshow_id=show_id)
                db.session.add(shb)
                sh.rating=(sh.rating+rate)//2
                db.session.commit()
                return shb, 200
            else:
                raise NotFoundError(status_code=404)

#----------------------------------------------------------------------------------------#

#--------------------------- Adding the resources to the API===========#
api.add_resource(AdminAPI, "/api/admin/<int:admin_id>", "/api/admin")
api.add_resource(UserAPI, "/api/user/<int:user_id>", "/api/user")
api.add_resource(VenueAPI, "/api/venue/<int:venue_id>", "/api/venue/create/<int:admin_id>")
api.add_resource(ShowAPI, "/api/show/create/<int:venue_id>","/api/show/<int:show_id>")
api.add_resource(ShowbookedAPI, "/api/showbook/<int:user_id>/<int:show_id>","/api/showbook/create/<int:user_id>/<int:venue_id>/<int:show_id>")
api.add_resource(RateAPI, "/api/rate/create/<int:user_id>/<int:show_id>")


#----------------------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True, port=8080)