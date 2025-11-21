@Override
public void run() {
    try {
        File file = new File(emlFilePath);

        // Load outer message
        MimeMessage outer;
        try (InputStream source = new SharedFileInputStream(file)) {
            outer = new MimeMessage(mailSession, source);
        }

        // 🔥 STEP 1: Unwrap message recursively (journal, NDR, journal-in-journal)
        MimeMessage effective = unwrapDeep(outer);

        // 🔥 STEP 2: Now 'effective' is ALWAYS the true business/original message
        MimeMessage out = new MimeMessage(mailSession);

        // FROM
        Address[] from = effective.getFrom();
        if (from != null && from.length > 0) out.addFrom(from);

        // TO/CC/BCC
        out.setRecipients(Message.RecipientType.TO,
                effective.getRecipients(Message.RecipientType.TO));
        out.setRecipients(Message.RecipientType.CC,
                effective.getRecipients(Message.RecipientType.CC));
        out.setRecipients(Message.RecipientType.BCC,
                effective.getRecipients(Message.RecipientType.BCC));

        // SUBJECT
        out.setSubject(effective.getSubject(), "UTF-8");

        // CONTENT
        out.setContent(effective.getContent(), effective.getContentType());
        out.saveChanges();

        // SEND
        Transport.send(out);

        // success logging
        // passedList.add(emlFilePath);

    } catch (Exception e) {
        e.printStackTrace();
        // failedList.add(emlFilePath);
    }
}
