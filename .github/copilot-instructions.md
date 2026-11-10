# Project Context
This is a React application using Streamlit as main GUI technology and Azure Functions with Python to act as proxi server to manage Azure Cloud data access from the Streamlit app server.

In this moment, the project contains:
- Stremalit app GUI for client users ("./src/control_de_cultivos/*)
- Azure Function app (python) to act as a proxi between Azure and Streamlit server ("./src/user_data_manager/*)
- Azure Storage Account for blobs (cloud)

The aim of this project is to set up a digital system to manage European CAP (Common Agrary Policy) information for farmers, where they can set up their agricultural exploitation (parcels, crops, whells, etc.), manage farming campaigns and planificate future campaigns while compliying with all CAP policies, both mandatory and optional ones.





# Agent behaivour
- When edditing any file, the agent does not need to compile the editted files by default, only if the developers requests a complete agentic programming session (explicit told by developer). Also don't try to execute any file unless the developer tells you explicitly.
- Check the codebase searching for customiced classes already created for the project before implementing new features. If you have any doubt if using them, ask the developer for help and wait for its answer to decide if create complete new code or use heredable classes or already set up classes.
