import pandas as pd
import json
from typing import Dict, List, Any
from utils.logger import logger_instance as logger
from analytics.duckdb_engine import duckdb_analytics
from analytics.data_validator import data_validator

class ExcelProcessor:
    """
    Process Excel data for keyword research and ad optimization.
    Uses DuckDB for high-performance analytics and Great Expectations for validation.
    """
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        self.duckdb = duckdb_analytics
        self.validator = data_validator
    
    def read_excel(self, file_path: str) -> pd.DataFrame:
        """Read Excel or CSV file"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return pd.DataFrame()
    
    def validate_and_load(self, file_path: str) -> Dict[str, Any]:
        """
        Validate data quality and load into DuckDB.
        Returns validation report and load status.
        """
        try:
            # Read data
            df = self.read_excel(file_path)
            if df.empty:
                return {"success": False, "error": "Empty dataframe"}
            
            # Validate data
            is_valid, validation_results = self.validator.validate_dataframe(df)
            validation_report = self.validator.get_validation_report()
            
            # Load into DuckDB if validation passes
            if validation_report["overall_status"] == "PASS":
                if file_path.endswith('.csv'):
                    self.duckdb.load_data_from_csv(file_path)
                else:
                    self.duckdb.load_data_from_excel(file_path)
                
                return {
                    "success": True,
                    "validation": validation_report,
                    "rows_loaded": len(df)
                }
            else:
                return {
                    "success": False,
                    "validation": validation_report,
                    "error": "Data validation failed"
                }
        
        except Exception as e:
            logger.error(f"Error in validate_and_load: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_keywords(self) -> Dict[str, Any]:
        """
        Analyze keyword data using DuckDB high-performance queries.
        """
        try:
            analysis = {
                "summary": self.duckdb.get_summary_stats(),
                "top_performers": self.duckdb.get_top_performers(10),
                "low_performers": self.duckdb.get_low_performers(10),
                "optimization_opportunities": self.duckdb.find_optimization_opportunities(),
                "roi_metrics": self.duckdb.calculate_roi_metrics()
            }
            
            logger.info("Keyword analysis complete using DuckDB")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing keywords: {str(e)}")
            return {}
    
    def generate_predictions(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate advanced predictions using DuckDB statistical functions.
        """
        try:
            predictions = self.duckdb.predict_performance(days)
            
            # Add additional insights
            predictions["insights"] = self._generate_prediction_insights(predictions)
            
            logger.info(f"Generated {days}-day predictions")
            return predictions
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            return {"predictions": [], "error": str(e)}
    
    def _generate_prediction_insights(self, predictions: Dict) -> List[str]:
        """Generate human-readable insights from predictions"""
        insights = []
        
        if predictions.get("predictions"):
            first_day = predictions["predictions"][0]
            last_day = predictions["predictions"][-1]
            
            # Growth insights
            click_growth = ((last_day["clicks"] - first_day["clicks"]) / first_day["clicks"]) * 100
            insights.append(f"Expected {click_growth:.1f}% growth in clicks over {len(predictions['predictions'])} days")
            
            # Cost insights
            total_cost = predictions.get("total_predicted_cost", 0)
            insights.append(f"Predicted total spend: ${total_cost:,.2f}")
            
            # ROI insights
            avg_roi = sum(p.get("predicted_roi", 0) for p in predictions["predictions"]) / len(predictions["predictions"])
            if avg_roi > 100:
                insights.append(f"Strong ROI predicted: {avg_roi:.1f}% average")
            elif avg_roi > 0:
                insights.append(f"Positive ROI predicted: {avg_roi:.1f}% average")
            else:
                insights.append(f"Warning: Negative ROI predicted: {avg_roi:.1f}%")
            
            # Conversion insights
            total_conversions = predictions.get("total_predicted_conversions", 0)
            insights.append(f"Expected {total_conversions} total conversions")
        
        return insights
    
    def format_for_agent(self, analysis: Dict, predictions: Dict) -> str:
        """Format analysis and predictions for agent prompt"""
        summary = analysis.get("summary", {})
        roi = analysis.get("roi_metrics", {})
        opportunities = analysis.get("optimization_opportunities", {})
        
        prompt = f"""
# 🎯 Advanced Keyword Research & Ad Campaign Analysis
## Powered by DuckDB High-Performance Analytics

## 📊 CURRENT PERFORMANCE METRICS
- Total Keywords Analyzed: {summary.get('total_keywords', 0)}
- Total Impressions: {summary.get('total_impressions', 0):,}
- Total Clicks: {summary.get('total_clicks', 0):,}
- Total Spend: ${summary.get('total_cost', 0):,.2f}
- Total Conversions: {summary.get('total_conversions', 0)}
- Average CTR: {summary.get('avg_ctr', 0):.2f}%
- Average CPC: ${summary.get('avg_cpc', 0):.2f}
- Average Conversion Rate: {summary.get('avg_conversion_rate', 0):.2f}%
- Overall Cost Per Conversion: ${summary.get('overall_cost_per_conversion', 0):.2f}

## 💰 ROI & PROFITABILITY ANALYSIS
- Total Revenue (Estimated): ${roi.get('estimated_revenue', 0):,.2f}
- Total Profit: ${roi.get('profit', 0):,.2f}
- ROI Percentage: {roi.get('roi_percentage', 0):.2f}%
- Break-Even Conversions Needed: {roi.get('break_even_conversions', 0)}
- Campaign Efficiency Score: {roi.get('efficiency_score', 0):.1f}/100

## 🏆 TOP 5 PERFORMING KEYWORDS
{json.dumps(analysis.get('top_performers', [])[:5], indent=2)}

## ⚠️ OPTIMIZATION OPPORTUNITIES

### 💸 High Cost, Low Conversion (PAUSE THESE)
{json.dumps(opportunities.get('high_cost_low_conversion', []), indent=2)}

### 👁️ High Impressions, Low Clicks (IMPROVE AD COPY)
{json.dumps(opportunities.get('high_impressions_low_clicks', []), indent=2)}

### 🎯 High Clicks, Low Conversions (IMPROVE LANDING PAGE)
{json.dumps(opportunities.get('high_clicks_low_conversions', []), indent=2)}

### 💵 BUDGET SAVERS (Zero Conversions, High Cost)
{json.dumps(opportunities.get('budget_savers', []), indent=2)}

## 📈 7-DAY PERFORMANCE PREDICTIONS
### Statistical Analysis with {predictions.get('confidence_level', 0)*100}% Confidence

**Prediction Method:** {predictions.get('method', 'N/A')}

**Total Predicted Metrics:**
- Clicks: {predictions.get('total_predicted_clicks', 0):,}
- Cost: ${predictions.get('total_predicted_cost', 0):,.2f}
- Conversions: {predictions.get('total_predicted_conversions', 0)}

**Day-by-Day Forecast:**
{json.dumps(predictions.get('predictions', []), indent=2)}

**Key Insights:**
{chr(10).join('- ' + insight for insight in predictions.get('insights', []))}

## 🎯 YOUR TASK
Based on this comprehensive data analysis, provide:

1. **💡 EXECUTIVE SUMMARY**
   - Overall campaign health score (0-100)
   - 3 key takeaways

2. **💰 MONEY-SAVING STRATEGIES**
   - Immediate actions to reduce waste
   - Keywords to pause (with estimated savings)
   - Budget reallocation recommendations
   - Expected monthly savings: $X,XXX

3. **🚀 GROWTH OPPORTUNITIES**
   - Keywords to scale up
   - New keyword suggestions based on top performers
   - Bid adjustment recommendations

4. **📊 OPTIMIZATION ROADMAP**
   - Week 1 actions
   - Week 2-4 actions
   - Expected results timeline

5. **⚡ QUICK WINS** (Implement Today)
   - 3 actions that will show immediate results

Format your response with clear sections, bullet points, and specific numbers.
"""
        return prompt

# Global instance
excel_processor = ExcelProcessor()

