from marshmallow import Schema, fields, validates_schema

class LoginSchema(Schema):
    email_address = fields.Email(required=True)
    password = fields.Str(load_only=True)  


login_schema = LoginSchema()