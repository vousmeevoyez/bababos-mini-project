# Bababos Mini Project Readme

## Overview
This mini project, named "Bababos," involves running Appsmith and Metabase locally using Docker. The provided `appsmith.yml` file contains the necessary configurations for running both applications in Docker containers.

## Running Appsmith Locally

To run Appsmith locally using Docker, follow these steps:

1. Open your terminal.
2. Navigate to the project directory.
3. Run the following command:

```bash
docker-compose -f appsmith.yml up -d --build
```

## Running Metabase Locally

To run Appsmith locally using Docker, follow these steps:

1. Open your terminal.
2. Navigate to the project directory.
3. Run the following command:

```bash
docker-compose -f metabase.yml up -d --build
```

## Data
The data directory contains datasets such as historical orders and other relevant information for the project. Make sure to explore and utilize this data as needed for your development and testing purposes.
