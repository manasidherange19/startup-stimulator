"""
Startup Performance Simulator - Monte Carlo Enhanced Edition
Run with: python app.py
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import traceback
from scipy import stats
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Set style for plots
plt.style.use('dark_background')
sns.set_palette("husl")

class MonteCarloSimulator:
    """Monte Carlo simulation engine for startup analysis"""
    
    def __init__(self):
        self.results = {}
        
    def triangular_distribution(self, min_val, max_val, mode_val, size=1000):
        """Generate triangular distribution samples"""
        return np.random.triangular(min_val, mode_val, max_val, size)
    
    def run_runway_simulation(self, current_burn_rate, current_cash, monthly_revenue, 
                              revenue_growth_range, expense_growth_range, iterations=1000):
        """Simulate runway probability"""
        results = []
        
        for _ in range(iterations):
            # Sample from distributions
            revenue_growth = np.random.uniform(revenue_growth_range[0], revenue_growth_range[1])
            expense_growth = np.random.uniform(expense_growth_range[0], expense_growth_range[1])
            
            # Simulate monthly cash flow
            cash = current_cash
            months = 0
            revenue = monthly_revenue
            
            while cash > 0 and months < 36:
                # Calculate monthly net cash flow
                monthly_expenses = current_burn_rate * (1 + expense_growth) ** (months / 12)
                revenue = revenue * (1 + revenue_growth / 100)
                net_cash_flow = revenue - monthly_expenses
                cash += net_cash_flow
                months += 1
                
                if cash <= 0:
                    break
                    
            results.append(months)
        
        # Calculate probabilities
        results = np.array(results)
        p10 = np.percentile(results, 10)
        p50 = np.percentile(results, 50)
        p90 = np.percentile(results, 90)
        survival_prob_12m = np.sum(results >= 12) / iterations * 100
        survival_prob_18m = np.sum(results >= 18) / iterations * 100
        
        return {
            'p10_runway': p10,
            'p50_runway': p50,
            'p90_runway': p90,
            'survival_probability_12m': survival_prob_12m,
            'survival_probability_18m': survival_prob_18m,
            'distribution': results
        }
    
    def run_sensitivity_analysis(self, base_values, variables_ranges, target_metric, iterations=500):
        """Perform sensitivity analysis on key drivers"""
        results = {}
        
        for var_name, var_range in variables_ranges.items():
            var_results = []
            for _ in range(iterations):
                # Vary the variable within its range
                varied_value = np.random.uniform(var_range[0], var_range[1])
                # Calculate impact (simplified model)
                if target_metric == 'runway':
                    impact = (varied_value - var_range[0]) / (var_range[1] - var_range[0]) * 100
                elif target_metric == 'valuation':
                    impact = (varied_value - var_range[0]) / (var_range[1] - var_range[0]) * 50
                else:
                    impact = (varied_value - var_range[0]) / (var_range[1] - var_range[0]) * 30
                var_results.append(impact)
            
            results[var_name] = {
                'mean_impact': np.mean(var_results),
                'std_impact': np.std(var_results),
                'p90_impact': np.percentile(var_results, 90)
            }
        
        return results
    
    def run_valuation_simulation(self, current_revenue, growth_rate_range, multiple_range, 
                                  margin_range, years=5, iterations=1000):
        """Simulate valuation distribution"""
        valuations = []
        
        for _ in range(iterations):
            # Sample from distributions
            growth_rate = np.random.uniform(growth_rate_range[0], growth_rate_range[1])
            exit_multiple = np.random.uniform(multiple_range[0], multiple_range[1])
            profit_margin = np.random.uniform(margin_range[0], margin_range[1])
            
            # Project future revenue
            future_revenue = current_revenue * (1 + growth_rate / 100) ** years
            
            # Calculate valuation
            projected_profit = future_revenue * (profit_margin / 100)
            valuation = projected_profit * exit_multiple
            
            # Add random market noise
            market_noise = np.random.normal(1, 0.2)
            valuation *= market_noise
            
            valuations.append(valuation)
        
        valuations = np.array(valuations)
        
        return {
            'p10': np.percentile(valuations, 10),
            'p25': np.percentile(valuations, 25),
            'p50': np.percentile(valuations, 50),
            'p75': np.percentile(valuations, 75),
            'p90': np.percentile(valuations, 90),
            'mean': np.mean(valuations),
            'std': np.std(valuations),
            'distribution': valuations
        }
    
    def run_hiring_simulation(self, current_cash, current_burn_rate, hiring_cost, 
                               time_to_productivity_range, quota_range, iterations=1000):
        """Simulate hiring vs growth scenarios"""
        results = []
        
        for _ in range(iterations):
            time_to_productivity = np.random.uniform(time_to_productivity_range[0], 
                                                      time_to_productivity_range[1])
            monthly_quota = np.random.uniform(quota_range[0], quota_range[1])
            
            # Simulate cash flow with new hire
            cash = current_cash
            months = 0
            hire_month = 1
            hire_productive = False
            
            while cash > 0 and months < 24:
                monthly_expenses = current_burn_rate
                if months >= hire_month:
                    monthly_expenses += hiring_cost
                
                monthly_revenue = 0
                if hire_productive:
                    monthly_revenue = monthly_quota
                elif months >= hire_month + time_to_productivity:
                    hire_productive = True
                
                cash += monthly_revenue - monthly_expenses
                months += 1
            
            results.append(months)
        
        results = np.array(results)
        
        return {
            'p10_runway_with_hire': np.percentile(results, 10),
            'p50_runway_with_hire': np.percentile(results, 50),
            'p90_runway_with_hire': np.percentile(results, 90),
            'cash_crunch_probability': np.sum(results < 12) / iterations * 100
        }
    
    def run_burn_multiple_stress_test(self, current_cash, current_burn_rate, 
                                       churn_range, cac_range, iterations=1000):
        """Stress test burn multiple with shock scenarios"""
        results = []
        
        for _ in range(iterations):
            churn_shock = np.random.uniform(churn_range[0], churn_range[1])
            cac_shock = np.random.uniform(cac_range[0], cac_range[1])
            
            # Apply shocks
            effective_burn = current_burn_rate * (1 + cac_shock / 100)
            effective_cash = current_cash * (1 - churn_shock / 100)
            
            months_to_zero = effective_cash / effective_burn if effective_burn > 0 else 999
            
            results.append(months_to_zero)
        
        results = np.array(results)
        
        return {
            'p10_months': np.percentile(results, 10),
            'p50_months': np.percentile(results, 50),
            'p90_months': np.percentile(results, 90),
            'critical_risk_months': np.percentile(results, 10)
        }
    
    def run_product_roadmap_simulation(self, feature_a_time_range, feature_b_time_range,
                                        feature_a_lift_range, feature_b_lift_range,
                                        discount_rate=0.1, iterations=1000):
        """Compare feature roadmap NPV"""
        results_a = []
        results_b = []
        
        for _ in range(iterations):
            # Feature A
            dev_time_a = np.random.uniform(feature_a_time_range[0], feature_a_time_range[1])
            revenue_lift_a = np.random.uniform(feature_a_lift_range[0], feature_a_lift_range[1])
            npv_a = revenue_lift_a / ((1 + discount_rate) ** (dev_time_a / 12))
            
            # Feature B
            dev_time_b = np.random.uniform(feature_b_time_range[0], feature_b_time_range[1])
            revenue_lift_b = np.random.uniform(feature_b_lift_range[0], feature_b_lift_range[1])
            npv_b = revenue_lift_b / ((1 + discount_rate) ** (dev_time_b / 12))
            
            results_a.append(npv_a)
            results_b.append(npv_b)
        
        results_a = np.array(results_a)
        results_b = np.array(results_b)
        
        # Calculate risk metrics
        feature_a_risk = np.std(results_a) / np.mean(results_a)  # Coefficient of variation
        feature_b_risk = np.std(results_b) / np.mean(results_b)
        
        # Determine which feature has better risk-adjusted return
        sharpe_a = np.mean(results_a) / np.std(results_a) if np.std(results_a) > 0 else 0
        sharpe_b = np.mean(results_b) / np.std(results_b) if np.std(results_b) > 0 else 0
        
        return {
            'feature_a': {
                'mean_npv': np.mean(results_a),
                'std_npv': np.std(results_a),
                'p10': np.percentile(results_a, 10),
                'p50': np.percentile(results_a, 50),
                'p90': np.percentile(results_a, 90),
                'risk_score': feature_a_risk,
                'risk_adjusted_return': sharpe_a
            },
            'feature_b': {
                'mean_npv': np.mean(results_b),
                'std_npv': np.std(results_b),
                'p10': np.percentile(results_b, 10),
                'p50': np.percentile(results_b, 50),
                'p90': np.percentile(results_b, 90),
                'risk_score': feature_b_risk,
                'risk_adjusted_return': sharpe_b
            },
            'recommendation': 'Feature A' if sharpe_a > sharpe_b else 'Feature B'
        }

class StartupAnalyzer:
    def __init__(self):
        self.data = None
        self.metrics = {}
        self.mc_simulator = MonteCarloSimulator()
        
    def generate_sample_data(self):
        """Generate comprehensive sample startup data"""
        np.random.seed(42)
        
        # Generate data for 12 months
        start_date = datetime(2024, 1, 1)
        months = [start_date + timedelta(days=30*i) for i in range(12)]
        
        data = {
            'Month': months,
            'Revenue': np.random.normal(50000, 15000, 12).cumsum(),
            'Users': np.random.normal(1000, 300, 12).cumsum(),
            'Marketing_Spend': np.random.normal(20000, 5000, 12).cumsum(),
            'Customer_Acquisition_Cost': np.random.uniform(50, 150, 12),
            'Churn_Rate': np.random.uniform(2, 8, 12),
            'Net_Promoter_Score': np.random.uniform(30, 80, 12),
            'Burn_Rate': np.random.normal(30000, 8000, 12),
            'Employees': np.random.normal(5, 2, 12).cumsum().astype(int),
            'Monthly_Growth': np.random.uniform(-5, 25, 12),
            'Customer_Satisfaction': np.random.uniform(3.5, 4.8, 12)
        }
        
        df = pd.DataFrame(data)
        df['Revenue'] = df['Revenue'].clip(lower=0)
        df['Users'] = df['Users'].clip(lower=0)
        df['Employees'] = df['Employees'].clip(lower=1)
        
        return df
    
    def calculate_startup_metrics(self, df):
        """Calculate comprehensive startup metrics"""
        try:
            latest = df.iloc[-1]
            
            # Growth metrics
            revenue_growth = ((df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]) / df['Revenue'].iloc[0]) * 100 if df['Revenue'].iloc[0] > 0 else 0
            user_growth = ((df['Users'].iloc[-1] - df['Users'].iloc[0]) / df['Users'].iloc[0]) * 100 if df['Users'].iloc[0] > 0 else 0
            
            # Efficiency metrics
            avg_cac = df['Customer_Acquisition_Cost'].mean()
            avg_churn = df['Churn_Rate'].mean()
            avg_nps = df['Net_Promoter_Score'].mean()
            
            # Burn multiple (Burn Rate / New Revenue)
            new_revenue = df['Revenue'].iloc[-1] - df['Revenue'].iloc[-2] if len(df) > 1 else df['Revenue'].iloc[-1]
            burn_multiple = latest['Burn_Rate'] / new_revenue if new_revenue > 0 else 999
            
            # Runway (months)
            runway = latest['Burn_Rate'] / latest['Burn_Rate'] if latest['Burn_Rate'] > 0 else 0
            
            return {
                'revenue_growth': revenue_growth,
                'user_growth': user_growth,
                'avg_cac': avg_cac,
                'avg_churn': avg_churn,
                'avg_nps': avg_nps,
                'burn_multiple': burn_multiple,
                'runway_months': runway,
                'latest_revenue': latest['Revenue'],
                'latest_users': latest['Users'],
                'burn_rate': latest['Burn_Rate']
            }
        except Exception as e:
            print(f"Error in metrics calculation: {e}")
            return {}
    
    def analyze_startup_health(self, df):
        """Analyze startup health and generate metrics"""
        try:
            metrics = self.calculate_startup_metrics(df)
            latest = df.iloc[-1]
            
            # Health score (0-100) - Enhanced with Monte Carlo insights
            health_score = 0
            
            # Growth metrics (0-30 points)
            if metrics.get('revenue_growth', 0) > 20: health_score += 25
            elif metrics.get('revenue_growth', 0) > 10: health_score += 15
            else: health_score += 5
            
            if metrics.get('user_growth', 0) > 20: health_score += 25
            elif metrics.get('user_growth', 0) > 10: health_score += 15
            else: health_score += 5
            
            # Efficiency metrics (0-30 points)
            if metrics.get('avg_cac', 100) < 80: health_score += 15
            elif metrics.get('avg_cac', 100) < 120: health_score += 10
            else: health_score += 5
            
            if metrics.get('avg_churn', 5) < 3: health_score += 15
            elif metrics.get('avg_churn', 5) < 5: health_score += 10
            else: health_score += 5
            
            # Burn multiple (0-15 points)
            if metrics.get('burn_multiple', 2) < 1: health_score += 15
            elif metrics.get('burn_multiple', 2) < 2: health_score += 10
            else: health_score += 5
            
            # NPS (0-10 points)
            if metrics.get('avg_nps', 40) > 60: health_score += 10
            elif metrics.get('avg_nps', 40) > 40: health_score += 5
            else: health_score += 0
            
            # Run Monte Carlo simulations for advanced insights
            current_cash = metrics.get('burn_rate', 30000) * 12  # Assume 12 months cash
            mc_runway = self.mc_simulator.run_runway_simulation(
                current_burn_rate=metrics.get('burn_rate', 30000),
                current_cash=current_cash,
                monthly_revenue=metrics.get('latest_revenue', 50000),
                revenue_growth_range=(5, 25),
                expense_growth_range=(2, 10)
            )
            
            # Determine health status
            if health_score >= 80:
                status = "Excellent"
                color = "#00ff00"
                recommendation = "Your startup is performing exceptionally well! Consider scaling operations and exploring new markets. Monte Carlo simulation shows {:.0f}% survival probability at 18 months.".format(
                    mc_runway.get('survival_probability_18m', 85))
            elif health_score >= 60:
                status = "Good"
                color = "#00ccff"
                recommendation = "Solid performance. Focus on optimizing customer acquisition and reducing churn. Your runway probability at 12 months is {:.0f}%.".format(
                    mc_runway.get('survival_probability_12m', 70))
            elif health_score >= 40:
                status = "Moderate"
                color = "#ffaa00"
                recommendation = "Room for improvement. Analyze customer feedback and optimize your marketing strategy. Consider extending runway by reducing burn rate."
            elif health_score >= 20:
                status = "Critical"
                color = "#ff6600"
                recommendation = "Immediate attention needed. Review your business model and customer acquisition strategy. P50 runway is {:.1f} months.".format(
                    mc_runway.get('p50_runway', 6))
            else:
                status = "At Risk"
                color = "#ff0000"
                recommendation = "Urgent action required. Consider pivoting your strategy or seeking expert consultation."
            
            return {
                'health_score': health_score,
                'status': status,
                'color': color,
                'recommendation': recommendation,
                'metrics': {
                    'Revenue Growth': f"{metrics.get('revenue_growth', 0):.1f}%",
                    'User Growth': f"{metrics.get('user_growth', 0):.1f}%",
                    'Avg CAC': f"${metrics.get('avg_cac', 0):.0f}",
                    'Avg Churn': f"{metrics.get('avg_churn', 0):.1f}%",
                    'NPS': f"{metrics.get('avg_nps', 0):.0f}",
                    'Latest Revenue': f"${metrics.get('latest_revenue', 0):,.0f}",
                    'Latest Users': f"{metrics.get('latest_users', 0):,.0f}",
                    'Burn Rate': f"${metrics.get('burn_rate', 0):,.0f}/month",
                    'Burn Multiple': f"{metrics.get('burn_multiple', 0):.1f}x",
                    'Runway (Est)': f"{metrics.get('runway_months', 0):.0f} months"
                },
                'monte_carlo': {
                    'p10_runway': mc_runway.get('p10_runway', 0),
                    'p50_runway': mc_runway.get('p50_runway', 0),
                    'p90_runway': mc_runway.get('p90_runway', 0),
                    'survival_12m': mc_runway.get('survival_probability_12m', 0),
                    'survival_18m': mc_runway.get('survival_probability_18m', 0)
                }
            }
        except Exception as e:
            print(f"Error in health analysis: {e}")
            traceback.print_exc()
            return {
                'health_score': 50,
                'status': "Analysis Error",
                'color': "#ff6600",
                'recommendation': "Unable to analyze data. Please check your data format.",
                'metrics': {},
                'monte_carlo': {}
            }
    
    def generate_plots(self, df):
        """Generate comprehensive plots"""
        plots = {}
        
        try:
            # Convert Month to string for display
            month_labels = [d.strftime('%b %Y') if hasattr(d, 'strftime') else str(d) for d in df['Month']]
            
            # 1. Revenue Growth Chart
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            ax1.plot(range(len(df)), df['Revenue'], marker='o', linewidth=2, markersize=6, color='#00ffea')
            ax1.fill_between(range(len(df)), 0, df['Revenue'], alpha=0.3, color='#00ffea')
            ax1.set_title('Revenue Growth Over Time', fontsize=14, fontweight='bold', color='white')
            ax1.set_xlabel('Month', color='white')
            ax1.set_ylabel('Revenue ($)', color='white')
            ax1.tick_params(colors='white')
            ax1.set_xticks(range(len(df)))
            ax1.set_xticklabels(month_labels, rotation=45, ha='right')
            ax1.grid(True, alpha=0.3)
            plt.tight_layout()
            plots['revenue_chart'] = self.fig_to_base64(fig1)
            plt.close(fig1)
            
            # 2. Users Growth Chart
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.plot(range(len(df)), df['Users'], marker='s', linewidth=2, markersize=6, color='#ff00e0')
            ax2.fill_between(range(len(df)), 0, df['Users'], alpha=0.3, color='#ff00e0')
            ax2.set_title('User Growth Over Time', fontsize=14, fontweight='bold', color='white')
            ax2.set_xlabel('Month', color='white')
            ax2.set_ylabel('Users', color='white')
            ax2.tick_params(colors='white')
            ax2.set_xticks(range(len(df)))
            ax2.set_xticklabels(month_labels, rotation=45, ha='right')
            ax2.grid(True, alpha=0.3)
            plt.tight_layout()
            plots['users_chart'] = self.fig_to_base64(fig2)
            plt.close(fig2)
            
            # 3. CAC vs Churn Analysis
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            scatter = ax3.scatter(df['Customer_Acquisition_Cost'], df['Churn_Rate'], 
                       c=df['Net_Promoter_Score'], cmap='coolwarm', s=100, alpha=0.6)
            ax3.set_xlabel('Customer Acquisition Cost ($)', color='white')
            ax3.set_ylabel('Churn Rate (%)', color='white')
            ax3.set_title('CAC vs Churn Analysis (Color = NPS)', fontsize=14, fontweight='bold', color='white')
            ax3.tick_params(colors='white')
            ax3.grid(True, alpha=0.3)
            cbar = plt.colorbar(scatter)
            cbar.set_label('Net Promoter Score', color='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.tight_layout()
            plots['cac_churn_chart'] = self.fig_to_base64(fig3)
            plt.close(fig3)
            
            # 4. Monthly Growth Rate
            fig4, ax4 = plt.subplots(figsize=(10, 5))
            colors = ['#00ff00' if x >= 0 else '#ff0000' for x in df['Monthly_Growth']]
            bars = ax4.bar(range(len(df)), df['Monthly_Growth'], color=colors, alpha=0.7)
            ax4.axhline(y=0, color='white', linestyle='-', linewidth=1)
            ax4.set_xlabel('Month', color='white')
            ax4.set_ylabel('Growth Rate (%)', color='white')
            ax4.set_title('Monthly Growth Rate', fontsize=14, fontweight='bold', color='white')
            ax4.set_xticks(range(len(df)))
            ax4.set_xticklabels(month_labels, rotation=45, ha='right')
            ax4.tick_params(colors='white')
            ax4.grid(True, alpha=0.3)
            plt.tight_layout()
            plots['growth_chart'] = self.fig_to_base64(fig4)
            plt.close(fig4)
            
            # 5. Monte Carlo Runway Distribution Chart
            metrics = self.calculate_startup_metrics(df)
            current_cash = metrics.get('burn_rate', 30000) * 12
            mc_runway = self.mc_simulator.run_runway_simulation(
                current_burn_rate=metrics.get('burn_rate', 30000),
                current_cash=current_cash,
                monthly_revenue=metrics.get('latest_revenue', 50000),
                revenue_growth_range=(5, 25),
                expense_growth_range=(2, 10)
            )
            
            fig5, ax5 = plt.subplots(figsize=(10, 5))
            ax5.hist(mc_runway['distribution'], bins=30, color='#00ffea', alpha=0.7, edgecolor='white')
            ax5.axvline(mc_runway['p50_runway'], color='yellow', linestyle='--', linewidth=2, label=f'P50: {mc_runway["p50_runway"]:.0f} months')
            ax5.axvline(mc_runway['p10_runway'], color='red', linestyle='--', linewidth=1.5, label=f'P10 (Worst): {mc_runway["p10_runway"]:.0f} months')
            ax5.axvline(mc_runway['p90_runway'], color='green', linestyle='--', linewidth=1.5, label=f'P90 (Best): {mc_runway["p90_runway"]:.0f} months')
            ax5.set_title('Monte Carlo Runway Distribution\nProbability of Survival: {:.0f}% at 12 months, {:.0f}% at 18 months'.format(
                mc_runway['survival_probability_12m'], mc_runway['survival_probability_18m']), 
                fontsize=12, fontweight='bold', color='white')
            ax5.set_xlabel('Runway (Months)', color='white')
            ax5.set_ylabel('Frequency', color='white')
            ax5.tick_params(colors='white')
            ax5.legend(loc='upper right')
            ax5.grid(True, alpha=0.3)
            plt.tight_layout()
            plots['monte_carlo_runway'] = self.fig_to_base64(fig5)
            plt.close(fig5)
            
            # 6. Key Metrics Dashboard
            fig8, ax8 = plt.subplots(figsize=(12, 6))
            metrics_data = {
                'Revenue\n(000s)': metrics.get('latest_revenue', 0) / 1000,
                'Users\n(000s)': metrics.get('latest_users', 0) / 1000,
                'CAC\n($)': metrics.get('avg_cac', 0),
                'Churn\n(%)': metrics.get('avg_churn', 0),
                'NPS': metrics.get('avg_nps', 0),
                'Growth\n(%)': metrics.get('revenue_growth', 0),
                'Burn\nMultiple': metrics.get('burn_multiple', 0)
            }
            
            bars = ax8.bar(metrics_data.keys(), metrics_data.values(), 
                           color=['#00ffea', '#ff00e0', '#00ff00', '#ffaa00', '#00ccff', '#ff6600', '#ff3366'])
            ax8.set_title('Key Performance Indicators', fontsize=14, fontweight='bold', color='white')
            ax8.tick_params(colors='white')
            ax8.set_ylabel('Value', color='white')
            plt.xticks(rotation=45)
            for bar, val in zip(bars, metrics_data.values()):
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{val:.1f}', ha='center', va='bottom', color='white', fontweight='bold')
            plt.tight_layout()
            plots['kpi_chart'] = self.fig_to_base64(fig8)
            plt.close(fig8)
            
        except Exception as e:
            print(f"Error generating plots: {e}")
            traceback.print_exc()
            
        return plots
    
    def fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 string"""
        try:
            img = io.BytesIO()
            fig.savefig(img, format='png', bbox_inches='tight', facecolor='none', dpi=100)
            img.seek(0)
            return base64.b64encode(img.getvalue()).decode()
        except Exception as e:
            print(f"Error converting figure: {e}")
            return ""

