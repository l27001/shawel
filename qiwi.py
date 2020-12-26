from pyqiwip2p import QiwiP2P
from pyqiwip2p.types import QiwiCustomer, QiwiDatetime
import os
from random import randint
dir_path = os.path.dirname(os.path.realpath(__file__))
qkey = open(f"{dir_path}/key","r").readline().replace("\n","")
p2p = QiwiP2P(auth_key=qkey)

def create_pay(amount, comment):
    billid = randint(100000,99999999)
    bill = p2p.bill(bill_id=billid ,amount=amount, lifetime=1440, comment=f"{comment} Оплата #{billid}")
    return {"id":bill.bill_id,"comment":bill.comment,"amount":bill.amount,"url":bill.pay_url}

def check_pay(bill_id):
    bill = p2p.check(bill_id=bill_id)
    return {"amount":bill.amount,"status":bill.status,"comment":bill.comment}

def revoke_pay(bill_id):
    p2p.reject(bill_id=bill_id)
