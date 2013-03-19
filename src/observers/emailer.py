import logging
from observer import Observer
import config
import smtplib


class Emailer(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice,
                    kbid, perc, weighted_buyprice, weighted_sellprice):
        if profit > config.profit_thresh \
                and perc > config.perc_thresh:

            message = """From: From Python Arbitrage <%s>
To: <%s>
Subject: Bitcoin opportunity

profit: %f EUR with volume: %f BTC
buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%
""" % (config.smtp_from, config.smtp_to,
       profit, volume, buyprice, kask,
       sellprice, kbid, perc)

            try:
                smtpObj = smtplib.SMTP(config.smtp_host)
                smtpObj.sendmail(config.smtp_from, [config.smtp_to], message)
            except smtplib.SMTPException:
                logging.warn("Error: unable to send email")
