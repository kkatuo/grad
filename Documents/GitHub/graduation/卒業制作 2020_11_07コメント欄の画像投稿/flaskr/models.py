# models.py
from re import M
from sqlalchemy import and_, or_
from sqlalchemy import desc
from operator import or_
from flask.globals import session
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import asc
from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime, timedelta
from uuid import uuid4

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(
        db.String(128),
        default=generate_password_hash('snsflaskapp')
    )
    picture_path = db.Column(db.Text)
    taglist = db.Column(db.String(64), index=True)
    # 有効か無効かのフラグ
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    def select_all():
        return db.session.query(User).all()

    def save_profile(id,user_name,imagename,taglist,password):
        query = db.session.query(User).filter(User.id==id).first()
        print(query.username)
        query.username = user_name
        query.picture_path = imagename
        query.taglist = taglist
        query.password = generate_password_hash(password)
        query.is_active = True

    def select_picture_path(id):
        return db.session.query(User.picture_path).filter_by(id=id).all()


    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)
    
    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True




# パスワードリセット時に利用する
class PasswordResetToken(db.Model):

    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default=str(uuid4)
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, user):
        # パスワード設定用のURLを生成
        token = str(uuid4())
        new_token = cls(
            token,
            user.id,
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        return record.user_id
        

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()


class Planning_data(db.Model):

    __tablename__ = 'planning_data'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    planner = db.Column(db.String(64), index=True)
    contents = db.Column(db.String(64), index=True)
    application = db.Column(db.String(64), index=True)
    image = db.Column(db.String(64), index=True)
    taglist = db.Column(db.String(64), index=True)
    flag = db.Column(db.String(1), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    #flag情報
    #[1]の時は募集中の企画
    #[2]の時は募集一時停止の企画
    #[3]の時はプロジェクト終了
    #[4]の時は企画者の評価の終了


    def __init__(self,title,planner,contents,application,image,taglist,flag):
        self.title = title
        self.contents = contents
        self.planner = planner
        self.application = application
        self.image = image
        self.taglist = taglist
        self.flag = flag

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def select_id_by_title(title):
        return db.session.query(Planning_data).filter_by(title=title).first()

    def select_create_at(title):
        return db.session.query(Planning_data).filter_by(title=title).\
            order_by(desc(Planning_data.create_at)).\
                first()
    #企画の作成
    def create_new_plan(self):
        db.session.add(self)

    def select_all():
        return db.session.query(Planning_data).all()

    def select_home():
        return db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.create_at,User.username).\
            join(User, Planning_data.planner==User.id).\
                filter(Planning_data.flag=='0').\
                    order_by(desc(Planning_data.create_at)).\
                        limit(6).all()

    def plan_status(id):
        return db.session.query(Planning_data.flag).\
            filter(Planning_data.id==id).first()

    def end_select_home():
        return db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.create_at,User.username).\
            join(User, Planning_data.planner==User.id).\
                filter(or_(Planning_data.flag=='3',Planning_data.flag=='4')).\
                    order_by(desc(Planning_data.create_at)).\
                        limit(6).all()

    def select_search(tag):
        tag = '%'+tag+'%'
        list = db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.create_at,User.username).\
            join(User, Planning_data.planner==User.id).\
                filter(or_(Planning_data.title.like(tag), Planning_data.taglist.like(tag))).\
                    filter(Planning_data.flag == '0').\
                    order_by(desc(Planning_data.create_at))
        return list

    def id_serect(ID):
        return db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.taglist,Planning_data.create_at,User.username,Planning_data.flag).\
            join(User, Planning_data.planner==User.id).\
                filter(Planning_data.id == ID).\
                    limit(1).all()

    def my_planning_list(ID):
        return db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.create_at,User.username).\
            join(User, Planning_data.planner==User.id).\
                filter(Planning_data.planner==ID).\
                    order_by(desc(Planning_data.create_at)).\
                        all()

    def participation_list(ID):
        return db.session.query(Planning_data.id,Planning_data.title,Planning_data.planner,Planning_data.contents,Planning_data.image,Planning_data.create_at,User.username).\
            join(User, Planning_data.planner==User.id).\
                join(Planning_menber, Planning_data.id==Planning_menber.plan_id).\
                filter(Planning_menber.member_id ==ID,Planning_menber.flag=='1').\
                    order_by(desc(Planning_data.create_at)).\
                        all()

    def delete_plan(ID):
        plan = db.session.query(Planning_data).filter(Planning_data.id == ID)
        plan_data = plan.one()
        db.session.delete(plan_data)
        db.session.commit()

    def update_plan(ID,title,contents,application,taglist):
        query = db.session.query(Planning_data).filter(Planning_data.id == ID).first()
        print(query)
        query.title = title
        query.contents = contents
        query.application = application
        query.taglist = taglist

    #企画のフラグ変更
    def change_flag(ID,flag):
        query = db.session.query(Planning_data).filter(Planning_data.id == ID).first()
        query.flag = flag

    def print_data(self):
        print(self)

    def select_planner(ID):
        return db.session.query(Planning_data.planner,Planning_data.flag).\
            filter(Planning_data.id == ID).all()
    
