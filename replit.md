# NurseAI - Your Living AI Health Companion

## Overview
NurseAI is a full-stack emotionally intelligent AI co-care health companion designed to foster a genuine human-AI partnership for health and wellness. Built with Flask, PostgreSQL, and Perplexity AI, it evolves with the user, offering personalized support and tracking. The project's ambition is to create an AI that feels alive and deeply integrated into the user's health journey, providing a personalized health journey with market potential in AI-driven wellness.

## User Preferences
- UI Style: Gen-Z vibecoding with emojis, gradients, micro-interactions
- Animation: Lifelike heartbeat and breathing effects
- Tone: Warm, supportive, non-judgmental
- Goal: Create genuine attachment, not just usage

## System Architecture
NurseAI utilizes a Flask backend with PostgreSQL for data persistence. The frontend is built with HTML templates and JavaScript, emphasizing dynamic and emotionally adaptive UI/UX.

**UI/UX Decisions & Design Patterns:**
- **Living Navigation:** Animated nurse avatar with heartbeat pulse and emotional reactions.
- **Emotionally Adaptive Dashboard:** Personalized greetings, mood check-ins, Co-Care Score, and dynamic UI theming based on user and nurse emotional states, including a 7-day analytics chart and dynamic heart-beat animation.
- **10-Emotion Nurse Feelings System:** Nurse displays detailed emotions triggered by user behavior, each with associated physiological responses and contextual messages.
- **Animated Assets:** Integration of various GIFs for micro-interactions and celebrations, alongside Google Material Icons.
- **Responsive Design:** Optimized for desktop, tablet, and mobile.
- **Co-Created Onboarding:** Interactive profile setup, nurse naming, avatar selection, and preference setting.
- **Co-Care Planner:** Routine management with duration tracking, expanded categories, browser notifications, and celebration animations.
- **First-Aid Co-Assist:** AI chat with quick tips UI for common symptoms and Markdown-formatted responses.
- **Co-Reflection & Growth:** Weekly journal with AI insights and preference learning.
- **Centralized Z-Index Hierarchy:** Global CSS variable system for consistent layering of all UI components.
- **Enhanced Onboarding Tour:** Improved overlay visibility, pulsing highlights, and directional tooltip arrows.
- **Emotion Selection Popup:** Animated modal for emotion selection with enhanced styling and dark mode support.
- **Collapsible Feeling Selector:** After selecting daily emotion, the selector collapses into a compact summary view, allowing users to expand and update their feeling.

**Technical Implementations:**
- **Replit Authentication:** Supports login via Google, GitHub, or email/password with proper session management.
- **Database Schema:** Includes tables for users, nurse profiles, moods, routines, medical history, reflections, and chat messages.
- **Personality Engine:** Nurse's mood, energy, and heartbeat adapt based on user behavior and care patterns.
- **Browser Notification System:** Utilizes Web Audio API and native browser notifications for routine reminders.
- **Client-side & Server-side Validation:** Ensures data integrity for all user inputs.
- **AI-Powered Improvement Suggestions:** AI generates personalized tips displayed in an animated modal after emotion selection.
- **Smart Reminder Pop-up System:** Automatic reminder detection with snooze functionality, musical chimes, and one-click routine completion.
- **Clean AI Responses:** Citation markers are removed from all Perplexity AI responses.
- **Reminder Bell Icon:** A live, animated bell icon in the navbar indicates the count of upcoming reminders.
- **Medical History View & Download:** Allows viewing full record details and exporting all medical history as JSON.
- **Real-Time Reminder System:** Checks for reminders every 10 seconds for accurate time matching.
- **Real-Time Dashboard Updates:** Dashboard statistics auto-refresh every 30 seconds, including real-time reminder statistics (coming, missed, completed today, total routines, day streak, Co-Care Score).
- **Time Format Standardization:** All time displays and internal comparisons consistently use a 24-hour format.
- **Missed Reminder Database Tracking:** A new `MissedReminder` table logs when routines pass their scheduled time without completion.
- **AI Text Formatting:** Client-side markdown-to-HTML conversion for AI-generated content (bold, italic, line breaks, bullet points).
- **7-Day Activity Trend Lines:** SVG-based multi-line chart showing completed (green), coming (blue), and missed (red) metrics over 7 days with normalized coordinate system, responsive scaling, interactive hover tooltips, y-axis scale labels, and smart padding to prevent clipping.
- **Heartbeat States:** Two physiological states - "normal" (60-100 bpm, calm/positive emotions) and "stressing" (100+ bpm, anxious/emergency states).
- **Positive-First Emotion System:** Emotion determination algorithm prioritized to default to positive states (happy, calm, energetic) with higher thresholds for negative emotions.
- **AI-Generated Daily Health Quote:** Personalized motivational quote displayed in planner using Perplexity AI's "sonar" model, contextually generated based on nurse name and user's routine progress.

