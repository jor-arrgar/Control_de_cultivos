# Control de Cultivos database

## General information

### Basic info

- **Technology**: Azure SQL (tSQL)
- **Region**: UK South
- **Tier**: Free tier (32 GB & 100000 vCore seconds per month)
- **Collation**: Modern_Spanish_100_CI_AS_KS_WS_SC_UTF8

### Bussiness description

Database for project "ControlDeCultivos". This DB will contain varied information, but primarily focused on user management, ranging from authentication to actions logs. It will not contain users' explotations data as this will be stored either directly in json files in Storage Account containers or in a NO-SQL database such us MongoDB (not implemented yet).

## Database sections

### User authentication management

> users.sql

The users must be able to register into the application and set a security password so their information can be stored in the cloud. The complexity of the infrastucture architecture of this solutions requires not just save the hashed password, but a complex cryptographic system.
