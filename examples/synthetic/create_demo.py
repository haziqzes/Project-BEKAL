"""Create a wholly fabricated receipt PDF for local BEKAL demonstrations."""

from pathlib import Path

from reportlab.pdfgen import canvas


def main() -> None:
    destination = Path(__file__).with_name("demo_receipt.pdf")
    document = canvas.Canvas(str(destination), pagesize=(400, 600), invariant=1)
    document.setFont("Helvetica", 12)
    for index, line in enumerate((
        "SYNTHETIC DEMO MART",
        "Date: 10/10/2026",
        "Receipt No: DEMO-001",
        "Payment: Card",
        "MILK 2 pcs 4.50 9.00",
        "BREAD 1 pcs 3.50 3.50",
        "Subtotal RM 12.50",
        "Total RM 12.50",
    )):
        document.drawString(35, 550 - index * 30, line)
    document.save()
    print(destination)


if __name__ == "__main__":
    main()
