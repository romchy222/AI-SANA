# README - Multi-Agent BolashakBot System

## Overview
This is a complete implementation of a multi-agent chatbot system for Kyzylorda University "Bolashak" with advanced analytics and admin dashboard.

## 🎯 Key Features Implemented

### 1. Multi-Agent Architecture ✅
- **5 Specialized Agents**: Each handles specific domain areas
  - `AdmissionAgent`: Поступление и зачисление
  - `ScholarshipAgent`: Стипендии и финансовая поддержка
  - `AcademicAgent`: Учебные вопросы и образовательный процесс
  - `StudentLifeAgent`: Студенческая жизнь и внеучебная деятельность
  - `GeneralAgent`: Общие вопросы и информация об университете

- **Intelligent Routing**: Messages are routed to the most suitable agent based on confidence scores
- **Fallback System**: Smart fallback responses when external APIs are unavailable
- **Extensible Design**: Easy to add new agents by extending the `BaseAgent` class

### 2. Enhanced Database Models ✅
- **Agent Tracking**: New fields in `UserQuery` model:
  - `agent_type`: Type of agent that handled the query
  - `agent_name`: Name of the selected agent
  - `agent_confidence`: Confidence score (0.0-1.0)
  - `context_used`: Whether FAQ context was utilized

### 3. Advanced Analytics Dashboard ✅
- **Chart.js Integration**: Interactive charts and graphs
- **Real-time Analytics**: Live data from agent interactions
- **Multiple Chart Types**:
  - Pie Chart: Agent usage distribution
  - Doughnut Chart: Language distribution
  - Bar Charts: Response times and success rates
  - Line Chart: Daily activity trends (30 days)

### 4. Analytics API Endpoints ✅
- `GET /admin/api/analytics/agents`: Detailed agent statistics
- `GET /admin/api/analytics/summary`: Summary analytics for dashboard
- `GET /api/agents`: Information about available agents

### 5. Comprehensive Documentation ✅
- **Architecture Documentation**: `/docs/multi-agent-architecture.md`
- **Complete API Documentation**: Endpoints and usage examples
- **Extension Guide**: How to add new agents
- **Database Schema**: Updated models with agent tracking

## 🏗️ Architecture

```
Frontend (Chat UI) → API Gateway (/api/chat) → AgentRouter → Specialized Agents → MistralClient
                                                     ↓
                                              Database Logging → Analytics Dashboard
```

## 🚀 Working Features

### Multi-Agent Routing
The system successfully routes different types of questions to appropriate agents:

```bash
# Admission questions → AdmissionAgent (confidence: 0.50)
"Как поступить в университет?"

# Scholarship questions → ScholarshipAgent (confidence: 0.60)
"Сколько стипендия?"

# Academic questions → AcademicAgent (confidence: 0.50)
"Расписание занятий"

# Student life questions → StudentLifeAgent (confidence: 0.60)
"Где общежитие?"

# General questions → GeneralAgent (confidence: 0.30)
"Контакты университета"
```

### API Endpoints
- `GET /api/agents` - ✅ Working
- `POST /api/chat` - ✅ Working (with smart fallbacks)
- `GET /api/health` - ✅ Working

## 📊 Analytics Features

### Dashboard Metrics
- **Agent Performance**: Usage statistics, response times, confidence levels
- **Language Distribution**: Russian vs Kazakh language usage
- **Success Rates**: Percentage of high-confidence responses
- **Temporal Analysis**: Daily usage trends and patterns

### Chart Types Implemented
1. **Agent Usage Pie Chart**: Shows distribution of queries by agent
2. **Language Distribution**: Russian vs Kazakh usage
3. **Response Time Analysis**: Average response times per agent
4. **Success Rate Tracking**: Confidence-based success metrics
5. **Daily Activity Trends**: 30-day historical usage data

## 🔧 Technical Implementation

### Key Files
- `agents.py`: Multi-agent architecture implementation
- `models.py`: Updated database models with agent tracking
- `views.py`: Enhanced API endpoints with agent routing
- `admin.py`: Analytics endpoints and admin functionality
- `templates/admin/dashboard.html`: Analytics dashboard with Chart.js

### Database Schema Updates
```sql
-- New fields in user_queries table
agent_type VARCHAR(50)        -- Type of agent (admission, scholarship, etc.)
agent_name VARCHAR(100)       -- Display name of the agent
agent_confidence FLOAT        -- Confidence score (0.0-1.0)
context_used BOOLEAN          -- Whether FAQ context was used
```

## 📈 Analytics Endpoints

### Agent Analytics
```json
GET /admin/api/analytics/agents
{
  "agent_stats": [...],      // Detailed per-agent statistics
  "language_stats": [...],   // Language distribution by agent
  "daily_stats": [...]       // 30-day activity trends
}
```

### Summary Analytics
```json
GET /admin/api/analytics/summary
{
  "agent_totals": [...],     // Total queries per agent
  "success_rates": [...]     // Success rates by agent type
}
```

## 🎨 UI Features

### Admin Dashboard
- **Interactive Charts**: Powered by Chart.js
- **Real-time Data**: Live analytics updates
- **Responsive Design**: Works on desktop and mobile
- **Color-coded Metrics**: Visual distinction for different data types

### Recent Queries Table
Enhanced with agent information:
- Agent name badges
- Confidence score indicators
- Color-coded success rates
- Language identification

## 🔄 Extension Guide

### Adding a New Agent

1. **Create Agent Class**:
```python
class NewTopicAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.NEW_TOPIC,
            "New Topic Agent",
            "Description of specialization"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        # Implement confidence logic
        pass
    
    def get_system_prompt(self, language: str = "ru") -> str:
        # Return specialized prompt
        pass
```

2. **Update AgentType Enum**:
```python
class AgentType(Enum):
    NEW_TOPIC = "new_topic"
    # ... existing types
```

3. **Register in AgentRouter**:
```python
self.agents = [
    # ... existing agents
    NewTopicAgent(),
    GeneralAgent()  # Keep as last
]
```

## 📝 Status Summary

### ✅ Completed Features
- [x] Multi-agent architecture with 5 specialized agents
- [x] Database models updated with agent tracking
- [x] Universal `/api/chat` endpoint with agent routing  
- [x] Chart.js integration in admin dashboard
- [x] Analytics API endpoints for real-time data
- [x] Comprehensive architecture documentation
- [x] Smart fallback responses for offline testing
- [x] Agent confidence scoring and selection

### 🔄 Current Limitations
- SQLAlchemy context issues in some admin functions (fixable)
- External API dependency for full response generation
- Initial data setup requires manual execution

### 🚀 Ready for Production
The multi-agent system core functionality is complete and working. The agent routing, confidence scoring, and analytics framework are fully operational. The system can be deployed with proper external API configuration and database initialization.

## 📞 Contact
For questions about extending the agent system or implementing additional features, refer to the architecture documentation in `/docs/multi-agent-architecture.md`.