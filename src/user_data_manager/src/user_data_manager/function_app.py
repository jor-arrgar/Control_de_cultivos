import azure.functions as func
import logging 
import json


from lib.cloud import AzureBlobStorageManager
from lib.main_functions import get_explotations_for_user, get_request_body, get_explotation


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# MARK: Test API
@app.route(route="test")
def test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a testing request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in \
                the query string or in the request body for a personalized response.",
             status_code=200
        )


# MARK: Get exploitation
@app.route(route="get_explotation_data")
def get_explotation_data(req: func.HttpRequest) -> func.HttpResponse:

    logging.warning("Innitiating function...")
    
    # Extracting request body/params
    body = get_request_body(req=req)
    if isinstance(body, func.HttpResponse):
        return body

    # Get request param values
    user = body.get('user')
    user_key = body.get('userKey')
    explotation_name = body.get('explotation')

    variables = [user, user_key, explotation_name]
    if None in variables:
        logging.error(f'Empty parameters:')
        for var in variables:
            logging.error(f'\t- {user.__str__()}:{user}')

        return func.HttpResponse(
            "\nEmpty parameters detected\n"
        )


    # Get explotation
    explotation_json = get_explotation(
        user=user,
        explotation_name=explotation_name
    )

    if isinstance(explotation_json, dict):
        return func.HttpResponse(
            json.dumps(explotation_json, ensure_ascii=False),  # O usar el diccionario directamente
            status_code=200,
            mimetype="application/json"  # ¡Importante!
        )

    elif isinstance(explotation_json, func.HttpResponse):
        return explotation_json
    



    final_response = f"Explotation file don't downloaded."

    return func.HttpResponse(
        "\n"+final_response+"\n",
        status_code=200
    )

 
# MARK: Get explotations
@app.route(route="get_explotations_list")
def get_explotations(req: func.HttpRequest) -> func.HttpResponse:

    logging.warning("Innitiating function...")
    
    # Extracting request body/params
    body = get_request_body(req)

    # Get request param values
    user = body.get('user')
    user_key = body.get('userKey')
    
    explotations = get_explotations_for_user(user)
    explotations_ = []
    for explotation in explotations:
        logging.warning(f"\n- {explotation.name}")
        explotations_.append(explotation.name.split('/')[1])

    return func.HttpResponse(
        json.dumps(explotations_, ensure_ascii=True),
        status_code=200
    )
    


    