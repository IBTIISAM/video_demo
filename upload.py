# upload.py

import logging
import requests
from config import config


def upload_file_simple(file_path):
    logger = logging.getLogger("ALLaM-Chat")
    logger.info(f"Attempting to upload file: {file_path}")
    upload_url = config["upload_url"]

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(upload_url, files=files)

        if response.status_code == 200:
            response_data = response.json()
            logger.info(
                f"File uploaded successfully. Download URL: {response_data.get('download_url')}"
            )
            return response_data
        else:
            error_msg = (
                f"Upload failed with status {response.status_code}: {response.text}"
            )
            logger.error(error_msg)
            raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}", exc_info=True)
        raise


def handle_file_upload(file, *histories):
    logger = logging.getLogger("ALLaM-Chat")
    if file:
        try:
            logger.info("Processing file upload for multiple histories")
            upload_response = upload_file_simple(file.name)
            for history in histories:
                history.set_image_url(upload_response["download_url"])
        except Exception as e:
            error_msg = f"⚠️ Error uploading file: {str(e)}"
            logger.error(error_msg)
    else:
        logger.info("Clearing file upload")
        for history in histories:
            history.set_image_url(None)
