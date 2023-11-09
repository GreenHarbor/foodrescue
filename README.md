# Food Rescue Service

## Introduction

Welcome to the Food Rescue Service repository! This service is dedicated to reducing food waste by connecting those with surplus food to those in need. Users can list and view various food items that require rescue, facilitating an efficient and ethical redistribution of resources.

## Features

- **List Surplus Food**: Users can easily list food items that they wish to donate.
- **View Available Food**: Browse through a list of available food items that need rescuing.
- **Flask-Based API**: A robust backend API built with Flask.
- **RDS Integration**: Persistent data storage with Amazon Relational Database Service (RDS).
- **Microservices Communication**: Utilizes Message Queuing (MQ) for seamless communication with other microservices.

## Getting Started

To get started with this project, please follow the instructions below:

### Prerequisites

- Python 3.6 or higher
- Flask
- Access to Amazon RDS
- A message queuing service

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/GreenHarbor/foodrescue.git
   ```
2. Navigate to the project directory:
   ```
   cd food-rescue-service
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Set up your environment variables for database and MQ credentials.

### Running the Application

1. Start the Flask server:
   ```
   flask run
   ```
2. The service should now be running and accessible at `localhost:5000`.
