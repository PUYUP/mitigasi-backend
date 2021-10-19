import logging
import smtplib
import requests

from django.utils.translation import ugettext_lazy as _
from django.core.mail import BadHeaderError, EmailMultiAlternatives

# Celery config
from celery import shared_task


@shared_task
def send_securecode_email(data):
    logging.info(_("Send secure code email run"))

    to = data.get('email', None)
    passcode = data.get('passcode', None)
    project_name = data.get('project_name', _("Secure Code"))

    if to and passcode:
        subject = _("Secure Code")
        from_email = '%s <mitigasicom@gmail.com>' % project_name

        # Message
        text = _(
            "Don't share this Secure Code to everyone "
            "Including %(app_label)s team. Your Secure Code is: " +
            passcode
        ) % {'app_label': project_name}

        html = _(
            "Don't share this Secure Code to everyone "
            "Including %(app_label)s team.<br />"
            "Your Secure Code is: "
            "<strong>" + passcode + "</strong>"
            "<br /><br />"
            "Happy Coding, <br /> <strong>%(app_label)s</strong>"
        ) % {'app_label': project_name}

        if subject and from_email:
            try:
                msg = EmailMultiAlternatives(subject, text, from_email, [to])
                msg.attach_alternative(html, "text/html")
                msg.send()
                logging.info(_("SecureCode email success"))
            except smtplib.SMTPConnectError as e:
                logging.error('SMTPConnectError: %s' % e)
            except smtplib.SMTPAuthenticationError as e:
                logging.error('SMTPAuthenticationError: %s' % e)
            except smtplib.SMTPSenderRefused as e:
                logging.error('SMTPSenderRefused: %s' % e)
            except smtplib.SMTPRecipientsRefused as e:
                logging.error('SMTPRecipientsRefused: %s' % e)
            except smtplib.SMTPDataError as e:
                logging.error('SMTPDataError: %s' % e)
            except smtplib.SMTPException as e:
                logging.error('SMTPException: %s' % e)
            except BadHeaderError:
                logging.warning(_("Invalid header found"))
    else:
        logging.warning(
            _("Tried to send email to non-existing SecureCode Code"))


@shared_task
def send_securecode_msisdn(data):
    logging.info(_("Send secure code msisdn run"))

    msisdn = data.get('msisdn')
    passcode = data.get('passcode')
    project_name = data.get('project_name', _("Kode Keamanan"))
    message = '%s - Kode keamanan: %s. Jangan berikan ke siapapun.' % (
        project_name, passcode)

    # add 62
    if msisdn[0] == '0':
        msisdn = msisdn[1:]

    msisdn = '{}{}'.format('62', msisdn)
    api_key = 'BUtyekOTMA3woP09cbh6VnAkAI2fxmd8LTqaFheQgJ4='
    cliend_id = 'd973df88-5df9-4dc0-ba71-79939aae16e8'
    sender_id = 'TCASTSMS'
    url = 'https://api.tcastsms.net/api/v2/SendSMS'

    payload = {
        "ApiKey": api_key,
        "ClientId": cliend_id,
        "SenderId": sender_id,
        "Message": message,
        "MobileNumbers": msisdn,
        "Is_Unicode": False,
        "Is_Flash": False
    }

    r = requests.get(url, params=payload)
    logging.info(str(r.status_code))
