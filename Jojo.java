import javax.mail.Address;
import javax.mail.BodyPart;
import javax.mail.Message;
import javax.mail.Multipart;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

import com.sun.mail.util.SharedFileInputStream;

import java.io.File;
import java.io.InputStream;
// adjust package / class as per your project
public class WorkerThread implements Runnable {

    private final Session mailSession;
    private final String emlFilePath;

    public WorkerThread(Session mailSession, String emlFilePath) {
        this.mailSession = mailSession;
        this.emlFilePath = emlFilePath;
    }

    /** Check if the message is a journal report (FROM journaling mailbox) */
    private boolean isJournalMail(MimeMessage msg) throws Exception {
        Address[] fromArr = msg.getFrom();
        if (fromArr == null || fromArr.length == 0) {
            return false;
        }
        String from = ((InternetAddress) fromArr[0]).getAddress();
        // 👉 put your real journaling mailbox here
        return from != null &&
               from.equalsIgnoreCase("journal@yourdomain.com");
    }


/** Handles ONLY journaled .eml files */
    private void processJournalEmlFile(File emlFile) throws Exception {

        try (InputStream source = new SharedFileInputStream(emlFile)) {

            // outer = journal report
            MimeMessage journalMsg = new MimeMessage(mailSession, source);

            // safety: if not actually journal, just return
            if (!isJournalMail(journalMsg)) {
                return;
            }

            // inner = original mail (From/To should come from this)
            MimeMessage original = extractOriginalFromJournal(journalMsg);

            // --- Create outgoing message with SAME From/To/Cc/Bcc as original ---

            MimeMessage out = new MimeMessage(mailSession);

            // FROM
            Address[] from = original.getFrom();
            if (from != null && from.length > 0) {
                out.addFrom(from);
            }

            // TO / CC / BCC
            Address[] to  = original.getRecipients(Message.RecipientType.TO);
            Address[] cc  = original.getRecipients(Message.RecipientType.CC);
            Address[] bcc = original.getRecipients(Message.RecipientType.BCC);

            if (to  != null) out.setRecipients(Message.RecipientType.TO,  to);
            if (cc  != null) out.setRecipients(Message.RecipientType.CC,  cc);
            if (bcc != null) out.setRecipients(Message.RecipientType.BCC, bcc);

            // SUBJECT
            out.setSubject(original.getSubject(), "UTF-8");

            // BODY + ATTACHMENTS (copy as-is)
            Object content = original.getContent();
            String contentType = original.getContentType();
            out.setContent(content, contentType);

            out.saveChanges();

            // 👉 Here you send or pass to your existing logic
            Transport.send(out);
        }
    }

/** Unwrap original email from journal report */
    private MimeMessage extractOriginalFromJournal(MimeMessage msg) {
        try {
            Object content = msg.getContent();

            if (!(content instanceof Multipart)) {
                return msg; // not multipart => not journal
            }

            Multipart mp = (Multipart) content;

            for (int i = 0; i < mp.getCount(); i++) {
                BodyPart part = mp.getBodyPart(i);

                // Case 1: embedded original message as message/rfc822
                if (part.isMimeType("message/rfc822")) {
                    return new MimeMessage(mailSession, part.getInputStream());
                    // or msg.getSession() if you prefer
                }

                // Case 2: attached .eml file
                String fileName = part.getFileName();
                if (fileName != null &&
                        fileName.toLowerCase().endsWith(".eml")) {
                    return new MimeMessage(mailSession, part.getInputStream());
                }
            }
        } catch (Exception e) {
            e.printStackTrace();  // replace with logger
        }

        // fallback: if nothing found, just return outer message
        return msg;
    }

@Override
    public void run() {
        try {
            File emlFile = new File(emlFilePath);

            try (InputStream source = new SharedFileInputStream(emlFile)) {
                MimeMessage msg = new MimeMessage(mailSession, source);

                if (isJournalMail(msg)) {
                    // ➜ JOURNALED FLOW
                    processJournalEmlFile(emlFile);
                } else {
                    // ➜ NORMAL FLOW (your existing code)
                    processNormalEmlFile(emlFile);  // your old method
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
