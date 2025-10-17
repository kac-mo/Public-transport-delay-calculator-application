# Public Transport Delay Calculator Application

This mobile application, developed in Kotlin, connects to the Wrocław MPK API to retrieve public transport data such as vehicle locations, stops, and schedules. It calculates possible delays for buses and trams and displays them on an interactive map within the app. The project integrates with Firebase for data storage and backend services.

## Overview

The app fetches real-time data from the MPK Wrocław public transport API and analyzes current vehicle positions relative to the timetable to estimate delays. The calculated delays, along with route and stop information, are visualized on a map interface. The project was originally designed for Android and relies on both a configured Firebase project and a running virtual machine for backend operations.  

At present, the application is not operational without re-establishing the Firebase connection and the virtual machine.

## Technologies Used

- Programming language: Kotlin  
- Platform: Android
- Backend: Python 
- API source: Wrocław MPK API  
- Database and authentication: Firebase  
- Map and visualization: Google Maps API 

## Setup Instructions

1. **Environment setup**
   - Install Android Studio and configure the Android SDK.
   - Clone the repository to your local environment.
   - Set up a virtual or physical Android device for testing.

2. **Firebase configuration**
   - Create a Firebase project at [https://firebase.google.com/](https://firebase.google.com/).
   - Download the `google-services.json` file from your Firebase project settings and place it in the `app/` directory.
   - Enable the required Firebase services (e.g., Firestore, Authentication, or Realtime Database, depending on the app’s requirements).

3. **API connection**
   - Ensure that the Wrocław MPK API endpoint is active and accessible.
   - Add any necessary API keys or URLs to the app’s configuration files or environment variables (see below for key locations).
   - Upload the Python files to a virtual machine and run them.

5. **Running the app**
   - Open the project in Android Studio.
   - Allow Gradle to build the project and download dependencies.
   - Run the app on an emulator or connected Android device.

## Notes on Project Status

The app depends on Firebase services and a backend VM that were active during development. These must be reconfigured or recreated for the app to function correctly. Without these services, the map and delay calculation features will not update in real time.

## Purpose

This project demonstrates how to combine real-time public transport APIs with a mobile mapping interface and backend services. It provides a basis for further development of delay prediction and visualization tools for urban transit systems.
