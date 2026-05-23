# Professional Poll API

A production-ready REST API for creating and managing polls with Django REST Framework.

## 🚀 Features

- ✅ Create, read, update, delete polls
- ✅ Vote on polls with validation
- ✅ Real-time results with percentages
- ✅ JWT Authentication
- ✅ Rate limiting & throttling
- ✅ API documentation (Swagger/ReDoc)
- ✅ Comprehensive test suite
- ✅ Docker support
- ✅ Pagination, filtering, searching
- ✅ Professional error handling

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/polls/` | List all polls |
| POST | `/api/v1/polls/` | Create a new poll |
| GET | `/api/v1/polls/{id}/` | Get poll details |
| PUT/PATCH | `/api/v1/polls/{id}/` | Update poll |
| DELETE | `/api/v1/polls/{id}/` | Delete poll |
| POST | `/api/v1/polls/{id}/vote/` | Submit a vote |
| GET | `/api/v1/polls/{id}/results/` | Get results |
| GET | `/api/v1/stats/` | Get statistics |

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/poll-api.git
cd poll-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
 
#to sync the votes 
python sync_votes.py

Access Points

http://127.0.0.1:8000/	Home page
http://127.0.0.1:8000/ui/	Voting Interface
http://127.0.0.1:8000/admin/	Admin panel
http://127.0.0.1:8000/api/v1/polls/	API endpoint
http://127.0.0.1:8000/swagger/	API docs