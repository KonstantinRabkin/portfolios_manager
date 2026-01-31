from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse

from backup_utils import (
    create_backup_file,
    get_latest_backup_path,
    restore_from_bytes,
)

router = APIRouter(prefix="/backup", tags=["backup"])


@router.post("/create")
async def backup_create():
    path: Path = create_backup_file()
    return RedirectResponse(
        url="/?error=JSON+backup+created:+{}".format(path.name),
        status_code=303,
    )


@router.get("/download")
async def backup_download():
    path = get_latest_backup_path()
    if not path:
        return RedirectResponse(
            url="/?error=No+backup+files+found",
            status_code=303,
        )
    return FileResponse(
        path,
        media_type="application/json",
        filename=path.name,
    )


@router.post("/restore")
async def backup_restore(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        return RedirectResponse(
            url="/?error=Uploaded+JSON+backup+is+empty",
            status_code=303,
        )

    try:
        restore_from_bytes(content)
    except Exception:
        return RedirectResponse(
            url="/?error=Failed+to+restore+JSON+backup",
            status_code=303,
        )

    return RedirectResponse(
        url="/?error=JSON+backup+restored",
        status_code=303,
    )

