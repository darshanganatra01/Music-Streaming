# Music Streaming Application

## Overview

This project is a full-featured music streaming web application developed as part of academic coursework. The application supports listening to music, reviewing and rating songs, playlist management, and role-based access for different types of users.

The system is designed to handle three distinct roles: User, Creator, and Admin, each with clearly defined permissions and responsibilities.

---

## User Roles and Features

### User
- Listen to songs
- Rate and review songs
- Create and manage playlists
- Option to register as a Creator

### Creator
- Upload songs
- Create, update, and delete albums
- Assign songs to albums
- View an overview of uploaded content

### Admin
- Full access to the system
- Manage and blacklist creators if required
- View system-wide statistics
- Access visual analytics such as histograms and line graphs

---

## Technologies Used

- **Flask** – Backend framework for application logic
- **Flask-SQLAlchemy** – ORM for database management
- **Jinja2** – Template engine for rendering views
- **Flask-RESTful** – REST API development
- **Flask-Security-Too** – Authentication and role-based authorization
- **Matplotlib** – Data visualization for admin analytics

---

## Architecture

The application follows the **MVC (Model–View–Controller)** architecture:

- **Model**: Handles data storage and database interactions  
- **View**: Manages presentation and UI rendering  
- **Controller**: Processes application logic and user requests  

This separation improves maintainability and scalability of the system.

---

## Database Design

The database schema is designed using an **Entity–Relationship (E-R) model**, covering entities such as:
- Users
- Roles
- Songs
- Albums
- Playlists
- Reviews

The design ensures proper relationships and efficient data handling.

---

## Additional Notes

- The UI was designed independently as part of the project
- Core features were implemented along with recommended extensions
- The project emphasizes role-based access control and structured backend design

---

## Demo Video

https://drive.google.com/file/d/1D1uuCEoaf_p8krF4DyWOjwBZrcv0N7Ep/view