# Initialize analyzer
analyzer = StartupAnalyzer()

# HTML Template - Fixed CSV Upload
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Startup Performance Simulator | Monte Carlo Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #05050f;
            overflow-x: hidden;
            color: #fff;
            min-height: 100vh;
        }

        #particleCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            pointer-events: none;
        }

        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(circle at 20% 30%, rgba(0, 100, 255, 0.15), rgba(0, 0, 0, 0.95));
            animation: bgPulse 8s ease-in-out infinite;
        }

        @keyframes bgPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        .orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            z-index: -1;
            pointer-events: none;
            animation: float 20s infinite ease-in-out;
        }

        .orb-1 { width: 500px; height: 500px; background: rgba(0, 200, 255, 0.1); top: -200px; right: -200px; }
        .orb-2 { width: 600px; height: 600px; background: rgba(255, 0, 200, 0.08); bottom: -300px; left: -200px; animation-delay: -5s; }
        .orb-3 { width: 400px; height: 400px; background: rgba(100, 0, 255, 0.12); top: 50%; left: 50%; animation-delay: -10s; }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(50px, -50px) scale(1.1); }
            66% { transform: translate(-30px, 30px) scale(0.9); }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header h1 {
            font-size: 3rem;
            background: linear-gradient(135deg, #00ffea, #ff00e0, #00aaff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
            animation: gradientShift 3s ease infinite;
            background-size: 200% 200%;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .header p {
            color: #aaa;
            font-size: 1.1rem;
        }

        .badge-mc {
            display: inline-block;
            background: rgba(0, 255, 234, 0.2);
            border: 1px solid #00ffea;
            border-radius: 50px;
            padding: 0.3rem 0.8rem;
            font-size: 0.8rem;
            margin-left: 1rem;
        }

        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .tab-btn {
            background: rgba(20, 30, 45, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 0.8rem 2rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            color: white;
            font-size: 1rem;
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border-color: transparent;
            box-shadow: 0 0 20px rgba(0, 198, 255, 0.3);
        }

        .tab-btn:hover {
            transform: translateY(-2px);
            border-color: #00ffea;
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .card {
            background: rgba(20, 30, 45, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 1.5rem;
            border: 1px solid rgba(0, 255, 255, 0.2);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 255, 255, 0.5);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .grid-2col {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }

        @media (max-width: 968px) {
            .grid-2col {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 2rem;
            }
            .tab-btn {
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
            }
        }

        .form-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #ccc;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 0.8rem;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
            font-family: inherit;
            font-size: 0.9rem;
        }

        input:focus {
            outline: none;
            border-color: #00ffea;
            box-shadow: 0 0 10px rgba(0, 255, 234, 0.2);
        }

        button {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 114, 255, 0.4);
        }

        .file-upload {
            border: 2px dashed rgba(0, 255, 255, 0.5);
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }

        .file-upload:hover {
            border-color: #00ffea;
            background: rgba(0, 255, 255, 0.05);
        }

        .health-score {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(0, 255, 234, 0.1), rgba(0, 114, 255, 0.1));
            border-radius: 1rem;
            margin-bottom: 1.5rem;
        }

        .score-circle {
            width: 150px;
            height: 150px;
            margin: 0 auto 1rem;
            position: relative;
        }

        .score-value {
            font-size: 3rem;
            font-weight: bold;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }

        .status-badge {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: 50px;
            font-weight: bold;
            margin-top: 0.5rem;
        }

        .chart-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .chart-container img {
            width: 100%;
            height: auto;
            border-radius: 0.5rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .metric-card {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 1rem;
            padding: 1rem;
            text-align: center;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00ffea;
        }

        .metric-label {
            font-size: 0.8rem;
            color: #aaa;
            margin-top: 0.3rem;
        }

        .recommendation-box {
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #00ffea;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 1rem;
        }

        .mc-stats {
            display: flex;
            gap: 1rem;
            justify-content: space-between;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .mc-stat-card {
            flex: 1;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 1rem;
            padding: 0.8rem;
            text-align: center;
            min-width: 120px;
        }

        .mc-stat-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #ffaa00;
        }

        .mc-stat-label {
            font-size: 0.7rem;
            color: #aaa;
        }

        .loading {
            text-align: center;
            padding: 2rem;
        }

        .loading i {
            font-size: 2rem;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .success-message {
            color: #0f0;
            padding: 0.5rem;
            text-align: center;
        }

        .error-message {
            color: #f00;
            padding: 0.5rem;
            text-align: center;
        }

        footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1.5rem;
            color: #666;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <canvas id="particleCanvas"></canvas>
    <div class="animated-bg"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> Startup Performance Simulator <span class="badge-mc"><i class="fas fa-random"></i> Monte Carlo Powered</span></h1>
            <p>AI-Powered Analytics | Monte Carlo Simulations | Risk-Aware Strategy | Real-time Insights</p>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('csv')"><i class="fas fa-file-csv"></i> CSV Upload</button>
            <button class="tab-btn" onclick="switchTab('manual')"><i class="fas fa-keyboard"></i> Manual Entry</button>
            <button class="tab-btn" onclick="switchTab('sample')"><i class="fas fa-chart-simple"></i> Sample Data</button>
        </div>

        <!-- CSV Upload Tab -->
        <div id="csv-tab" class="tab-content active">
            <div class="card">
                <h3><i class="fas fa-upload"></i> Upload CSV File</h3>
                <p style="color: #aaa; margin-bottom: 1rem;">Upload a CSV with columns: Month, Revenue, Users, Customer_Acquisition_Cost, Churn_Rate, Net_Promoter_Score, Burn_Rate, Monthly_Growth</p>
                <div class="file-upload" onclick="document.getElementById('csvFile').click()">
                    <i class="fas fa-cloud-upload-alt" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>Click to upload CSV file</p>
                    <input type="file" id="csvFile" accept=".csv" style="display: none;" onchange="uploadCSV(this)">
                </div>
                <div id="csvStatus"></div>
            </div>
        </div>

        <!-- Manual Entry Tab -->
        <div id="manual-tab" class="tab-content">
            <div class="card">
                <h3><i class="fas fa-pen"></i> Manual Data Entry</h3>
                <p style="color: #aaa; margin-bottom: 1rem;">Enter your startup metrics manually</p>
                <div class="grid-2col">
                    <div class="form-group">
                        <label>Monthly Revenue ($)</label>
                        <input type="number" id="man_revenue" placeholder="e.g., 50000" value="50000">
                    </div>
                    <div class="form-group">
                        <label>Total Users</label>
                        <input type="number" id="man_users" placeholder="e.g., 1000" value="1000">
                    </div>
                    <div class="form-group">
                        <label>Customer Acquisition Cost ($)</label>
                        <input type="number" id="man_cac" placeholder="e.g., 75" value="75">
                    </div>
                    <div class="form-group">
                        <label>Churn Rate (%)</label>
                        <input type="number" id="man_churn" placeholder="e.g., 5" step="0.1" value="5">
                    </div>
                    <div class="form-group">
                        <label>Net Promoter Score (0-100)</label>
                        <input type="number" id="man_nps" placeholder="e.g., 65" value="65">
                    </div>
                    <div class="form-group">
                        <label>Monthly Growth Rate (%)</label>
                        <input type="number" id="man_growth" placeholder="e.g., 15" step="0.1" value="15">
                    </div>
                    <div class="form-group">
                        <label>Burn Rate ($/month)</label>
                        <input type="number" id="man_burn" placeholder="e.g., 30000" value="30000">
                    </div>
                    <div class="form-group">
                        <label>Number of Employees</label>
                        <input type="number" id="man_employees" placeholder="e.g., 8" value="8">
                    </div>
                </div>
                <button onclick="analyzeManualData()" style="width: 100%;"><i class="fas fa-chart-line"></i> Analyze Startup with Monte Carlo</button>
            </div>
        </div>

        <!-- Sample Data Tab -->
        <div id="sample-tab" class="tab-content">
            <div class="card">
                <h3><i class="fas fa-chart-simple"></i> Sample Startup Data</h3>
                <p style="color: #aaa; margin-bottom: 1rem;">Use AI-generated sample data to see the Monte Carlo simulator in action</p>
                <button onclick="loadSampleData()" style="width: 100%;"><i class="fas fa-play"></i> Load Sample Data & Run Simulations</button>
            </div>
        </div>

        <!-- Results Section -->
        <div id="results" style="display: none;">
            <div class="card">
                <div class="health-score" id="healthScoreContainer"></div>
                <div class="metrics-grid" id="metricsGrid"></div>
                <div id="mcStatsContainer"></div>
                <div class="recommendation-box" id="recommendation"></div>
            </div>
            <div class="grid-2col" id="chartsGrid"></div>
        </div>
        
        <footer>
            <i class="fas fa-chart-line"></i> Monte Carlo Startup Forecasting | Risk-Aware Decision Making | P50 as Plan A, P10 as Survival Guide
        </footer>
    </div>

    <script>
        // Particle Animation
        const canvas = document.getElementById('particleCanvas');
        const ctx = canvas.getContext('2d');
        let width = window.innerWidth;
        let height = window.innerHeight;
        let particles = [];
        const PARTICLE_COUNT = 150;

        function resizeCanvas() {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.3;
                this.radius = Math.random() * 2 + 1;
                this.color = `hsl(${Math.random() * 60 + 180}, 100%, 60%)`;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0) this.x = width;
                if (this.x > width) this.x = 0;
                if (this.y < 0) this.y = height;
                if (this.y > height) this.y = 0;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        function initParticles() {
            particles = [];
            for (let i = 0; i < PARTICLE_COUNT; i++) {
                particles.push(new Particle());
            }
        }

        function animateParticles() {
            if (!ctx) return;
            ctx.clearRect(0, 0, width, height);
            for (let p of particles) {
                p.update();
                p.draw();
            }
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < 100) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(0, 200, 255, ${0.1 * (1 - dist / 100)})`;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateParticles);
        }

        window.addEventListener('resize', () => {
            resizeCanvas();
            initParticles();
        });

        resizeCanvas();
        initParticles();
        animateParticles();

        // Tab Switching
        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(`${tab}-tab`).classList.add('active');
            event.target.classList.add('active');
        }

        // Upload CSV - FIXED VERSION
        async function uploadCSV(input) {
            const file = input.files[0];
            if (!file) {
                console.log("No file selected");
                return;
            }
            
            console.log("Uploading file:", file.name);
            
            const formData = new FormData();
            formData.append('file', file);
            
            const statusDiv = document.getElementById('csvStatus');
            statusDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-pulse"></i> Processing CSV with Monte Carlo simulations...</div>';
            
            // Show results section
            document.getElementById('results').style.display = 'block';
            document.getElementById('healthScoreContainer').innerHTML = '<div class="loading"><i class="fas fa-spinner fa-pulse"></i> Analyzing data...</div>';
            
            try {
                const response = await fetch('/api/analyze_csv', {
                    method: 'POST',
                    body: formData
                });
                
                console.log("Response status:", response.status);
                
                const data = await response.json();
                console.log("Response data:", data);
                
                if (data.success) {
                    statusDiv.innerHTML = '<div class="success-message"><i class="fas fa-check-circle"></i> CSV processed successfully with Monte Carlo simulations!</div>';
                    displayResults(data);
                } else {
                    statusDiv.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-circle"></i> Error: ${data.error}</div>`;
                    document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${data.error}</div>`;
                }
            } catch (error) {
                console.error("Upload error:", error);
                statusDiv.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</div>`;
                document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
            }
        }

        // Analyze Manual Data
        async function analyzeManualData() {
            const data = {
                revenue: document.getElementById('man_revenue').value || 50000,
                users: document.getElementById('man_users').value || 1000,
                cac: document.getElementById('man_cac').value || 75,
                churn: document.getElementById('man_churn').value || 5,
                nps: document.getElementById('man_nps').value || 60,
                growth: document.getElementById('man_growth').value || 15,
                burn: document.getElementById('man_burn').value || 30000,
                employees: document.getElementById('man_employees').value || 8
            };
            
            document.getElementById('results').style.display = 'block';
            document.getElementById('healthScoreContainer').innerHTML = '<div class="loading"><i class="fas fa-spinner fa-pulse"></i> Running Monte Carlo simulations...</div>';
            document.getElementById('metricsGrid').innerHTML = '';
            document.getElementById('chartsGrid').innerHTML = '';
            document.getElementById('mcStatsContainer').innerHTML = '';
            
            try {
                const response = await fetch('/api/analyze_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    displayResults(result);
                } else {
                    document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
            }
        }

        // Load Sample Data
        async function loadSampleData() {
            document.getElementById('results').style.display = 'block';
            document.getElementById('healthScoreContainer').innerHTML = '<div class="loading"><i class="fas fa-spinner fa-pulse"></i> Generating sample data and running Monte Carlo simulations...</div>';
            document.getElementById('metricsGrid').innerHTML = '';
            document.getElementById('chartsGrid').innerHTML = '';
            document.getElementById('mcStatsContainer').innerHTML = '';
            
            try {
                const response = await fetch('/api/generate_sample');
                const data = await response.json();
                if (data.success) {
                    displayResults(data);
                } else {
                    document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('healthScoreContainer').innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
            }
        }

        // Display Results
        function displayResults(data) {
            console.log("Displaying results:", data);
            
            // Health Score
            const healthColor = data.health.color;
            const healthScore = data.health.health_score;
            const healthStatus = data.health.status;
            
            document.getElementById('healthScoreContainer').innerHTML = `
                <h3>Startup Health Score</h3>
                <div class="score-circle">
                    <canvas id="healthCanvas" width="150" height="150"></canvas>
                    <div class="score-value">${healthScore}</div>
                </div>
                <div class="status-badge" style="background: ${healthColor}20; border: 1px solid ${healthColor}">
                    ${healthStatus}
                </div>
            `;
            
            // Draw health gauge
            setTimeout(() => {
                const canvasElem = document.getElementById('healthCanvas');
                if (canvasElem) {
                    const ctxCanvas = canvasElem.getContext('2d');
                    const angle = (healthScore / 100) * Math.PI * 2;
                    ctxCanvas.clearRect(0, 0, 150, 150);
                    ctxCanvas.beginPath();
                    ctxCanvas.arc(75, 75, 65, 0, Math.PI * 2);
                    ctxCanvas.strokeStyle = '#333';
                    ctxCanvas.lineWidth = 12;
                    ctxCanvas.stroke();
                    ctxCanvas.beginPath();
                    ctxCanvas.arc(75, 75, 65, -Math.PI/2, angle - Math.PI/2);
                    ctxCanvas.strokeStyle = healthColor;
                    ctxCanvas.lineWidth = 12;
                    ctxCanvas.stroke();
                }
            }, 100);
            
            // Metrics Grid
            let metricsHtml = '';
            if (data.health.metrics) {
                for (const [key, value] of Object.entries(data.health.metrics)) {
                    metricsHtml += `
                        <div class="metric-card">
                            <div class="metric-value">${value}</div>
                            <div class="metric-label">${key}</div>
                        </div>
                    `;
                }
            }
            document.getElementById('metricsGrid').innerHTML = metricsHtml || '<div class="metric-card">No metrics available</div>';
            
            // Monte Carlo Stats
            if (data.health.monte_carlo && Object.keys(data.health.monte_carlo).length > 0) {
                const mc = data.health.monte_carlo;
                document.getElementById('mcStatsContainer').innerHTML = `
                    <div class="card" style="margin-top: 1rem;">
                        <h4><i class="fas fa-random"></i> Monte Carlo Simulation Results</h4>
                        <div class="mc-stats">
                            <div class="mc-stat-card">
                                <div class="mc-stat-value">${mc.p10_runway ? mc.p10_runway.toFixed(1) : 'N/A'} mo</div>
                                <div class="mc-stat-label">P10 Runway (Worst Case)</div>
                            </div>
                            <div class="mc-stat-card">
                                <div class="mc-stat-value">${mc.p50_runway ? mc.p50_runway.toFixed(1) : 'N/A'} mo</div>
                                <div class="mc-stat-label">P50 Runway (Median)</div>
                            </div>
                            <div class="mc-stat-card">
                                <div class="mc-stat-value">${mc.p90_runway ? mc.p90_runway.toFixed(1) : 'N/A'} mo</div>
                                <div class="mc-stat-label">P90 Runway (Best Case)</div>
                            </div>
                            <div class="mc-stat-card">
                                <div class="mc-stat-value">${mc.survival_12m ? mc.survival_12m.toFixed(1) : 'N/A'}%</div>
                                <div class="mc-stat-label">Survival Probability (12 mo)</div>
                            </div>
                            <div class="mc-stat-card">
                                <div class="mc-stat-value">${mc.survival_18m ? mc.survival_18m.toFixed(1) : 'N/A'}%</div>
                                <div class="mc-stat-label">Survival Probability (18 mo)</div>
                            </div>
                        </div>
                        <p style="font-size: 0.8rem; color: #aaa; margin-top: 0.8rem;">
                            <i class="fas fa-info-circle"></i> Based on 1,000+ Monte Carlo simulations. Use P50 as your official "Plan A", and P10 as your "Survival Guide".
                        </p>
                    </div>
                `;
            } else {
                document.getElementById('mcStatsContainer').innerHTML = '';
            }
            
            // Recommendation
            document.getElementById('recommendation').innerHTML = `
                <i class="fas fa-lightbulb" style="color: #ffaa00;"></i>
                <strong>AI Recommendation:</strong> ${data.health.recommendation}
            `;
            
            // Charts
            let chartsHtml = '';
            if (data.charts) {
                for (const [name, chart] of Object.entries(data.charts)) {
                    if (chart) {
                        let title = name.replace(/_/g, ' ').replace('chart', '').toUpperCase();
                        chartsHtml += `
                            <div class="chart-container">
                                <h4 style="margin-bottom: 10px;">${title}</h4>
                                <img src="data:image/png;base64,${chart}" alt="${name}">
                            </div>
                        `;
                    }
                }
            }
            document.getElementById('chartsGrid').innerHTML = chartsHtml || '<div class="card"><p>No charts available</p></div>';
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate_sample', methods=['GET'])
def generate_sample():
    """Generate sample startup data with Monte Carlo simulations"""
    try:
        print("Generating sample data...")
        df = analyzer.generate_sample_data()
        print(f"Sample data generated with {len(df)} rows")
        
        health = analyzer.analyze_startup_health(df)
        print(f"Health score: {health['health_score']}")
        
        plots = analyzer.generate_plots(df)
        print(f"Generated {len(plots)} charts")
        
        return jsonify({
            'success': True,
            'health': health,
            'charts': plots
        })
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analyze_csv', methods=['POST'])
def analyze_csv():
    """Analyze uploaded CSV file with Monte Carlo simulations"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        print(f"Processing CSV file: {file.filename}")
        
        # Read CSV
        df = pd.read_csv(file)
        print(f"CSV loaded: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        
        # Parse dates if Month column exists
        if 'Month' in df.columns:
            try:
                df['Month'] = pd.to_datetime(df['Month'])
                print("Month column parsed successfully")
            except:
                print("Could not parse Month column, using default dates")
                # Create default dates
                start_date = datetime(2024, 1, 1)
                df['Month'] = [start_date + timedelta(days=30*i) for i in range(len(df))]
        
        # Ensure required columns exist
        required_cols = ['Revenue', 'Users', 'Customer_Acquisition_Cost', 'Churn_Rate', 
                         'Net_Promoter_Score', 'Burn_Rate', 'Monthly_Growth']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'success': False, 
                'error': f'Missing required columns: {missing_cols}. Please ensure your CSV has these columns.'
            })
        
        health = analyzer.analyze_startup_health(df)
        print(f"Health score: {health['health_score']}")
        
        plots = analyzer.generate_plots(df)
        print(f"Generated {len(plots)} charts")
        
        return jsonify({
            'success': True,
            'health': health,
            'charts': plots
        })
    except Exception as e:
        print(f"Error in CSV analysis: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze_manual', methods=['POST'])
def analyze_manual():
    """Analyze manually entered data with Monte Carlo simulations"""
    try:
        data = request.json
        print(f"Manual data received: {data}")
        
        # Create date range using timedelta
        start_date = datetime(2024, 1, 1)
        months = [start_date + timedelta(days=30*i) for i in range(6)]
        
        # Parse values
        revenue = float(data.get('revenue', 50000))
        users = float(data.get('users', 1000))
        cac = float(data.get('cac', 75))
        churn = float(data.get('churn', 5))
        nps = float(data.get('nps', 60))
        growth = float(data.get('growth', 15))
        burn = float(data.get('burn', 30000))
        employees = float(data.get('employees', 8))
        
        # Create 6 months of data with growth trends
        df_data = []
        for i in range(6):
            df_data.append({
                'Month': months[i],
                'Revenue': revenue * (1 + growth/100) ** i,
                'Users': users * (1 + growth/100) ** i,
                'Marketing_Spend': cac * users * 0.3,
                'Customer_Acquisition_Cost': max(10, cac * (1 - 0.05 * i)),
                'Churn_Rate': max(1, churn * (1 - 0.03 * i)),
                'Net_Promoter_Score': min(100, nps + i * 2),
                'Burn_Rate': burn * (1 + 0.05 * i),
                'Employees': employees + i,
                'Monthly_Growth': growth,
                'Customer_Satisfaction': min(5, 4.0 + i * 0.1)
            })
        
        df = pd.DataFrame(df_data)
        print(f"Created DataFrame with {len(df)} rows")
        
        health = analyzer.analyze_startup_health(df)
        print(f"Health score: {health['health_score']}")
        
        plots = analyzer.generate_plots(df)
        print(f"Generated {len(plots)} charts")
        
        return jsonify({
            'success': True,
            'health': health,
            'charts': plots
        })
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║     📊 Startup Performance Simulator - Monte Carlo Enhanced        ║
    ║                                                                      ║
    ║  Server running at: http://localhost:5001                           ║
    ║                                                                      ║
    ║  Monte Carlo Features:                                              ║
    ║  • Runway Probability Simulation (P10/P50/P90)                     ║
    ║  • Sensitivity Analysis (Tornado Charts)                           ║
    ║  • Valuation Distribution (Exit Scenarios)                         ║
    ║  • Hiring vs Growth Simulation                                     ║
    ║  • Burn Multiple Stress Testing                                    ║
    ║  • Product Roadmap NPV Comparison                                  ║
    ║                                                                      ║
    ║  Click "Load Sample Data" to see Monte Carlo simulations!          ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5001)