from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import shutil
import os
from datetime import datetime, timedelta
import asyncio
import uuid

# Configure upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# File expiration time in minutes
FILE_EXPIRATION_MINUTES = 60


async def check_and_delete_expired_files():
    """
    Periodically check for expired files and delete them.
    Runs every 5 minutes.
    """
    while True:
        try:
            current_time = datetime.now()

            # Check all files in the upload directory
            for filename in os.listdir(UPLOAD_DIR):
                filepath = os.path.join(UPLOAD_DIR, filename)
                file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
                expiration_time = file_creation_time + timedelta(
                    minutes=FILE_EXPIRATION_MINUTES
                )

                if current_time >= expiration_time:
                    try:
                        os.remove(filepath)
                        print(f"Deleted expired file: {filename}")
                    except Exception as e:
                        print(f"Error deleting file {filepath}: {e}")

        except Exception as e:
            print(f"Error in cleanup task: {e}")

        # Wait for 5 minutes before next check
        await asyncio.sleep(300)  # 5 minutes in seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Clean existing files and start cleanup task
    for file in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, file)
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up file {filepath}: {e}")

    # Start the background cleanup task
    cleanup_task = asyncio.create_task(check_and_delete_expired_files())

    yield  # Server is running

    # Shutdown: Cancel cleanup task and perform cleanup
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Mount the upload directory for static file serving
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate UUID and preserve file extension
        original_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{str(uuid.uuid4())}{original_extension}"
        filepath = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return the download URL and file information
        download_url = f"/files/{unique_filename}"
        return JSONResponse(
            {
                "message": "File uploaded successfully",
                "filename": unique_filename,
                "download_url": download_url,
                "size_bytes": os.path.getsize(filepath),
                "expires_in": f"{FILE_EXPIRATION_MINUTES} minutes",
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Failed to upload file: {str(e)}"}
        )


@app.get("/files/list/")
async def list_files():
    """List all available files and their information"""
    files = []
    current_time = datetime.now()

    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
        expiration_time = creation_time + timedelta(minutes=FILE_EXPIRATION_MINUTES)
        remaining_time = expiration_time - current_time

        files.append(
            {
                "filename": filename,
                "upload_time": creation_time.isoformat(),
                "expires_at": expiration_time.isoformat(),
                "remaining_minutes": max(0, round(remaining_time.total_seconds() / 60)),
                "size_bytes": os.path.getsize(filepath),
                "download_url": f"/files/{filename}",
            }
        )

    return {"files": files}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9898)
