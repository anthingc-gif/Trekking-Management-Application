# Trekking Management Application V2

## Project Overview

The Trekking Management Application V2 is a full-stack web application developed to manage trekking activities and improve the coordination between administrators, trekking staff, and trekkers. The system implements role-based access control to ensure that users can only access functions relevant to their responsibilities.

The application was developed using the Flask framework for the backend REST API and Vue.js 3 for the frontend single-page application (SPA). The system also incorporates caching and background task processing to improve performance and scalability.

## Objectives

The main objectives of this project are:

1. To provide a centralized platform for managing trekking activities and bookings.
2. To implement secure role-based access control for different categories of users.
3. To improve operational efficiency through automation features such as reminders, reporting, and data export.

## System Architecture

The application follows a client-server architecture consisting of two major components:

* **Backend:** Developed using Flask, responsible for business logic, database operations, authentication, and API services.
* **Frontend:** Developed using Vue.js 3, responsible for user interaction and data visualization.

Communication between the frontend and backend is performed through RESTful APIs.

## User Roles

The system supports three different user roles:

### 1. Administrator

The administrator has full control over the system and can:

* Create and manage trekking activities.
* Manage staff accounts and user accounts.
* Assign staff members to treks.
* Monitor bookings and system activities.
* Blacklist or deactivate users when necessary.

### 2. Staff

Staff members are responsible for operational activities and can:

* View assigned trekking activities.
* Update trek details and available slots.
* Manage participant information for assigned treks only.

### 3. Trekker

Trekkers are end users of the platform and can:

* Register and manage their profiles.
* Browse and search available trekking activities.
* Make and cancel bookings.
* View booking history and notifications.

## Technologies Used

| Component          | Technology              |
| ------------------ | ----------------------- |
| Backend Framework  | Flask 3.1               |
| Frontend Framework | Vue.js 3                |
| Database           | SQLite                  |
| ORM                | SQLAlchemy              |
| Authentication     | Flask-JWT-Extended      |
| Caching            | Redis and Flask-Caching |
| Background Tasks   | Celery                  |
| HTTP Communication | Axios                   |
| User Interface     | Bootstrap 5             |
| Data Visualization | Chart.js                |

## Key Features

### Authentication and Security

* JWT-based authentication mechanism.
* Role-based access control for Admin, Staff, and Trekker users.
* Protection against unauthorized access.

### Trek Management

* Creation and modification of trekking activities.
* Staff assignment functionality.
* Slot management for available trekking positions.

### Booking Management

* Prevention of duplicate bookings.
* Prevention of overbooking through slot validation.
* Booking cancellation support.

### Reporting and Notifications

* Automated daily reminders for upcoming treks.
* Monthly activity reports.
* CSV export functionality for booking history.

### Performance Optimization

* API response caching using Redis.
* Background job processing using Celery for long-running tasks.

## Project Structure

The project is divided into two main modules:

* **Backend Module:** Handles APIs, authentication, database management, and business logic.
* **Frontend Module:** Handles user interfaces, navigation, and interaction with backend services.

This separation improves maintainability, scalability, and modularity of the application.

## Conclusion

The Trekking Management Application V2 demonstrates the implementation of modern web development practices using Flask and Vue.js. The project successfully integrates authentication, role-based access control, asynchronous processing, and caching mechanisms to create a scalable trekking management platform suitable for real-world usage scenarios.
