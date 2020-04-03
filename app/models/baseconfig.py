from app import db

# 状态表
#登录协议
class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    attribute = db.Column(db.String(64), index=True)
    
    requirements = db.relationship('IssueRequirement', back_populates='status')
    bugs = db.relationship('IssueBug', back_populates='status')
    tasks = db.relationship('IssueTask', back_populates='status')
    baselines = db.relationship('Baseline', back_populates='status')
    
    def __repr__(self):
        return '<Status.name %r>' % self.name



# 标签: 1.功能完善 2.待确认 3.新增需求 4.解释性问题 5.重复问题 6.需求变更
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False,unique=True, index=True)
    attribute = db.Column(db.String(64), index=True)

    requirements = db.relationship('IssueRequirement', back_populates='tag')
    bugs = db.relationship('IssueBug', back_populates='tag')