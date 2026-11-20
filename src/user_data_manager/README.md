# Control de cultivos - User data manager

Servicio de entrega de datos de usuario de la aplicación. Accede a los datos del usuario y sus explotaciones guardadas en la nube (almacén).

## Usage

### Lista de explotaciones para usuario

```bash
curl -X POST "http://localhost:7071/api/get_explotations_list"   -H "Content-Type: application/json"   -d '{"check":0,"user":"test","userKey":"miPassword"}' ; echo # End with newline
```

### Datos de explotación

```bash
curl -X POST "http://localhost:7071/api/get_explotation_data"   -H "Content-Type: application/json"   -d '{"check":0,"user":"test","userKey":"miPassword", "explotation":"test_con_temporadas.json"}' ; echo
```

### Datos de usuario

```bash
curl "http://localhost:7071/api/get_user_data?check=0&user=juan@example.com"

curl -X POST "http://localhost:7071/api/get_user_data" \
  -H "Content-Type: application/json" \
  -d '{"check":0, "user":"juan@example.com"}' ; echo
```

### Nuevo usuario

```bash
curl -X POST "http://localhost:7071/api/insert_new_user" \
  -H "Content-Type: application/json" \
  -d '{"check":0,"user_data":{"code":"juan2@example.com","email":"juan2@example.com","name":"Juan2","province":"Madrid"}}' ; echo
```

### Estructura de tabla de db

```bash
curl "http://localhost:7071/api/get_table_structure?check=0&table_name=01_users" ; echo
```

### Valores únicos en una columna de la DB

```bash
curl "http://localhost:7071/api/get_column_uniques?check=0&table_name=01_users&column_name=code" ; echo
```
