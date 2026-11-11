import struct

from sqlalchemy import create_engine, event, text
from azure.identity import AzureCliCredential

# Configuración
SERVER = "personalprojects-jar-uks.database.windows.net"
DATABASE = "free-ControlDeCultivos-DEV"

# Configuración de autenticación
credential = AzureCliCredential()

SQL_COPT_SS_ACCESS_TOKEN = 1256
TOKEN_SCOPE = "https://database.windows.net/.default"

# Cadena de conexión SQLAlchemy
connection_string = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
)

engine = create_engine(
    connection_string,
    pool_pre_ping=True
)

# Inyectar el token de Microsoft Entra ID
@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):

    # SQLAlchemy añade Trusted_Connection automáticamente
    cargs[0] = cargs[0].replace(
        ";Trusted_Connection=Yes", ""
    )

    # Obtener token usando la sesión de az login
    token = credential.get_token(TOKEN_SCOPE).token

    # Codificación requerida por el driver ODBC
    token_bytes = token.encode("utf-16-le")

    token_struct = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes
    )

    cparams["attrs_before"] = {
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    }


# Probar conexión
with engine.connect() as connection:
    result = connection.execute(
        text("SELECT SYSTEM_USER, DB_NAME()")
    )
    print(result.fetchone())