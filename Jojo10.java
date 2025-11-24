if (isJournal) {
    SMTPcsurvSAASImplementor.log.info("Journal mail detected → {}", this.emlFile);

    String journalRcpt = this.propertiesMap.get("PostfixToMailid");
    if (journalRcpt == null || journalRcpt.isEmpty()) {
        SMTPcsurvSAASImplementor.log.error("PostfixToMailid not configured – cannot send journal mail {}", this.emlFile);
        return;
    }

    javax.mail.Address[] rcpts =
            javax.mail.internet.InternetAddress.parse(journalRcpt, false);

    SMTPcsurvSAASImplementor.log.info(
            "Sending journal EML as-is. Envelope RCPT = {}, Header TO = {}",
            journalRcpt,
            java.util.Arrays.toString(rawMsg.getRecipients(javax.mail.Message.RecipientType.TO))
    );

    rawMsg.saveChanges();
    javax.mail.Transport.send(rawMsg, rcpts);

    SMTPcsurvSAASImplementor.passedList.add(this.emlFile);
    SMTPcsurvSAASImplementor.counts_successCount.incrementAndGet();

    return;     // ★ IMPORTANT: STOP here
}
