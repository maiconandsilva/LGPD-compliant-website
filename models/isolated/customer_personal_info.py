from flask.globals import session
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, FernetEngine
from sqlalchemy_utils import EncryptedType
from cryptography.fernet import Fernet

from app import db
from models.customers import Customers


def _get_customer_personal_info(model, ColumnType, engine, key):

    AnonymizedColumnsMixin = type('AnonymizedColumnsMixin', (), {
        column.name: db.Column(ColumnType(column.type, key, engine))
        for column in model.__table__.columns
        if column.info.get('anonymize')
    })

    class CustomerPersonalInfo(AnonymizedColumnsMixin, db.Model):
        """
        Class writes deleted customer's personal info encrypted
        on the isolated database
        """
        __bind_key__ = 'db_isolated'
        __tablename__ = 'customers_personal_info'

        customerid = db.Column('customerid', db.Integer, primary_key=True)

        @classmethod
        def from_customer(cls, customer):
            self = cls()
            for column in self.__table__.columns:
                setattr(self, column.name, getattr(customer, column.name))
            return self

    return CustomerPersonalInfo


def _get_key():
    session['cryptkey'] = session.get('cryptkey', Fernet.generate_key())
    return session['cryptkey']

CustomerPersonalInfo = _get_customer_personal_info(
    Customers, EncryptedType, FernetEngine, _get_key)