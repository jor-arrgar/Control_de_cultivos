# Control de cultivos - User data manager

Servicio de entrega de datos de usuario de la aplicación. Accede a los datos del usuario y sus explotaciones guardadas en la nube (almacén).

## Usage

**Lista de explotaciones para usuario**

```bash
curl -X POST "http://localhost:7071/api/get_explotations_list"   -H "Content-Type: application/json"   -d '{"check":0,"user":"test","userKey":"miPassword"}'
```

**Datos de explotación**

```bash
curl -X POST "http://localhost:7071/api/get_explotation_data"   -H "Content-Type: application/json"   -d '{"check":0,"user":"test","userKey":"miPassword", "explotation":"test_con_temporadas.json"}'
```
