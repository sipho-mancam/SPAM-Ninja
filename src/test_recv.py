from imaplib import IMAP4
import imaplib


with IMAP4("rbconsult.co.za") as imap:
    print(imap.noop())
    imap.debug = 4

    try:
        print(imap.login("webmaster@rbconsult.co.za", "Webmail@RBC2022"))
        print(imap.select())
        typ, data = imap.search(None, 'NEW') # get the recent messages.
        print("Data: ",data[0].split())
        for num in data[0].split():
            typ, data = imap.fetch(num, '(RFC822)')
            print("Message %s\n%s\n"%(num, str(data)))
            imap.store(num,'+FLAGS', '\\SPAM')
            # break
        # imap.expunge()
    except imap.error as e:
        print(e)