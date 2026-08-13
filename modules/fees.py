import streamlit as st

from supabase_client import create_fee_record, list_fees, list_students, SUPABASE_URL
from pathlib import Path
import io
from utils.helpers import format_currency

# School details used in receipts
SCHOOL_NAME = "Shree janta Scecondary school"
SCHOOL_ADDRESS = "mayadevi-5 baluhawa"
PRINCIPAL_NAME = "ramnewas chauhan"


def render_fees(user: dict) -> None:
    st.title("💰 Fees")
    students = list_students()
    if not students:
        st.info("No students available")
        return

    student_lookup = {item["student_id"]: item["full_name"] for item in students}
    student_id = st.selectbox("Student", list(student_lookup.keys()), format_func=lambda value: student_lookup[value])
    kind = st.selectbox("Fee type", ["Admission", "Monthly", "Transport", "Exam", "Library"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    status = st.selectbox("Status", ["Pending", "Paid", "Overdue"])
    if st.button("Save fee"):
        create_fee_record(student_id=student_id, kind=kind, amount=amount, status=status)
        st.success("Fee record saved")

    st.subheader("Fee records")
    fees = list_fees()
    st.dataframe(fees, use_container_width=True, hide_index=True)

    if fees:
        # allow selecting a fee to generate a receipt
        fee_lookup = {f"{item['id']}": f"{student_lookup.get(item['student_id'], item['student_id'])} - {item['kind']} - ${item['amount']}" for item in fees}
        selected_fee_id = st.selectbox("Select fee for receipt", list(fee_lookup.keys()), format_func=lambda v: fee_lookup[v])
        if st.button("Generate receipt"):
            fee = next((f for f in fees if f["id"] == selected_fee_id), None)
            if fee is None:
                st.error("Selected fee not found")
            else:
                student_name = student_lookup.get(fee["student_id"], fee["student_id"]) 
                lines = [
                    "Shree janta Scecondary school",
                    "Address: mayadevi-5 baluhawa",
                    "Fee Receipt",
                    "-------------------------",
                    f"Receipt ID: {fee['id']}",
                    f"Student: {student_name}",
                    f"Fee type: {fee.get('kind')}",
                    f"Amount: {format_currency(fee.get('amount', 0))}",
                    f"Status: {fee.get('status')}",
                    f"Created: {fee.get('created_at')}",
                    "\nThank you for your payment.",
                ]

                out_dir = Path("data") / "receipts"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"receipt_{fee['id']}.pdf"

                # Attempt enhanced PDF generation with logo and QR code
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.utils import ImageReader
                    import qrcode

                    buffer = io.BytesIO()
                    pdf = canvas.Canvas(buffer, pagesize=letter)
                    pdf.setTitle("Fee Receipt")

                    y = 760
                    # optional logo at data/logo.png
                    logo_path = Path("data") / "logo.png"
                    if logo_path.exists():
                        try:
                            logo = ImageReader(str(logo_path))
                            pdf.drawImage(logo, 40, y - 60, width=120, height=60)
                            y -= 80
                        except Exception:
                            pass

                    pdf.setFont("Helvetica-Bold", 14)
                    pdf.drawString(40, y, SCHOOL_NAME)
                    y -= 16
                    pdf.setFont("Helvetica", 10)
                    pdf.drawString(40, y, SCHOOL_ADDRESS)
                    y -= 18
                    pdf.setFont("Helvetica-Bold", 12)
                    pdf.drawString(40, y, "Fee Receipt")
                    y -= 16
                    pdf.setFont("Helvetica", 10)
                    for line in lines[2:]:
                        if y < 60:
                            pdf.showPage()
                            y = 760
                        pdf.drawString(40, y, line)
                        y -= 14

                    # add QR code linking to a simple verification URL
                    try:
                        qr_data = f"{SUPABASE_URL.rstrip('/')}/verify?table=fees&id={fee['id']}"
                        qr = qrcode.make(qr_data)
                        qr_buf = io.BytesIO()
                        qr.save(qr_buf, format="PNG")
                        qr_buf.seek(0)
                        qr_img = ImageReader(qr_buf)
                        pdf.drawImage(qr_img, 420, 40, width=120, height=120)
                    except Exception:
                        # ignore QR failures
                        pass

                    pdf.save()
                    buffer.seek(0)
                    data = buffer.read()
                    # persist to disk as well
                    with open(out_path, "wb") as fh:
                        fh.write(data)
                    st.success("Receipt generated (PDF)")
                    st.download_button("Download receipt (PDF)", data, file_name=out_path.name, mime="application/pdf")
                except Exception:
                    # fallback to simple text/PDF generator
                    try:
                        from utils.pdf_generator import export_simple_pdf

                        export_simple_pdf(out_path, lines)
                        with open(out_path, "rb") as fh:
                            data = fh.read()
                        st.success("Receipt generated (PDF)")
                        st.download_button("Download receipt (PDF)", data, file_name=out_path.name, mime="application/pdf")
                    except Exception:
                        txt = "\n".join(lines + ["", f"Principal: {PRINCIPAL_NAME}", f"Address: {SCHOOL_ADDRESS}"])
                        st.warning("PDF generator not available — offering text receipt")
                        st.download_button("Download receipt (TXT)", txt, file_name=f"receipt_{fee['id']}.txt", mime="text/plain")
