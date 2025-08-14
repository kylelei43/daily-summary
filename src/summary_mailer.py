"""Utilities for building and sending daily summary emails."""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable, Tuple


def build_body(email_items: Iterable[str], weather: str, headlines: Iterable[str]) -> Tuple[str, str]:
    """Construct plain text and HTML bodies for the summary email.

    Parameters
    ----------
    email_items:
        Items to include in the email body. Each item should be a string.
    weather:
        A string representing current weather conditions.
    headlines:
        A list of news headlines to include.

    Returns
    -------
    tuple of str
        A ``(text, html)`` tuple containing the plain text and HTML versions
        of the email body.
    """

    items_list = "".join(f"- {item}\n" for item in email_items)
    headlines_list = "".join(f"- {h}\n" for h in headlines)

    text_body = (
        "Daily Summary\n\n"
        f"Weather:\n{weather}\n\n"
        f"Headlines:\n{headlines_list}\n"
        f"Items:\n{items_list}"
    )

    html_body = (
        "<html><body>"
        "<h1>Daily Summary</h1>"
        f"<h2>Weather</h2><p>{weather}</p>"
        "<h2>Headlines</h2><ul>"
        + "".join(f"<li>{h}</li>" for h in headlines)
        + "</ul>"
        "<h2>Items</h2><ul>"
        + "".join(f"<li>{item}</li>" for item in email_items)
        + "</ul>"
        "</body></html>"
    )

    return text_body, html_body


def send_summary_email(email_items: Iterable[str], weather: str, headlines: Iterable[str]) -> None:
    """Send the summary email using SMTP credentials from environment variables.

    Required environment variables:
    - ``SMTP_HOST``: SMTP server hostname.
    - ``SMTP_PORT``: SMTP server port.
    - ``SMTP_USER``: Username for authentication.
    - ``SMTP_PASSWORD``: Password for authentication.
    - ``EMAIL_FROM``: From address.
    - ``EMAIL_TO``: Destination email address.
    """

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("EMAIL_FROM")
    to_addr = os.getenv("EMAIL_TO")

    if not all([host, user, password, from_addr, to_addr]):
        raise ValueError("Missing SMTP configuration in environment variables")

    text_body, html_body = build_body(email_items, weather, headlines)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily Summary"
    msg["From"] = from_addr
    msg["To"] = to_addr

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