## External Dependencies
- **Perplexity AI:** Exclusively used for all AI features (personalized greetings, chat responses, medical information, weekly insights, symptom analysis, daily health quotes) using three models:
  - `sonar` - General queries, greetings, emotion tips, daily health quotes
  - `sonar-pro` - Complex medical information, emergency responses, weekly insights
  - `sonar-deep-research` - Comprehensive research (reserved for future use)
- **PostgreSQL:** Primary database for all application data.
- **Replit Auth:** Integrated for user authentication.
- **marked.js:** Used for rendering Markdown in chat messages.

## Recent Changes (Nov 8, 2025)
- Replaced heartbeat terminology from "fast/slow" to "normal/stressing" for more accurate physiological representation
- Refactored emotion determination logic to favor positive emotional states with higher thresholds for negative emotions
- Added AI-generated daily health quote feature in planner using Perplexity AI
- Default nurse emotion now "happy" instead of "calm" for more welcoming experience
- **Navbar Enhancement:** Increased heartbeat GIF size (w-10 h-10) for better visibility
- **Routine Management CRUD:** Added view, edit, and delete functionality for routines with secure user ownership validation
- **Modern Dashboard Chart:** Redesigned 7-day analytics with gradient-filled areas, glassmorphic design, animated pill legend with pulsing indicators, smooth line-drawing animations displaying clean trend lines, and hover tooltips showing daily counts for all three metrics (completed, coming, missed)
- **JSON Serialization Fix:** Converted Routine objects to dictionaries in planner route to enable proper JSON serialization for JavaScript modals
- **Chart Hover Tooltips:** Added interactive tooltips on the 7-day analytics chart that display all three metrics (completed, coming, missed) when hovering over any day
- **Automatic Tour After Signup:** Implemented onboarding tour auto-trigger when users complete signup, with URL parameter cleanup for clean navigation
- **Responsive Personalized Tips Modal:** Fixed modal to properly fit within viewport (90vh max-height) with scrollable content area, preventing overflow on long AI-generated tips
- **Reminder Calculation Bug Fix:** Fixed logic for calculating missed and coming reminders across dashboard, planner, and stats API to properly handle edge cases (None values, empty strings, False states) with explicit checks and error logging
- **Duration-Aware Routine Tracking:** Implemented smart routine expiration system where time-boxed routines (7 days, 2 weeks, 1 month, etc.) automatically stop counting toward coming/missed metrics after their duration expires, while "ongoing" routines remain active indefinitely
- **Created Date Display:** Added "Created [date]" badge to routine cards in planner with calendar icon for better tracking and context
- **Robust Duration Parser:** Created `is_routine_within_duration()` helper function supporting all duration formats (days, weeks, months, years, ongoing) with comprehensive error handling, validation, and expiry logging for debugging
- **Fixed Routine Creation Timestamp:** Routines now explicitly set created_at with current datetime.now() to ensure accurate creation timestamps
- **Improved Streak Calculation:** Completely rewrote streak logic with simplified algorithm - if today has no completions yet, the streak persists from yesterday's count; completing a routine immediately increases the streak counter by including today
- **Fixed Routine Completion Timestamp:** Routine completions now explicitly set completed_at with current datetime.now() to prevent timezone and date conflicts, ensuring accurate tracking across day transitions