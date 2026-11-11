
import logging
import json

import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError


from lib.cloud import AzureBlobStorageManager


# MARK: Process requests
def get_request_body(req: func.HttpRequest) -> func.HttpResponse | dict:
    
    # Extracting request body/params
    body = req.params
    if not body.get('check'):
        body = req.get_json()

    try:
        if int(body.get('check', 9999)) != 0:
            logging.error('Invalid checker argument. Call not authoriced & therefore rejected.')
            logging.warning(f"Value: {body.get('check', 9999)}")
            return func.HttpResponse(
                "\nInvalid request (2nd level).\n",
                status_code=401
            )
    except ValueError:
        logging.error('Invalid checker argument. Call not authoriced & therefore rejected.')
        logging.warning(f"Value: {body.get('check', 9999)}")
        return func.HttpResponse(
            "\nInvalid request (1st level).\n",
            status_code=401
        )

    return body


# MARK: Storage blobs
def get_explotations_for_user(user: str) -> list:

    user_exploitations = AzureBlobStorageManager().get_blobs_list(
                                            container_name=f"user-{user}",
                                            path="exploitations")
    logging.info(len(user_exploitations))
    return user_exploitations


def get_explotation(user: str, explotation_name: str) -> dict | None:

    explotation_path = "exploitations/" + explotation_name
    logging.warning(f'Downloading "{explotation_path}"...')
    try:
        explotation = AzureBlobStorageManager().download_blob(
                                            container_name=f'user-{user}',
                                            blob_path=explotation_path
                                            )
    except ResourceNotFoundError:
        return func.HttpResponse(
            f"The selected explotation ({explotation_name}) does not exists\n",
            status_code=400
        )

    except:
        return func.HttpResponse(
            "Error during downloading process",
            status_code=400
        )

    explotation_json = json.loads(explotation.decode("utf-8"))

    return explotation_json