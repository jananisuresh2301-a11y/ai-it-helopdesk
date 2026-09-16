# Email Issues

## Not Receiving Emails
Symptoms: Emails sent to the user never arrive, no bounce message to sender.

Steps:
1. Check the Junk/Spam folder.
2. Check mailbox storage quota — a full mailbox silently rejects new mail.
3. Verify mail forwarding/rules aren't redirecting messages elsewhere.
4. Ask the sender to check for a bounce-back or delivery delay notice.
5. Check the mail server's message trace/logs for the specific message.

## Emails Stuck in Outbox
Symptoms: Sent emails sit in Outbox and never send.

Steps:
1. Check internet connectivity.
2. Check for oversized attachments exceeding server limits.
3. Restart the email client.
4. Check if the account needs re-authentication (expired token/password).

## Can't Log Into Webmail
Symptoms: "Incorrect password" despite correct credentials, or repeated MFA
prompts.

Steps:
1. Confirm account isn't locked (see password_reset.md).
2. Clear browser cache/cookies or try an incognito window.
3. Check for a service-wide outage on the provider's status page.
