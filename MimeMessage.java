InputStream source = new SharedFileInputStream(emlFile);
MimeMessage outer = new MimeMessage(session, source);

// Step 1: Detect journal mail
String from = "";
if (outer.getFrom() != null && outer.getFrom().length > 0) {
    from = ((InternetAddress) outer.getFrom()[0]).getAddress();
}
boolean isJournaled = from.equalsIgnoreCase("journal@domain.com");

// Step 2: Fix structure
MimeMessage effectiveMessage = isJournaled
        ? extractOriginalFromJournal(outer)
        : outer;

// Step 3: Use your existing code AS-IS
MyInboundMessage messageSecond =
        new MyInboundMessage(new MyMimeMessage(session, effectiveMessage));

// ➜ Everything else in your current code remains unchanged

private MimeMessage extractOriginalFromJournal(MimeMessage msg) {
    try {
        Object content = msg.getContent();

        if (!(content instanceof Multipart)) {
            return msg; // not journal
        }

        Multipart mp = (Multipart) content;

        for (int i = 0; i < mp.getCount(); i++) {
            BodyPart part = mp.getBodyPart(i);

            // Case 1: journaled mail contains "message/rfc822"
            if (part.isMimeType("message/rfc822")) {
                Object pc = part.getContent();

                if (pc instanceof MimeMessage) {
                    return (MimeMessage) pc;
                }
                if (pc instanceof Message) {
                    return new MimeMessage((Message) pc);
                }
            }

            // Case 2: attached inner .eml file
            String fileName = part.getFileName();
            if (fileName != null && fileName.toLowerCase().endsWith(".eml")) {
                return new MimeMessage(session, part.getInputStream());
            }
        }

    } catch (Exception e) {
        e.printStackTrace();
    }

    return msg; // fallback
}
