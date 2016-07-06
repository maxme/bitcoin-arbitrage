import logging
from .observer import Observer
import config
import smtplib
import traceback

def send_email(subject, msg):
    import smtplib

    message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s\r\n" % (config.EMAIL_HOST_USER, ", ".join(config.EMAIL_RECEIVER), subject, msg)
    try:
        smtpserver = smtplib.SMTP(config.EMAIL_HOST)
        smtpserver.set_debuglevel(0)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(config.EMAIL_HOST_USER, config.EMAIL_HOST_PASSWORD)
        smtpserver.sendmail(config.EMAIL_HOST_USER, config.EMAIL_RECEIVER, message)
        smtpserver.quit()  
        smtpserver.close() 
        logging.info("send mail success")      
    except:
        logging.error("send mail failed")
        traceback.print_exc()

class Emailer(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if profit > config.profit_thresh and perc > config.perc_thresh:
            message = """profit: %f CNY with volume: %f BTC
buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%
""" % (profit, volume, buyprice, kask, sellprice, kbid, perc)
            send_email("Arbitrage Bot", message)
