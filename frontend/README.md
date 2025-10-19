# ORCA Trading Platform Frontend

A comprehensive algorithmic trading platform with real-time market data, automated trading strategies, backtesting capabilities, and data management.

## 🚀 Features

### 🔐 Authentication
- **Supabase Integration** - Secure authentication with email/password
- **Multi-Factor Authentication (MFA)** - Enhanced security with TOTP
- **Multi-Tenancy Support** - User-specific data isolation

### 📊 Dashboard
- **Live Market Prices** - Real-time price updates for:
  - MNQ (Micro E-mini Nasdaq-100)
  - NQ (E-mini Nasdaq-100)
  - ES (E-mini S&P 500)
  - MES (Micro E-mini S&P 500)
  - GC (Gold Futures)
  - MGC (Micro Gold Futures)
- **Active Algorithms Monitor** - Track running trading strategies
- **Account Management** - View all trading accounts and balances

### 🤖 Algorithm Trading
- **9 Point Breakout Strategy** - First-hour breakout algorithm with:
  - Configurable parameters (spacing, orders, stop loss, take profit)
  - Multiple instrument support (ES, NQ, MES, MNQ)
  - Real-time start/stop controls
  - Account selection

### 📈 Backtesting
- **Historical Analysis** - Test strategies with past data
- **Comprehensive Metrics**:
  - Total P&L, Win Rate, Sharpe Ratio
  - Max Drawdown, Profit Factor
  - Average Win/Loss statistics
- **Visual Analytics** - Equity curve charts
- **Trade History** - Detailed trade-by-trade analysis
- **Export Results** - Download backtest reports as CSV

### 📁 Data Management
- **File Upload** - Support for CSV, TXT, and JSON files
- **Drag & Drop Interface** - Easy file upload
- **Data Preview** - View uploaded data before processing
- **Batch Processing** - Handle large datasets efficiently

## 🛠️ Tech Stack

- **Frontend Framework**: React 18 with Vite
- **UI Components**: TailwindCSS + Framer Motion
- **Authentication**: Supabase Auth with MFA
- **State Management**: React Context API
- **Data Visualization**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **Date Handling**: date-fns + react-datepicker

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/saurabhpatilsam/orca_stagnator.git
cd orca-ven-backend-main/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment variables**
Create a `.env` file in the frontend directory:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=your_backend_api_url
```

4. **Start development server**
```bash
npm run dev
```

5. **Build for production**
```bash
npm run build
```

## 🚀 Deployment

### Deploy to Vercel (Recommended)
1. Push your code to GitHub
2. Import project in Vercel dashboard
3. Configure environment variables
4. Deploy

### Deploy to Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build the project
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=dist
```

### Manual Deployment
The built files in `dist/` can be served by any static file hosting service.

## 📱 Application Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx         # Main app layout with sidebar
│   │   ├── Login.jsx          # Authentication component
│   │   ├── Dashboard.jsx      # Main dashboard with live prices
│   │   ├── Algorithm.jsx      # Algorithm trading interface
│   │   ├── Backtesting.jsx    # Backtesting interface
│   │   └── DataUpload.jsx     # Data upload interface
│   ├── contexts/
│   │   └── AuthContext.jsx    # Authentication context provider
│   ├── config/
│   │   └── supabase.js        # Supabase client configuration
│   ├── services/
│   │   └── tradingViewService.js  # TradingView data service
│   ├── App.jsx                # Main app component
│   └── main.jsx               # App entry point
├── public/                    # Static assets
├── dist/                      # Production build output
└── package.json              # Dependencies and scripts
```

## 🔧 Configuration

### Supabase Setup
1. Create a Supabase project
2. Enable email authentication
3. Set up MFA if required
4. Create necessary tables for accounts and algorithms

### Backend Integration
The frontend expects a backend API at the configured URL with endpoints for:
- `/api/algorithms/start` - Start trading algorithm
- `/api/algorithms/stop` - Stop trading algorithm
- `/api/backtest` - Run backtesting
- `/api/accounts` - Get trading accounts

## 🎯 Usage

1. **Sign Up/Login** - Create an account or login with existing credentials
2. **Dashboard** - View live market prices and active algorithms
3. **Algorithm** - Configure and start the 9 Point breakout algorithm
4. **Backtesting** - Test strategies with historical data
5. **Data** - Upload and manage trading data files

## 🔒 Security

- All API keys are stored as environment variables
- Supabase Row Level Security (RLS) for data isolation
- MFA support for enhanced account security
- Secure token management with httpOnly cookies

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the development team.
