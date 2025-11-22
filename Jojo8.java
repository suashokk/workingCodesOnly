private Address[] getSafeFrom(MimeMessage inner,
                              MimeMessage outer) throws Exception {

    // 1) Prefer From on inner/original mail
    if (inner != null) {
        Address[] fromInner = inner.getFrom();
        if (fromInner != null && fromInner.length > 0) {
            return fromInner;
        }

        // Some system mails use "Sender" instead of "From"
        Address sender = inner.getSender();
        if (sender != null) {
            return new Address[]{ sender };
        }
    }

    // 2) Fall back to outer/journal/NDR From
    if (outer != null) {
        Address[] fromOuter = outer.getFrom();
        if (fromOuter != null && fromOuter.length > 0) {
            return fromOuter;
        }
    }

    // 3) Last fallback: config FromMailId (no-reply)
    String fromProp = properties.getProperty("FromMailId");
    if (fromProp != null && !fromProp.isEmpty()) {
        return InternetAddress.parse(fromProp, false);
    }

    // 4) Absolute last resort: null (caller will handle)
    return null;
}

// FROM with inner → outer → config fallback
Address[] from = getSafeFrom(original, outer);
if (from != null && from.length > 0) {
    out.addFrom(from);
}
