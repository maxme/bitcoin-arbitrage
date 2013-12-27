import logging
from .observer import Observer
import config
import smtplib


def send_email(subject, message):
    _to = config.smtp_to
    _from = config.smtp_from
    mime_message = """From: Python Arbitrage Script <%(_from)s>
To: <%(_to)s>
Subject: %(subject)s

%(message)s
""" % locals()
    try:
        smtpObj = smtplib.SMTP(config.smtp_host)
        smtpObj.sendmail(_from, [_to], mime_message)
    except smtplib.SMTPException:
        logging.warn("Unable to send email")

class Emailer(Observer):
    def opportunity(self, tradechains):
        for chain in tradechains:
            if chain.profit > config.profit_thresh and chain.percentage > config.perc_thresh:
                send_email("Arbitrage Bot", str(chain))
