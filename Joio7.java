private void processJournalEmlFile(File emlFile) throws Exception {

    // Load outer message (journal / NDR / wrapper)
    byte[] data = Files.readAllBytes(emlFile.toPath());
    MimeMessage outer = new MimeMessage(mailSession, new ByteArrayInputStream(data));

    // Unwrap all nested levels – final business/original mail
    MimeMessage original = unwrapDeep(outer);

    MimeMessage out = new MimeMessage(mailSession);

    // FROM
    Address[] from = original.getFrom();
    if (from != null && from.length > 0) {
        out.addFrom(from);
    }

    // TO / CC / BCC using safe inner→outer fallback
    Address[] to  = getSafeRecipients(original, outer, Message.RecipientType.TO);
    Address[] cc  = getSafeRecipients(original, outer, Message.RecipientType.CC);
    Address[] bcc = getSafeRecipients(original, outer, Message.RecipientType.BCC);

    // Optional: last fallback to a configured address if still no TO
    if ((to == null || to.length == 0)) {
        String fallbackTo = properties.getProperty("PostfixToMailid"); // or whatever key you use
        if (fallbackTo != null && !fallbackTo.isEmpty()) {
            to = InternetAddress.parse(fallbackTo, false);
        }
    }

    if (to != null && to.length > 0) {
        out.setRecipients(Message.RecipientType.TO, to);
    }
    if (cc != null && cc.length > 0) {
        out.setRecipients(Message.RecipientType.CC, cc);
    }
    if (bcc != null && bcc.length > 0) {
        out.setRecipients(Message.RecipientType.BCC, bcc);
    }

    // Final guard – avoid "No recipient addresses"
    if (out.getAllRecipients() == null || out.getAllRecipients().length == 0) {
        throw new MessagingException("No recipients found in inner/outer/fallback for " + emlFile.getName());
    }

    // SUBJECT
    out.setSubject(original.getSubject(), "UTF-8");

    // CONTENT (body + attachments)
    Object content = original.getContent();
    out.setContent(content, original.getContentType());
    out.saveChanges();

    // send
    Transport.send(out);
}
