import azure.functions as func
import logging 
import json


from support.main_functions import *


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# MARK: Test API
@app.route(route="health")
def test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a testing request.')

    return func.HttpResponse(
        json.dumps({"status": "healthy", "code": 200})
    )


# MARK: Get exploitation
@app.route(route="get_explotation_data")
def get_explotation_data(req: func.HttpRequest) -> func.HttpResponse:

    logging.warning("Innitiating function \"get_explotation_data\"...")
    
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

    logging.warning("Innitiating function \"get_explotations\"...")
    
    # Extracting request body/params
    body = get_request_body(req)

    # Get request param values
    user = body.get('user')
    
    explotations = get_explotations_for_user(user)
    explotations_ = []
    for explotation in explotations:
        logging.warning(f"\n- {explotation.name}")
        explotations_.append(explotation.name.split('/')[1])

    return func.HttpResponse(
        json.dumps(explotations_, ensure_ascii=True),
        status_code=200
    )
    
# MARK: Get user data
@app.route(route="get_user_data")
def get_user_data(req: func.HttpRequest) -> func.HttpResponse:

    logging.warning("Innitiating function \"get_user_data\"...")
        
    # Extracting request body/params
    body = get_request_body(req)

    # Get request param values
    user = body.get('user')

    logging.warning(f"Retrieving user data for user '{user}'...")
    user_data, code = consult_user_data(user)
    logging.warning(f"User data retrieved for user '{user}': {code}")
    return user_data
    



# MARK: Insert new user
@app.route(route="insert_new_user", methods=["POST"])
def insert_new_user_route(req: func.HttpRequest) -> func.HttpResponse:
    logging.warning("Innitiating function \"insert_new_user_route\"...")

    # Extracting request body/params
    body = get_request_body(req)

    if isinstance(body, func.HttpResponse):
        return body
    # Get request param values
    user_data = body.get('user_data')

    if not isinstance(user_data, dict):
        return func.HttpResponse(
            "Invalid user data format. Expected a dictionary.",
            status_code=400
        )

    try:
        insert_new_user(user_data)
        return func.HttpResponse(
            json.dumps({"message": "User inserted successfully."}, ensure_ascii=True),
            status_code=200
        )
    except Exception as e:
        logging.error(f"Failed to insert new user: {e}")
        return func.HttpResponse(
            f"Failed to insert new user: {e}",
            status_code=500
        )



# MARK: Get table structure
@app.route(route="get_table_structure")
def get_table_structure_route(req: func.HttpRequest) -> func.HttpResponse:
    logging.warning("Innitiating function \"get_table_structure_route\"...")

    # Extracting request body/params
    body = get_request_body(req)

    if isinstance(body, func.HttpResponse):
        return body

    # Get request param values
    table_name = body.get('table_name')

    if not table_name:
        return func.HttpResponse(
            "Missing 'table_name' parameter.",
            status_code=400
        )

    table_structure = get_table_structure(table_name)
    if isinstance(table_structure, list):
        logging.warning('Table structure obtained')
        return func.HttpResponse(
            json.dumps(table_structure, ensure_ascii=True),
            status_code=200
        )
    else:
        logging.error('Table structure not generated')
        return table_structure  # This is an HttpResponse in case of error


# MARK: Get uniques for column
@app.route(route="get_column_uniques")
def get_uniques_for_column(req: func.HttpRequest) -> func.HttpResponse:
    logging.warning("Innitiating function \"get_uniques_for_column\"...")

    # Extracting request body/params
    body = get_request_body(req)

    if isinstance(body, func.HttpResponse):
        return body

    # Get request param values
    table_name = body.get('table_name')
    column_name = body.get('column_name')

    uniques, code = get_column_uniques(table_name, column_name)

    return uniques
