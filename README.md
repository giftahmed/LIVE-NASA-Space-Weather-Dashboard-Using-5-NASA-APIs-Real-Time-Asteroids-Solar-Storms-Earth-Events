# 🚀 NASA Space Weather Dashboard

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![NASA APIs](https://img.shields.io/badge/NASA-APIs-0B3D91?style=flat&logo=nasa&logoColor=white)](https://api.nasa.gov)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A real-time, interactive monitoring dashboard for space weather, asteroid tracking, Earth events, and deep space imagery — powered entirely by NASA's public APIs.

![Dashboard Preview](https://raw.githubusercontent.com/giftahmed/LIVE-NASA-Space-Weather-Dashboard-Using-5-NASA-APIs-Real-Time-Asteroids-Solar-Storms-Earth-Events/CometR3_Orion.jpg)

---

## ✨ Features

| Module | API | What It Shows |
|--------|-----|---------------|
| 🌌 **APOD** | [Astronomy Picture of the Day](https://api.nasa.gov/#apod) | Daily space imagery with scientific explanation |
| 🪨 **Asteroid Tracker** | [NeoWs](https://api.nasa.gov/#neo) | Near-Earth objects, hazard assessment, approach timelines |
| 🌞 **Space Weather** | [DONKI](https://api.nasa.gov/#donki) | Solar events: CMEs, geomagnetic storms, solar flares |
| 🌍 **Earth Events** | [EONET](https://eonet.gsfc.nasa.gov/) | Natural disasters mapped globally in real-time |
| 🌎 **EPIC Earth** | [EPIC](https://api.nasa.gov/#epic) | Full-disc Earth images from the DSCOVR satellite |
| 🔴 **Mars Rover** | [Mars Photos](https://api.nasa.gov/#mars-rover-photos) | Browse Curiosity & Perseverance photos by sol |

### Key Capabilities

- 📊 **Interactive Visualizations** — Plotly charts, scatter plots, geo maps, and timelines
- ⚡ **Real-time Data** — Live feeds from 5 NASA APIs with smart caching
- 🎨 **Dark Theme UI** — NASA-inspired styling with responsive layout
- ⚠️ **Hazard Alerts** — Automatic flagging of potentially hazardous asteroids
- 🗺️ **Global Event Mapping** — Plot natural disasters on an interactive world map
- 🔍 **Smart Filtering** — Filter Mars photos by camera, Earth events by category
- 📱 **Mobile Ready** — Works on desktop, tablet, and phone

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A free NASA API key (optional, but recommended) — [get one here](https://api.nasa.gov/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/nasa-space-weather-dashboard.git
cd nasa-space-weather-dashboard

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure your NASA API key
# Option A: Environment variable
export NASA_API_KEY="your_api_key_here"  # Linux/Mac
set NASA_API_KEY=your_api_key_here       # Windows

# Option B: Streamlit secrets
mkdir -p .streamlit
echo 'NASA_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml

# 5. Launch the dashboard
streamlit run nasa_space_weather_dashboard.py
```

The app will open automatically at `http://localhost:8501`

---

## 📁 Project Structure

```
nasa-space-weather-dashboard/
├── nasa_space_weather_dashboard.py   # Main Streamlit application
├── requirements.txt                  # Python dependencies
├── .streamlit/
│   └── secrets.toml                  # API key configuration (gitignored)
├── assets/
│   └── preview.png                   # Dashboard screenshot
├── docs/
│   ├── api_reference.md              # NASA API endpoint documentation
│   └── screenshots/                  # Additional screenshots
├── tests/
│   └── test_api_functions.py         # Unit tests for API wrappers
├── LICENSE                           # MIT License
└── README.md                         # This file
```

---

## 🔑 API Configuration

### Getting an API Key

1. Visit [api.nasa.gov](https://api.nasa.gov/)
2. Fill out the registration form (takes ~30 seconds)
3. Your key will be emailed to you instantly

### Why You Should Use Your Own Key

| Key Type | Rate Limit | Best For |
|----------|-----------|----------|
| `DEMO_KEY` (default) | 30 requests/hour | Quick testing |
| Personal API Key | 1,000 requests/hour | Daily use, development |

The dashboard caches data for 5 minutes to stay well within limits.

---

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black nasa_space_weather_dashboard.py

# Check linting
flake8 nasa_space_weather_dashboard.py
```

### Adding a New API Module

1. Add an API wrapper function in `nasa_space_weather_dashboard.py`
2. Create a `render_*_section()` function for the UI
3. Add a new tab in the `main()` function
4. Update this README with the new module

---

## 🌍 Deployment

### Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your `NASA_API_KEY` in the Secrets manager
5. Deploy!

### Docker

```bash
# Build image
docker build -t nasa-dashboard .

# Run container
docker run -p 8501:8501 -e NASA_API_KEY=your_key nasa-dashboard
```

### Docker Compose

```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NASA_API_KEY=${NASA_API_KEY}
```

---

## 📊 API Reference

### Data Sources

All data is fetched in real-time from NASA's public APIs:

| API | Base URL | Docs |
|-----|----------|------|
| APOD | `api.nasa.gov/planetary/apod` | [Docs](https://api.nasa.gov/#apod) |
| NeoWs | `api.nasa.gov/neo/rest/v1` | [Docs](https://api.nasa.gov/#neo) |
| DONKI | `api.nasa.gov/DONKI` | [Docs](https://api.nasa.gov/#donki) |
| EONET | `eonet.gsfc.nasa.gov/api/v3` | [Docs](https://eonet.gsfc.nasa.gov/docs/v3) |
| EPIC | `api.nasa.gov/EPIC/api` | [Docs](https://api.nasa.gov/#epic) |
| Mars Photos | `api.nasa.gov/mars-photos/api/v1` | [Docs](https://api.nasa.gov/#mars-rover-photos) |

### Caching Strategy

All API calls are cached for **5 minutes** using Streamlit's `@st.cache_data` decorator to:
- Respect NASA's rate limits
- Improve dashboard responsiveness
- Reduce unnecessary network traffic

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Contributions

- [ ] Add **TechPort** technology project browser
- [ ] Add **TechTransfer** patent search
- [ ] Implement **email alerts** for close asteroid approaches
- [ ] Add **historical data** charts and trends
- [ ] Create **export to PDF** functionality
- [ ] Add **dark/light theme toggle**
- [ ] Build **REST API wrapper** for headless usage
- [ ] Add **unit tests** for all API functions
- [ ] Create **Docker** deployment setup
- [ ] Add **CI/CD** with GitHub Actions

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

NASA imagery and data are public domain courtesy of the U.S. government. This project is not affiliated with or endorsed by NASA.

---

## 🙏 Acknowledgments

- [NASA Open APIs](https://api.nasa.gov/) — for making incredible space data freely available
- [Streamlit](https://streamlit.io/) — for the amazing Python app framework
- [Plotly](https://plotly.com/) — for beautiful interactive visualizations
- The entire space science community — for exploring the cosmos and sharing what you find

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/nasa-space-weather-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nasa-space-weather-dashboard/discussions)
- **Email**: your.email@example.com

---

<p align="center">
  <img src="https://api.nasa.gov/assets/img/favicons/favicon-192.png" width="60" alt="NASA Logo">
  <br>
  <em>"We choose to go to the moon in this decade and do the other things, not because they are easy, but because they are hard."</em>
  <br>
  — John F. Kennedy
</p>
