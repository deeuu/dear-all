'''
Based on:
https://erikreed.net/batch-emailing-a-csv-file-of-data-using-python-and-smtp/
'''
import json
import re
import smtplib
import csv
from email.mime.text import MIMEText
import sys
import getopt
import time
import datetime


def wait_until_tomorrow():
    """
    Wait to tommorow 00:00 am
    http://code.activestate.com/recipes/577183-wait-to-tomorrow/
    """

    tomorrow = datetime.datetime.replace(datetime.datetime.now() +
                                         datetime.timedelta(days=1),
                                         hour=0,
                                         minute=0,
                                         second=0)
    delta = tomorrow - datetime.datetime.now()
    time.sleep(delta.seconds)


def valid_email(email):
    if re.match(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email
    ):
        return True
    return False


def update_emailed_list(address, state_filename):
    with open(state_filename, "a+") as f:
        addresses = csv.reader(f)

        addresses = [_[0] for _ in addresses]

        if address not in addresses:
            csv.writer(f).writerow([address])


def have_already_emailed(address, state_filename):

    with open(state_filename, "a+") as f:

        addresses = csv.reader(f)

        addresses = [_[0] for _ in addresses]

        if address in addresses:
            have_emailed = True
        else:
            have_emailed = False

    return have_emailed


def send_mail(msg, configuration):

    if not have_already_emailed(msg['To'], configuration['state_filename']):

        server = smtplib.SMTP(configuration['smtp_server'])
        server.starttls()
        server.login(configuration['smtp_user'],
                     configuration['smtp_pass'])

        to = msg['To']
        if 'CC' in msg:
            to = [to, msg['CC']]

        server.sendmail(configuration['from_address'],
                        to,
                        msg.as_string())

        server.quit()

        print('Email sent to {}').format(msg['To'])

        update_emailed_list(msg['To'], configuration['state_filename'])

        time.sleep(configuration['email_interval_in_seconds'])

        return 1

    else:
        print(
            ('Email not sent. You have already emailed {}').format(msg['To'])
        )

        return 0


def first_word_stripper(name):
    return name.strip().split(' ')[0]


def formatter(name, msg):
    return 'Dear {0},\n\n{1}'.format(name, msg)


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hi")
    except getopt.GetoptError:
        print('Usage: python emailer.py -i <input-configuration-file>')
        sys.exit(2)
    if not args:
        print('Please provide a configuration file')
        sys.exit(2)

    with open(args[0]) as f:
        configuration = json.load(f)

    with open(configuration['message_filename']) as f:
        message = f.read()

    counter = 0

    with open(configuration['csv_filename']) as f:

        reader = csv.reader(f)

        for row in reader:

            if (counter == configuration['max_emails_to_send_per_day']):

                print("""
                      Reached maximum number of emails to send.
                      I will continue tomorrow.
                      """
                      )

                counter = 0
                wait_until_tomorrow()

            email = first_word_stripper(row[configuration['to_col_index']])

            if valid_email(email):

                if configuration['name_col_index']:

                    name = first_word_stripper(
                        row[configuration['name_col_index']]
                    )

                    msg = MIMEText(formatter(name, message))
                else:
                    msg = MIMEText(message)

                # Compile email
                msg['To'] = email
                msg['From'] = configuration['from_address']

                try:
                    cc_email = first_word_stripper(
                        row[configuration['cc_col_index']]
                    )

                    if valid_email(cc_email):
                        msg['CC'] = cc_email
                except:
                    pass

                msg['Subject'] = configuration['subject']

                counter += send_mail(msg, configuration)


if __name__ == '__main__':

    main(sys.argv[1:])
