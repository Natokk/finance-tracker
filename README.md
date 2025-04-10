Finance Tracker Pro** 💰📊

A personal finance tracking application with GUI built with Python and Tkinter.

![Finance Tracker Screenshot](screenshot.png) *(Add a screenshot later)*

## **Features** ✨
- Track income and expenses with detailed records
- Set monthly budget limits for spending categories
- Visualize spending patterns with interactive charts
- Dark/light mode toggle for comfortable viewing
- Recurring transaction management
- AI-powered natural language transaction input
- Spending heatmap and sparkline visualizations
- Budget progress tracking with alerts

## **Installation** ⚙️

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Natokk/finance-tracker.git
   cd finance-tracker
   ```

2. **Set up a virtual environment (recommended)**:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate  # On Windows
   source myenv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

## **Usage** 🖥️

1. **Add Transactions**:
   - Manual entry via the Transactions tab
   - Natural language input via "Add via AI" button
   - Set up recurring bills

2. **Manage Budgets**:
   - Set monthly spending limits by category
   - View budget status and remaining amounts

3. **View Analytics**:
   - Dashboard with spending overview
   - Heatmap visualization of spending patterns
   - Recent transaction history

## **File Structure** 📂
```
finance-tracker/
├── app.py               # Main application GUI
├── tracker.py           # Core finance tracking logic
├── visualization.py     # Data visualization functions
├── nlp_queries.py       # AI transaction parsing
├── transactions.json    # Data storage file
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## **Contributing** 🤝
Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## **License** 📜
[MIT](https://choosealicense.com/licenses/mit/)
