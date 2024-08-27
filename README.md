# Payload Data Migration Tool

## Rationale
This migration tool has been created to facilitate the migration of data between different instances of [Payload CMS](https://payloadcms.com/). A good use case for the tool could be when you want to migrate data from a Payload CMS instance using MongoDB to an instance that uses PostgreSQL. The tool utilizes the Payload [REST API](https://payloadcms.com/docs/rest-api/overview) which abstracts all the database operations.

## Installation and Usage
To install the tool follow through the following steps:

1. Clone the repository.
1. Create a [virtual environment](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/) for your project.
1. Change into the cloned project directory and run the following command to install the project dependencies.

    <pre>
    pip install -r requirements.txt
   </pre>
1. Create a `.env` file for your project and set the required settings ```cp .env.example .env``` For more details see [Environment Variables Definition](#environment-variables-definition).

1. Configure the collections you want to import data in the `./collections` directory. A sample configurations file is provided with this project.

1. Execute the `start_data_migration.py` file to start the data migration




## Environment Variables Definition
In this context, `SOURCE` refers to the Payload instance from which data will be copied, while `SINK` refers to the Payload instance where the data will be newly created or migrated, 

Thus, Sink credentials are variables used to configure the target Payload instance, where data will be migrated or newly created, the definition for the configured variables are as follows:

- **`SINK_USERNAME`**: The username for authenticating with the SINK Payload instance.
- **`SINK_PASSWORD`**: The password associated with the `SINK_USERNAME` for authentication.
- **`SINK_API_URL`**: The API URL endpoint of the SINK Payload instance where the data will be transferred.

Source variables are variables used to configure the source Payload instance, from which data will be copied, the definition for the configured variables are as follows:

- **`SOURCE_USERNAME`**: The username for authenticating with the SOURCE Payload instance.
- **`SOURCE_PASSWORD`**: The password associated with the `SOURCE_USERNAME` for authentication.
- **`SOURCE_API_URL`**: The API URL endpoint of the SOURCE Payload instance from which the data will be retrieved.
