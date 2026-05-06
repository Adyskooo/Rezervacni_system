import sys
from django.core.mail.backends.console import EmailBackend

class ReadableConsoleEmailBackend(EmailBackend):
    def write_message(self, message):
        # Získáme tělo zprávy a dekódujeme ho, aby bylo čitelné (bez quoted-printable)
        try:
            body = message.body
        except AttributeError:
            body = str(message)

        self.stream.write("\n" + "="*60 + "\n")
        self.stream.write(f" PRO:      {', '.join(message.to)}\n")
        self.stream.write(f" PŘEDMĚT:  {message.subject}\n")
        self.stream.write("-" * 60 + "\n")
        self.stream.write(f"{body}\n")
        self.stream.write("="*60 + "\n\n")
        self.stream.flush()
