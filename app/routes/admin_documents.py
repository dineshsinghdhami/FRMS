import os

from flask import Blueprint, current_app, render_template, send_from_directory
from flask_login import login_required

from app.models.document import Document
from app.utilities.decorators import admin_required


admin_documents_bp = Blueprint(
    "admin_documents",
    __name__,
    url_prefix="/admin/documents"
)


@admin_documents_bp.route("/")
@login_required
@admin_required
def index():
    documents = Document.query.order_by(
        Document.uploaded_at.desc()
    ).all()

    return render_template(
        "admin/documents.html",
        documents=documents
    )


@admin_documents_bp.route("/<int:document_id>/download")
@login_required
@admin_required
def download(document_id):
    document = Document.query.get_or_404(document_id)

    documents_folder = os.path.join(
        current_app.root_path,
        "uploads",
        "documents"
    )

    return send_from_directory(
        documents_folder,
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )