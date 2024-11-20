# Dart Tournament Website

Welcome to the **Dart Tournament Website**! This project is a web application built with Flask to manage dart tournaments. It provides features for creating, joining, and managing dart tournaments, as well as tracking scores and standings.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tournament Format](#tournament-format)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Setup and Installation](#setup-and-installation)

---

## Project Overview

The Dart Tournament Website is designed to help players organize and participate in dart tournaments online. The application allows users to:
- Create new tournaments.
- Register for tournaments.
- Track scores.
- View standings and results.
- Manage players and teams.

---

## Tournament Format

The tournament is divided into two parts:

1. **Group Stage**: 
   - Players are divided into groups where everyone plays against everyone else. 
   - Points are awarded based on match results, and the top players from each group advance to the next round.

2. **Double Elimination Round**: 
   - The 16 best players from the group stage advance to the double elimination bracket.
   - Players in this round compete in a knockout format, with a loser’s bracket that gives eliminated players a second chance.
   - The final winner is determined through this elimination process.
---

## Features

- **Tournament Creation**: Organizers can create a new dart tournament by specifying the tournament format and details.
- **Player Registration**: Players can join tournaments by registering their names.
- **Score Tracking**: Scores can be updated in real-time during matches.
- **Standings**: Tournament standings are displayed as players' scores and rankings are updated.
- **Match Scheduling**: Admins can schedule matches between players or teams.
  
---

## Tech Stack
Wrote using python 3.12.7

The website is built using the following technologies:

- **Flask**: A lightweight Python web framework for handling the server-side logic.
- **HTML/CSS**: For front-end design and layout.
- **JavaScript**: For interactive features on the front-end.
- **SQLite**: A simple database to store tournament and player data (you can switch to a more robust database like PostgreSQL or MySQL if needed).

---

## Setup and Installation
for the installation you need to have python.
I used python 3.12.7 to write the programm

To set up the project locally, follow these steps:

### 1. Clone the repository

First, clone the project repository to your local machine:
```bash
git clone https://github.com/fubiii11/dart-tournament-website.git
cd dart-tournament-website
```

### 2. Create a virtual environment (recommended)

Create and activate a virtual environment:

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
Once the virtual environment is activated, install the required dependencies from the requirements.txt file:

```bash
pip install -r requirements.txt
```
### 4. Set up the database
The application uses a simple SQLite database. You can set it up by running the following:

```bash
python setup_db.py
```
This will create the necessary database tables for your tournament app.

### 5. Run the application
Finally, you can run the Flask development server:

```bash
python app.py
```
The website will be available at http://127.0.0.1:5000/ in your browser.

