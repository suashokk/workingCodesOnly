private MimeMessage unwrapDeep(MimeMessage msg) {
    MimeMessage current = msg;

    try {
        for (int depth = 0; depth < 5; depth++) {
            MimeMessage next = extractOneLevel(current);
            if (next == current) break;
            current = next;
        }
    } catch (Exception e) {
        e.printStackTrace();
    }

    return current;
}

private MimeMessage extractOneLevel(MimeMessage msg) {
    try {
        Object content = msg.getContent();

        if (!(content instanceof Multipart)) return msg;

        Multipart mp = (Multipart) content;

        for (int i = 0; i < mp.getCount(); i++) {
            BodyPart part = mp.getBodyPart(i);

            if (part.isMimeType("message/rfc822")) {
                return new MimeMessage(mailSession, part.getInputStream());
            }

            String fileName = part.getFileName();
            if (fileName != null && fileName.toLowerCase().endsWith(".eml")) {
                return new MimeMessage(mailSession, part.getInputStream());
            }
        }
    } catch (Exception e) {
        e.printStackTrace();
    }

    return msg;
}
