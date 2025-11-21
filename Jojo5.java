private MimeMessage extractOneLevel(MimeMessage msg) {
    try {
        Object content = msg.getContent();

        if (!(content instanceof Multipart)) {
            return msg;
        }

        Multipart mp = (Multipart) content;

        for (int i = 0; i < mp.getCount(); i++) {
            BodyPart part = mp.getBodyPart(i);

            // Case 1: message/rfc822
            if (part.isMimeType("message/rfc822")) {
                return createMessageFromPart(part);
            }

            // Case 2: .eml file
            String fileName = part.getFileName();
            if (fileName != null && fileName.toLowerCase().endsWith(".eml")) {
                return createMessageFromPart(part);
            }
        }

    } catch (Exception e) {
        e.printStackTrace();
    }

    return msg;
}

private MimeMessage createMessageFromPart(BodyPart part) throws Exception {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    part.writeTo(baos); // safe copy
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
    return new MimeMessage(mailSession, bais);
}