class Planning_menber(db.Model):

    __tablename__ = 'planning_menber'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    member_id = db.Column(db.String(64), index=True)
    flag = db.Column(db.String(1), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,plan_id,member_id,flag):
        self.plan_id = plan_id
        self.member_id = member_id
        self.flag = flag
        
    def menber_add(self):
        db.session.add(self)

    #メンバーのフラグ変更
    def menber_flag(ID,flag):
        menber = db.session.query(Planning_menber).\
            filter(Planning_menber.id==ID).first()
        print(menber)
        menber.flag = flag

    #メンバーのフラグ変更(更新)
    def menber_flags(plan_id,user_id,flag):
        menber = db.session.query(Planning_menber).\
            filter(Planning_menber.member_id==user_id,Planning_menber.plan_id==plan_id).\
                first()
        print(menber)
        menber.flag = flag

    #企画メンバーのステータス確認
    def menber_status(plan_id,user_id):
        return db.session.query(Planning_menber.flag).\
            filter(Planning_menber.plan_id==plan_id,Planning_menber.member_id==user_id).\
                first()


    #企画メンバーかどうかのチェック
    def check_menber(ID,user):
        return db.session.query(Planning_menber).\
            join(Planning_data,Planning_menber.plan_id==Planning_data.id).\
                filter(Planning_menber.member_id==user).\
                    count()

    #企画メンバーの検索
    def plan_member(ID):
        return db.session.query(Planning_menber.member_id,User.username).\
            join(User,Planning_menber.member_id==User.id).\
                filter(Planning_menber.plan_id==ID).\
                    filter(or_(Planning_menber.flag=='1',Planning_menber.flag=='3')).\
                        all()
      
class Comment_data(db.Model):

    __tablename__ = 'comment_data'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    user_id = db.Column(db.String(64), index=True)
    comment = db.Column(db.String(64), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,plan_id,user_id,comment):
        self.plan_id = plan_id
        self.user_id = user_id
        self.comment = comment

    @classmethod

    def print_data(self):
        print(self)


    def select_comment_date(ID):
        return db.session.query(User.username,User.picture_path,Comment_data.comment,Comment_data.create_at).\
            join(User, Comment_data.user_id==User.id).\
                filter(Comment_data.plan_id==ID).\
                    all()

    def create_new_comment(self):
        db.session.add(self)

class Message_data(db.Model):

    __tablename__ = 'message_data'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    recipient_name_id = db.Column(db.String(64), index=True)
    sender_name_id = db.Column(db.String(64), index=True)
    message = db.Column(db.String(64), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,plan_id,recipient_name_id,sender_name_id,message):
        self.plan_id = plan_id
        self.recipient_name_id = recipient_name_id
        self.sender_name_id = sender_name_id
        self.message = message

    def create_new_message(self):
        db.session.add(self)

    def select_recipient_message(id):
        return db.session.query(Planning_data.title,Message_data.id,Message_data.sender_name_id,User.username,Message_data.message,Message_data.create_at).\
            join(Planning_data,Message_data.plan_id==Planning_data.id).\
                join(User,Message_data.sender_name_id==User.id).\
                    filter(Message_data.recipient_name_id==id).\
                        order_by(desc(Message_data.create_at)).\
                            all()

    def details_message(id):
        return db.session.query(Planning_data.title,Message_data.id,Message_data.sender_name_id,User.username,Message_data.message,Message_data.create_at,Planning_menber.flag).\
            join(Planning_data,Message_data.plan_id==Planning_data.id).\
                join(User,Message_data.sender_name_id==User.id).\
                    join(Planning_menber,Message_data.plan_id==Planning_menber.plan_id).\
                        filter(Message_data.id==id).\
                            order_by(desc(Planning_menber.update_at)).\
                                all()

    def application_confirmation(ID,user_id):
        return db.session.query(Message_data).\
            filter(Message_data.plan_id==ID,Message_data.sender_name_id==user_id).\
                count()
  


class Planning_chat(db.Model):

    __tablename__ = 'planning_chat'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    member_id = db.Column(db.String(64), index=True)
    comment = db.Column(db.String(300), index=True)
    flag = db.Column(db.String(1), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)

    #flag
    #[0]文字のコメント
    #[1]画像
    #[2]動画
    #[3]音楽

    def __init__(self,plan_id,member_id,comment,flag):
        self.plan_id = plan_id
        self.member_id = member_id
        self.comment = comment
        self.flag = flag

    def select_plan_chat(ID):
        return db.session.query(Planning_chat.comment,Planning_chat.create_at,User.username,User.picture_path,Planning_chat.flag).\
            join(User,Planning_chat.member_id==User.id).\
                filter(Planning_chat.plan_id==ID).\
                    all()

    def add_plan_chat(self):
        db.session.add(self)


class Plan_evaluation(db.Model):

    __tablename__ = 'plan_evaluation'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    user_id = db.Column(db.String(64), index=True)
    evaluation = db.Column(db.String(300), index=True)
    comment = db.Column(db.String(300), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,plan_id,user_id,evaluation,comment):
        self.plan_id = plan_id
        self.user_id = user_id
        self.evaluation = evaluation
        self.comment = comment

    def evaluation_add(self):
        db.session.add(self)

class User_evaluation(db.Model):

    __tablename__ = 'user_evaluation'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(64), index=True)
    receiver = db.Column(db.String(64), index=True)
    sender = db.Column(db.String(64), index=True)
    evaluation = db.Column(db.String(300), index=True)
    comment = db.Column(db.String(300), index=True)
    create_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,plan_id,receiver,sender,evaluation,comment):
        self.plan_id = plan_id
        self.receiver = receiver
        self.sender = sender
        self.evaluation = evaluation
        self.comment = comment

    def user_evaluation_add(self):
        db.session.add(self)