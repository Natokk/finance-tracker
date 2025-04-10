import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def create_spending_heatmap(transactions):
    """Generate color-coded spending intensity map"""
    try:
        df = pd.DataFrame(transactions)
        if df.empty:
            return None
            
        expenses = df[df['type'] == 'expense'].copy()
        if expenses.empty:
            return None
            
        expenses['date'] = pd.to_datetime(expenses['date'])
        daily = expenses.groupby('date')['amount'].sum()
        
        # Create custom color gradient (green -> yellow -> red)
        colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
        cmap = LinearSegmentedColormap.from_list("money", colors)
        
        # Plot setup
        fig, ax = plt.subplots(figsize=(10, 2))
        img = ax.imshow([daily.values], cmap=cmap, aspect='auto',
                       extent=[0, len(daily), 0, 1])
        
        # Add colorbar
        plt.colorbar(img, ax=ax, orientation='horizontal', label='Spending Amount')
        
        # X-axis formatting
        if len(daily) > 0:
            ax.set_xticks(range(len(daily)))
            ax.set_xticklabels([d.strftime('%b %d') for d in daily.index], rotation=45)
        ax.set_yticks([])  # Hide y-axis
        
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"Heatmap generation error: {e}")
        return None

def create_spending_sparkline(transactions):
    """Generate mini spending trend visualization"""
    try:
        df = pd.DataFrame(transactions)
        if df.empty:
            return None
            
        expenses = df[df['type'] == 'expense']
        if expenses.empty:
            return None
            
        expenses['date'] = pd.to_datetime(expenses['date'])
        daily = expenses.groupby('date')['amount'].sum()
        
        fig, ax = plt.subplots(figsize=(4, 1))
        ax.plot(daily.values, color='#e74c3c', linewidth=2)
        ax.fill_between(range(len(daily)), daily.values, color='#e74c3c', alpha=0.2)
        ax.axis('off')
        fig.patch.set_alpha(0)
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"Sparkline generation error: {e}")
        return None