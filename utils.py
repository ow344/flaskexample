from models import Changelog, db

class ChangeService:
    def __init__(self, object):
        self.object = object
    def __enter__(self):
        self.current_dict = self.object.__dict__.copy()
    def __exit__(self, exc_type, exc_value, traceback):
        new_dict = self.object.__dict__
        changes = self.compare(self.current_dict, new_dict)
        if changes:
            for change in changes:
                self.record_change(
                    user_id=4,
                    object_type=self.object.__class__.__name__,
                    object_id=self.object.id,
                    attribute_changed=change['attribute_changed'],
                    old_value=change['old_value'],
                    new_value=change['new_value']
                )

    def compare(self, current_dict, new_dict):
        changes = []
        for key in current_dict:
            if key[0] != '_':
                if current_dict[key] != new_dict[key]:
                    changes.append({
                        'attribute_changed': key,
                        'old_value': current_dict[key],
                        'new_value': new_dict[key]
                    })
        return changes

    def record_change(self, user_id, object_type, object_id, attribute_changed, old_value, new_value):
        change = {
            'user_id': user_id,
            'object_type': object_type,
            'object_id': object_id,
            'attribute_changed': attribute_changed,
            'old_value': old_value,
            'new_value': new_value
        }
        change = Changelog(**change)
        print(change)
        db.session.add(change)
        db.session.commit()

    # def go(self):
    #     user_id = input('User ID: ')
    #     object_type = input('Object type: ')
    #     object_id = input('Object ID: ')
    #     attribute_changed = input('Attribute changed: ')
    #     old_value = input('Old value: ')
    #     new_value = input('New value: ')
    #     self.record_change(user_id, object_type, object_id, attribute_changed, old_value, new_value)

    
 

    # def get_all(self):
    #     return Changelog.query.all()


    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=lambda: current_user.id if current_user.is_authenticated else None)
    # user = db.relationship('User', backref='changelog', lazy='select')
    # datetime = db.Column(db.DateTime, default=datetime.utcnow)

    # object_type = db.Column(db.String(50))  # 'User' or 'School'
    # object_id = db.Column(db.Integer)
    # attribute_changed = db.Column(db.String(50))
    # old_value = db.Column(db.String(100))
    # new_value = db.Column(db.String(100))

    # def __repr__(self):
    #     the_class = globals().get(self.object_type)
    #     item  = db.session.get(the_class, self.object_id)
    #     return f'{item}'

