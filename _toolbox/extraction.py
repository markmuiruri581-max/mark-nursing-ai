"""Local-only text extraction helpers for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
from typing import Any

from _toolbox import paths, security


EXTRACTION_STATUS_EXTRACTED = "EXTRACTED"
EXTRACTION_STATUS_FAILED = "FAILED"
EXTRACTION_STATUS_UNSUPPORTED = "UNSUPPORTED"
TEXT_EXTENSIONS = {".txt", ".md"}
HTML_EXTENSIONS = {".html", ".htm"}


@dataclass(frozen=True)
class ExtractionResult:
    """Result from a local source extraction attempt."""

    record_update: dict[str, Any]
    metadata: dict[str, Any]
    text_written: bool


class VisibleTextParser(HTMLParser):
    """Extract visible text from simple HTML using the standard library."""

    def __init__(self) -> None:
        super().__init__()
        self._hidden_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._hidden_depth == 0:
            cleaned = " ".join(data.split())
            if cleaned:
                self._chunks.append(cleaned)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


def read_plain_text(path: Path) -> str:
    """Read local plain text with replacement for invalid UTF-8."""

    return path.read_text(encoding="utf-8", errors="replace")


def extract_html_text(path: Path) -> str:
    """Extract visible text from a local HTML file."""

    parser = VisibleTextParser()
    parser.feed(read_plain_text(path))
    parser.close()
    return parser.get_text()


def extract_pdf_text(path: Path) -> tuple[str, str]:
    """Extract PDF text only when an optional local PDF package is available."""

    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError as pypdf_error:
        try:
            from PyPDF2 import PdfReader  # type: ignore[import-not-found]
        except ImportError as pypdf2_error:
            raise RuntimeError(
                "PDF extraction requires optional local dependency pypdf or PyPDF2."
            ) from pypdf2_error
        method = "PyPDF2"
    else:
        method = "pypdf"

    reader = PdfReader(str(path))
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts), method


def build_output_paths(module_dir: Path, source_id: str) -> tuple[Path, Path]:
    """Return extracted-text and metadata paths for one source ID."""

    research_paths = paths.get_research_module_paths(module_dir)
    return (
        research_paths.extracted_text_dir / f"{source_id}.txt",
        research_paths.metadata_dir / f"{source_id}.json",
    )


def ensure_output_paths_available(text_path: Path | None, metadata_path: Path) -> None:
    """Refuse to overwrite extraction outputs."""

    if text_path is not None and text_path.exists():
        raise FileExistsError(f"Refusing to overwrite extracted text file: {text_path}")
    if metadata_path.exists():
        raise FileExistsError(f"Refusing to overwrite metadata file: {metadata_path}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write UTF-8 JSON without changing existing files."""

    if path.exists():
        raise FileExistsError(f"Refusing to overwrite metadata file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_metadata(
    source_record: dict[str, Any],
    *,
    status: str,
    source_path: Path,
    extracted_text_path: str,
    metadata_path: str,
    extracted_at: str,
    text_char_count: int,
    extraction_method: str,
    extraction_error: str,
) -> dict[str, Any]:
    """Build metadata for one extraction attempt."""

    return {
        "source_id": source_record["source_id"],
        "source_type": source_record.get("source_type", ""),
        "original_filename": source_record.get("original_filename", ""),
        "stored_filename": source_record.get("stored_filename", ""),
        "relative_stored_path": source_record.get("relative_stored_path", ""),
        "source_sha256": source_record.get("sha256", ""),
        "file_size": source_record.get("file_size", 0),
        "file_extension": source_path.suffix.lower(),
        "extraction_status": status,
        "extracted_text_path": extracted_text_path,
        "metadata_path": metadata_path,
        "extracted_at": extracted_at,
        "text_char_count": text_char_count,
        "extraction_method": extraction_method,
        "extraction_error": extraction_error,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
    }


def extract_local_source(
    workspace_root: Path,
    module_dir: Path,
    source_record: dict[str, Any],
    *,
    extracted_at: str,
) -> ExtractionResult:
    """Extract text and metadata for one registered local source."""

    if source_record.get("source_type") != "local_file":
        raise ValueError(f"Source is not a local file: {source_record.get('source_id', '')}")

    source_id = str(source_record.get("source_id", "")).strip()
    relative_source_path = str(source_record.get("relative_stored_path", "")).strip()
    if not source_id or not relative_source_path:
        raise ValueError("Local source record is missing source_id or relative_stored_path.")

    source_path = security.assert_safe_local_path(workspace_root, workspace_root / relative_source_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"Registered local source file does not exist: {source_path}")

    text_path, metadata_path = build_output_paths(module_dir, source_id)
    security.assert_safe_local_path(workspace_root, text_path)
    security.assert_safe_local_path(workspace_root, metadata_path)
    extension = source_path.suffix.lower()
    extracted_text = ""
    status = EXTRACTION_STATUS_EXTRACTED
    method = ""
    error = ""
    should_write_text = True

    try:
        if extension in TEXT_EXTENSIONS:
            extracted_text = read_plain_text(source_path)
            method = "utf-8-text"
        elif extension in HTML_EXTENSIONS:
            extracted_text = extract_html_text(source_path)
            method = "html.parser"
        elif extension == ".pdf":
            extracted_text, method = extract_pdf_text(source_path)
        else:
            status = EXTRACTION_STATUS_UNSUPPORTED
            method = "unsupported"
            error = f"Unsupported file extension: {extension or '[none]'}"
            should_write_text = False
    except Exception as exc:
        status = EXTRACTION_STATUS_FAILED
        method = method or "failed"
        error = str(exc)
        should_write_text = False

    output_text_path = text_path if should_write_text else None
    ensure_output_paths_available(output_text_path, metadata_path)

    relative_text_path = (
        paths.relative_to_workspace(workspace_root, text_path) if should_write_text else ""
    )
    relative_metadata_path = paths.relative_to_workspace(workspace_root, metadata_path)
    text_char_count = len(extracted_text) if should_write_text else 0
    metadata = build_metadata(
        source_record,
        status=status,
        source_path=source_path,
        extracted_text_path=relative_text_path,
        metadata_path=relative_metadata_path,
        extracted_at=extracted_at,
        text_char_count=text_char_count,
        extraction_method=method,
        extraction_error=error,
    )

    if should_write_text:
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(extracted_text, encoding="utf-8", newline="\n")
    write_json(metadata_path, metadata)

    record_update = {
        "extraction_status": status,
        "extracted_text_path": relative_text_path,
        "metadata_path": relative_metadata_path,
        "extracted_at": extracted_at,
        "text_char_count": text_char_count,
        "file_extension": extension,
        "extraction_method": method,
        "extraction_error": error,
    }
    return ExtractionResult(
        record_update=record_update,
        metadata=metadata,
        text_written=should_write_text,
    )
