import mailbox
import re
import pandas as pd

mails = mailbox.mbox('Sent.mbox')
reply_chain_delim = re.compile('On [Sun |Mon |Tue |Wed |Thu |Fri |Sat |Jan |Feb |Mar |Apr |May |Jun |Jul |Aug |Sep |Oct |Nov |Dec ]|---------- Forwarded message ----------|[^\s-]{50,}')
# bullshit = re.compile('[^\s-]{50,}')
df = pd.DataFrame(columns=['date', 'recipient', 'text', 'subject'])

i = 0
for mail in mails:
    sender = mail['from']
    if sender is not None:
        if "Alex Risman" in sender:
            curr_date = mail['date']
            recip = mail['to']
            subj = mail['subject']
            found_text_ind = False
            payload = mail
            while not found_text_ind:
                new_payload = payload.get_payload()
                if type(new_payload)==str:
                    new_payload = reply_chain_delim.split(new_payload)[0]
                    text = new_payload
                    found_text_ind = True
                else:
                    payload = new_payload[0]
            # if bullshit.match(text) is None:
            df.loc[i] = [curr_date, recip, text, subj]
            i += 1

df.to_csv("extracted_emails.csv")