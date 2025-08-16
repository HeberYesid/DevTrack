# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context
This is a Django web application for tracking OnlineGDB exercise statistics with:

- User authentication and management
- Exercise tracking with traffic light system (green/yellow/red indicators)
- Automatic grade calculation based on exercise completion status
- Dashboard with charts and statistics visualization
- MySQL database integration
- Deployment-ready configuration for free hosting services

## Key Features
1. **Exercise Management**: Track student exercises with status indicators
2. **Grade Calculation**: 
   - 100% green exercises = 5.0 grade
   - 60% yellow exercises = 3.0 grade  
   - Rest calculated as green_count/total_count
3. **Dashboard**: Visual charts showing exercise progress and statistics
4. **User System**: Individual student accounts with personal statistics

## Technology Stack
- Backend: Django (Python)
- Database: MySQL (with SQLite fallback for development)
- Frontend: HTML, CSS, JavaScript with Chart.js
- Deployment: Ready for free hosting services

## Code Style Guidelines
- Follow Django best practices
- Use class-based views where appropriate
- Implement proper error handling
- Include comprehensive docstrings
- Follow PEP 8 style guidelines
