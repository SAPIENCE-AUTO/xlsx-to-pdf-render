from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import tempfile
import os
import subprocess

app = FastAPI(title="XLSX to PDF (LibreOffice)", version="1.0.0")


@app.get("/health")
def health():
    return {"ok": True}


def convert_xlsx_to_pdf_bytes(xlsx_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        xlsx_path = os.path.join(td, "input.xlsx")

        with open(xlsx_path, "wb") as f:
            f.write(xlsx_bytes)

        cmd = [
            "soffice",
            "--headless",
            "--nologo",
            "--nolockcheck",
            "--nodefault",
            "--nofirststartwizard",
            "--convert-to", "pdf",
            "--outdir", td,
            xlsx_path,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if proc.returncode != 0:
            raise RuntimeError(f"LibreOffice failed: {proc.stderr[:800]}")

        pdf_path = None
        for fn in os.listdir(td):
            if fn.lower().endswith(".pdf"):
                pdf_path = os.path.join(td, fn)
                break

        if not pdf_path:
            raise RuntimeError("PDF not produced.")

        with open(pdf_path, "rb") as f:
            return f.read()


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    try:
        xlsx_bytes = await file.read()
        pdf_bytes = convert_xlsx_to_pdf_bytes(xlsx_bytes)

        filename = (file.filename or "output.xlsx").rsplit(".", 1)[0] + ".pdf"
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
