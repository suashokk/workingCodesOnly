if (isJournal) {
    log.info("Journal mail detected → sending raw EML as-is: {}", this.emlFile);

    javax.mail.Address[] rcpts = rawMsg.getAllRecipients();

    // Fallback 1: try "To" header manually
    if (rcpts == null || rcpts.length == 0) {
        try {
            String[] toHdr = rawMsg.getHeader("To");
            if (toHdr != null && toHdr.length > 0) {
                rcpts = javax.mail.internet.InternetAddress.parse(toHdr[0], false);
            }
        } catch (Exception ignore) {
        }
    }

    // Fallback 2: use a configured journal recipient (if nothing else found)
    if (rcpts == null || rcpts.length == 0) {
        String journalTo = this.propertiesMap.get("journalToMailId"); // add this key in config
        if (journalTo == null || journalTo.isEmpty()) {
            journalTo = this.propertiesMap.get("PostfixToMailid");   // or reuse existing key
        }
        if (journalTo != null && !journalTo.isEmpty()) {
            rcpts = javax.mail.internet.InternetAddress.parse(journalTo, false);
            log.info("No recipients in journal mail headers, using fallback: {}", journalTo);
        }
    }

    if (rcpts == null || rcpts.length == 0) {
        log.warn("Journal mail {} has NO recipients even after fallback – skipping", this.emlFile);
        return;
    }

    // IMPORTANT: do NOT change mail.smtp.from, do NOT build a new message
    rawMsg.saveChanges();
    Transport.send(rawMsg, rcpts);

    log.info("Journal mail {} sent successfully", this.emlFile);
    return; // do not run BBG logic below
}
