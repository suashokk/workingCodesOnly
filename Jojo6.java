private Address[] getSafeRecipients(MimeMessage inner, MimeMessage outer, Message.RecipientType type) throws Exception {
    Address[] innerR = inner.getRecipients(type);
    if (innerR != null && innerR.length > 0) return innerR;

    Address[] outerR = outer.getRecipients(type);
    if (outerR != null && outerR.length > 0) return outerR;

    return null;  // totally empty
}

Address[] to  = getSafeRecipients(effective, outer, Message.RecipientType.TO);
Address[] cc  = getSafeRecipients(effective, outer, Message.RecipientType.CC);
Address[] bcc = getSafeRecipients(effective, outer, Message.RecipientType.BCC);

if (to != null)  out.setRecipients(Message.RecipientType.TO,  to);
if (cc != null)  out.setRecipients(Message.RecipientType.CC,  cc);
if (bcc != null) out.setRecipients(Message.RecipientType.BCC, bcc);

if (out.getAllRecipients() == null || out.getAllRecipients().length == 0) {
    throw new MessagingException("No recipients found in both inner and outer message");
}
