import pandas as pd
from typing import Dict, List, Any, Tuple
from utils.logger import logger_instance as logger
import json

class DataValidator:
    """
    Data validation using Great Expectations principles.
    Ensures data quality before analysis.
    """
    
    def __init__(self):
        self.required_columns = ['keyword', 'impressions', 'clicks', 'cost', 'conversions']
        self.validation_results = []
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """
        Validate DataFrame against expectations.
        Returns (is_valid, validation_results)
        """
        self.validation_results = []
        is_valid = True
        
        # Expectation 1: Required columns exist
        if not self._expect_columns_exist(df):
            is_valid = False
        
        # Expectation 2: No null values in critical columns
        if not self._expect_no_nulls(df):
            is_valid = False
        
        # Expectation 3: Numeric columns are non-negative
        if not self._expect_non_negative_values(df):
            is_valid = False
        
        # Expectation 4: Logical relationships hold
        if not self._expect_logical_relationships(df):
            is_valid = False
        
        # Expectation 5: Data types are correct
        if not self._expect_correct_dtypes(df):
            is_valid = False
        
        # Expectation 6: Reasonable value ranges
        if not self._expect_reasonable_ranges(df):
            is_valid = False
        
        logger.info(f"Data validation complete. Valid: {is_valid}")
        return is_valid, self.validation_results
    
    def _expect_columns_exist(self, df: pd.DataFrame) -> bool:
        """Expect all required columns to exist"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            self.validation_results.append({
                "expectation": "columns_exist",
                "success": False,
                "message": f"Missing required columns: {missing_columns}",
                "severity": "critical"
            })
            return False
        
        self.validation_results.append({
            "expectation": "columns_exist",
            "success": True,
            "message": "All required columns present"
        })
        return True
    
    def _expect_no_nulls(self, df: pd.DataFrame) -> bool:
        """Expect no null values in critical columns"""
        null_counts = df[self.required_columns].isnull().sum()
        has_nulls = null_counts.sum() > 0
        
        if has_nulls:
            null_info = {col: int(count) for col, count in null_counts.items() if count > 0}
            self.validation_results.append({
                "expectation": "no_null_values",
                "success": False,
                "message": f"Found null values: {null_info}",
                "severity": "high"
            })
            return False
        
        self.validation_results.append({
            "expectation": "no_null_values",
            "success": True,
            "message": "No null values found"
        })
        return True
    
    def _expect_non_negative_values(self, df: pd.DataFrame) -> bool:
        """Expect numeric columns to be non-negative"""
        numeric_cols = ['impressions', 'clicks', 'cost', 'conversions']
        negative_found = False
        
        for col in numeric_cols:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    negative_found = True
                    self.validation_results.append({
                        "expectation": "non_negative_values",
                        "success": False,
                        "message": f"Found {negative_count} negative values in {col}",
                        "severity": "high"
                    })
        
        if not negative_found:
            self.validation_results.append({
                "expectation": "non_negative_values",
                "success": True,
                "message": "All numeric values are non-negative"
            })
        
        return not negative_found
    
    def _expect_logical_relationships(self, df: pd.DataFrame) -> bool:
        """Expect logical relationships to hold (e.g., clicks <= impressions)"""
        issues = []
        
        # Clicks should not exceed impressions
        if 'clicks' in df.columns and 'impressions' in df.columns:
            invalid_ctr = (df['clicks'] > df['impressions']).sum()
            if invalid_ctr > 0:
                issues.append(f"{invalid_ctr} rows where clicks > impressions")
        
        # Conversions should not exceed clicks
        if 'conversions' in df.columns and 'clicks' in df.columns:
            invalid_conv = (df['conversions'] > df['clicks']).sum()
            if invalid_conv > 0:
                issues.append(f"{invalid_conv} rows where conversions > clicks")
        
        # Cost should be positive if there are clicks
        if 'cost' in df.columns and 'clicks' in df.columns:
            invalid_cost = ((df['clicks'] > 0) & (df['cost'] == 0)).sum()
            if invalid_cost > 0:
                issues.append(f"{invalid_cost} rows with clicks but zero cost (warning)")
        
        if issues:
            self.validation_results.append({
                "expectation": "logical_relationships",
                "success": False,
                "message": f"Logical issues found: {'; '.join(issues)}",
                "severity": "medium"
            })
            return False
        
        self.validation_results.append({
            "expectation": "logical_relationships",
            "success": True,
            "message": "All logical relationships valid"
        })
        return True
    
    def _expect_correct_dtypes(self, df: pd.DataFrame) -> bool:
        """Expect correct data types"""
        dtype_issues = []
        
        numeric_cols = ['impressions', 'clicks', 'cost', 'conversions']
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    dtype_issues.append(f"{col} is not numeric")
        
        if 'keyword' in df.columns:
            if not pd.api.types.is_string_dtype(df['keyword']) and not pd.api.types.is_object_dtype(df['keyword']):
                dtype_issues.append("keyword is not string type")
        
        if dtype_issues:
            self.validation_results.append({
                "expectation": "correct_dtypes",
                "success": False,
                "message": f"Data type issues: {'; '.join(dtype_issues)}",
                "severity": "high"
            })
            return False
        
        self.validation_results.append({
            "expectation": "correct_dtypes",
            "success": True,
            "message": "All data types correct"
        })
        return True
    
    def _expect_reasonable_ranges(self, df: pd.DataFrame) -> bool:
        """Expect values to be in reasonable ranges"""
        warnings = []
        
        # Check for extremely high values (potential data errors)
        if 'impressions' in df.columns:
            max_impressions = df['impressions'].max()
            if max_impressions > 10000000:  # 10M impressions
                warnings.append(f"Very high impressions detected: {max_impressions}")
        
        if 'cost' in df.columns:
            max_cost = df['cost'].max()
            if max_cost > 100000:  # $100k per keyword
                warnings.append(f"Very high cost detected: ${max_cost}")
        
        # Check for suspiciously low CTR
        if 'clicks' in df.columns and 'impressions' in df.columns:
            df_temp = df[df['impressions'] > 0].copy()
            df_temp['ctr'] = (df_temp['clicks'] / df_temp['impressions']) * 100
            low_ctr_count = (df_temp['ctr'] < 0.1).sum()
            if low_ctr_count > len(df) * 0.5:  # More than 50% have very low CTR
                warnings.append(f"{low_ctr_count} keywords with CTR < 0.1%")
        
        if warnings:
            self.validation_results.append({
                "expectation": "reasonable_ranges",
                "success": True,  # Warnings, not failures
                "message": f"Warnings: {'; '.join(warnings)}",
                "severity": "low"
            })
        else:
            self.validation_results.append({
                "expectation": "reasonable_ranges",
                "success": True,
                "message": "All values in reasonable ranges"
            })
        
        return True
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get formatted validation report"""
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results if r["success"])
        
        critical_failures = [r for r in self.validation_results if not r["success"] and r.get("severity") == "critical"]
        high_failures = [r for r in self.validation_results if not r["success"] and r.get("severity") == "high"]
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0,
            "critical_failures": len(critical_failures),
            "high_failures": len(high_failures),
            "details": self.validation_results,
            "overall_status": "PASS" if len(critical_failures) == 0 and len(high_failures) == 0 else "FAIL"
        }

# Global instance
data_validator = DataValidator()
