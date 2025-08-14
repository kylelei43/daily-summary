import imaplib
import email
from email.header import decode_header
from typing import List, Tuple


def fetch_unread(
    host: str,
    username: str,
    password: str,
    *,
    mailbox: str = "INBOX",
    mark_as_read: bool = False,
    exclude_promotions: bool = False,
) -> List[Tuple[str, str]]:
    """Fetch unread email messages from an IMAP server.

    Parameters
    ----------
    host:
        IMAP server hostname.
    username:
        Account username.
    password:
        Account password.
    mailbox:
        Mailbox to check. Defaults to ``"INBOX"``.
    mark_as_read:
        If ``True`` the messages will be marked as read after fetching.
    exclude_promotions:
        If ``True`` and the server is Gmail, messages categorized as
        Promotions will be skipped using the ``X-GM-RAW`` search modifier.

    Returns
    -------
    list[tuple[str, str]]
        A list of ``(subject, snippet)`` pairs for each unread message.
    """

    connection = imaplib.IMAP4_SSL(host)
    try:
        connection.login(username, password)
        connection.select(mailbox)

        if exclude_promotions:
            status, data = connection.search(
                None, "X-GM-RAW", "category:primary", "UNSEEN"
            )
        else:
            status, data = connection.search(None, "UNSEEN")
        if status != "OK":
            return []

        messages: List[Tuple[str, str]] = []
        for num in data[0].split():
            status, msg_data = connection.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Decode the subject if needed
            subject, encoding = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="replace")

            snippet = _extract_snippet(msg)
            messages.append((subject, snippet))

            if mark_as_read:
                connection.store(num, "+FLAGS", "\\Seen")

        return messages
    finally:
        try:
            connection.close()
        finally:
            connection.logout()


def _extract_snippet(msg: email.message.Message) -> str:
    """Return a short text snippet from an email message."""
    text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
                break
    else:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
        elif isinstance(payload, str):
            text = payload

    snippet = " ".join(text.strip().split())
    return snippet[:100]
