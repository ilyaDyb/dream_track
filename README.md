# DreamTrack

DreamTrack is a gamified task and goal tracker combining productivity tools with an RPG-like experience. Users earn XP and coins for completing tasks, level up, and can spend earned rewards in an in-app shop featuring avatars, backgrounds, and more.

## 🚀 Key Features

### 🎯 Tasks (TODO)

- Create tasks with deadlines and difficulty levels.
- Completing tasks grants XP and coins.
- Designed to reinforce habit-building through rewards.

### 📈 Level System

- Automatically levels up users as they gain XP.
- Uses progressive XP requirements for each level.

### 💰 Shop

- Purchase items with earned coins or donation-based crystals.
- Multiple item types: avatars, icons, backgrounds, and boosts.
- Filtering, searching, and pagination for items.

### 🎒 Inventory

- Displays all purchased items.
- Allows users to apply items (e.g. change avatar, icon, background).
- Updates user profile visuals upon application.

### ⚡ Boosts

- Temporary power-ups for XP or coin earnings.
- Duration-based, with safeguards against stacking same-type boosts.
- Automatically expires and prevents multiple boosts of the same type.

### 🔥 Streak System

- Tracks user's daily activity streak.
- Rewards consistent usage with special badges and bonuses.
- Automatically updates streaks based on user activity.
- Provides milestone rewards for reaching streak thresholds.
- Motivates users to maintain daily engagement.

### 🏆 Achievements
- Users earn achievements for reaching activity milestones.
- Supports XP, coins, and item rewards.
- Automatically granted based on triggers (e.g., completed tasks, bought items).

### 📊 Statistics
- Tracks key user activity: completed tasks, bought/equipped items, finished dreams.
- Updated automatically via UserProgressService (in progress).
- Used internally to validate achievement conditions.

### ✅ Progress Tracking
- Unified service to update statistics and check for achievements.
- Triggered inside business logic: purchases, completions, etc.
- Easily extensible with new stat types and triggers.

### 🔄 Trade System
- Allows users to exchange items and coins with each other.
- Trade offers include both items and in-game currency.
- Three-stage process: request, review, and accept/reject.
- Trade validation ensures users own offered items.
- Transaction safety with database-level consistency.
- Real-time status updates for both trade participants.
- Trade history for tracking past exchanges.
- Protection against fraudulent trades through validation checks.

### 🌱 Habit System
- Create recurring habits.
- Track habit completion streaks and consistency metrics.
- Earn rewards for maintaining consistent habit completion.


### ⚡ Performance & Stability & Integrations
- Implemented caching for API responses.
- Implemented pagination for API responses.
- Implemented rate limiting for API responses.
- Added caching for achievements, significantly reducing database queries and improving API response times.
- Integrated with OpenRouter AI for generating dream steps using artificial intelligence.

### 📄 Swagger API Docs

- Full API schema using drf-yasg.
- Interactive testing through Swagger UI.

### 🎰 Daily Roulette
- The user can spin the wheel of fortune once a day. Rewards include coins, experience, and rare, unique items.

### 🤝 Friendship System
- Ability to send and receive friend requests.
- View your friends list.
- Accept or decline incoming requests.

---

## 🛠️ Tech Stack

- Python 3.10
- Django / Django REST Framework
- PostgreSQL
- Swagger / drf-yasg
- OpenRouter AI
- JWT
- Pillow for image processing
- Python-dotenv for environment variables
- Django REST Framework SimpleJWT for authentication
- Redis for caching
- Docker and Docker Compose for containerization
- Pytest for testing

---

## ⚙️ Setup

```bash
git clone https://github.com/yourname/dreamtrack.git
cd dreamtrack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📬 Contact

Developer: Ilya Dybovsky\
Email: [ilya77788899@mail.ru]
Phone number: +79170760362
Telegram: @wicki7