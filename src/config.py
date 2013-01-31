import subprocess

percentage_threshold = 1
sleep_time = 120 # in seconds
callback = lambda a, b, c: a
#email_address $= fixme@fixme.fixme
#callback = send_email

def send_email(title, msg, raw_data):
    if send_email.old_raw_data == raw_data:
        print "already sent"
        return
    send_email.old_raw_data = raw_data
    print "sending email"
    subprocess.call('echo "%s" | mutt -s "%s" "%s"' % (msg, title, email_address),
                    shell=True)
send_email.old_raw_data = ""

