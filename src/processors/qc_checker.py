"""Quality control checker for geophysical data."""

import pandas as pd
from typing import Dict, Any, List
import logging
import numpy as np


class QCChecker:
    """Performs quality control checks on geophysical data.
    
    This class runs various quality control checks on parsed data to identify
    potential issues before standardization and output.
    
    Attributes:
        logger: Logger instance for this class.
    
    Example:
        >>> qc = QCChecker()
        >>> result = qc.check(parsed_data)
        >>> if not result['passed']:
        ...     print(result['issues'])
    """
    
    def __init__(self):
        """Initialize the QC checker."""
        self.logger = logging.getLogger(__name__)
    
    def check(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run QC checks on parsed data.
        
        Args:
            parsed_data: Dictionary with 'metadata' and 'data' keys.
        
        Returns:
            Dictionary with QC results:
                - passed: Boolean indicating if all checks passed
                - issues: List of issue descriptions
                - warnings: List of warning messages
                - checks_run: List of check names that were executed
        """
        df = parsed_data['data']
        issues = []
        warnings = []
        checks_run = []
        
        # Check for missing values
        missing_result = self._check_missing_values(df)
        checks_run.append('missing_values')
        if missing_result['has_issues']:
            issues.append(missing_result['message'])
        elif missing_result.get('has_warnings'):
            warnings.append(missing_result['message'])
        
        # Check for duplicates
        duplicate_result = self._check_duplicates(df)
        checks_run.append('duplicates')
        if duplicate_result['has_issues']:
            issues.append(duplicate_result['message'])
        
        # Check for outliers
        outlier_result = self._check_outliers(df)
        checks_run.append('outliers')
        if outlier_result['has_warnings']:
            warnings.append(outlier_result['message'])
        
        # Check data consistency
        consistency_result = self._check_consistency(df)
        checks_run.append('consistency')
        if consistency_result['has_warnings']:
            warnings.append(consistency_result['message'])
        
        passed = len(issues) == 0
        
        result = {
            'passed': passed,
            'issues': issues,
            'warnings': warnings,
            'checks_run': checks_run,
            'summary': {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'issues_found': len(issues),
                'warnings_found': len(warnings),
            }
        }
        
        if passed:
            self.logger.info("All QC checks passed")
        else:
            self.logger.warning(f"QC checks failed with {len(issues)} issues")
        
        return result
    
    def _check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values in data.
        
        Args:
            df: DataFrame to check.
        
        Returns:
            Dictionary with check results.
        """
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]
        
        if len(missing_cols) > 0:
            total_missing = missing_cols.sum()
            total_values = len(df) * len(df.columns)
            missing_pct = (total_missing / total_values) * 100
            
            message = (
                f"Missing values found: {total_missing} ({missing_pct:.2f}%). "
                f"Affected columns: {missing_cols.to_dict()}"
            )
            
            # Determine if it's an issue or warning based on threshold
            if missing_pct > 10:  # More than 10% missing
                return {'has_issues': True, 'message': message}
            else:
                return {'has_issues': False, 'has_warnings': True, 'message': message}
        
        return {'has_issues': False, 'message': 'No missing values found'}
    
    def _check_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for duplicate rows in data.
        
        Args:
            df: DataFrame to check.
        
        Returns:
            Dictionary with check results.
        """
        duplicates = df.duplicated().sum()
        
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            message = (
                f"{duplicates} duplicate rows found ({dup_pct:.2f}% of total)"
            )
            
            # Determine if it's an issue based on threshold
            if dup_pct > 5:  # More than 5% duplicates
                return {'has_issues': True, 'message': message}
            else:
                return {'has_issues': False, 'has_warnings': True, 'message': message}
        
        return {'has_issues': False, 'message': 'No duplicates found'}
    
    def _check_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for outliers in numeric columns using IQR method.
        
        Args:
            df: DataFrame to check.
        
        Returns:
            Dictionary with check results.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_info = {}
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            
            if outliers > 0:
                outlier_pct = (outliers / len(df)) * 100
                outlier_info[col] = {
                    'count': int(outliers),
                    'percentage': round(outlier_pct, 2)
                }
        
        if outlier_info:
            message = f"Outliers detected in columns: {outlier_info}"
            return {'has_warnings': True, 'message': message}
        
        return {'has_warnings': False, 'message': 'No outliers detected'}
    
    def _check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for data consistency issues.
        
        Args:
            df: DataFrame to check.
        
        Returns:
            Dictionary with check results.
        """
        warnings = []
        
        # Check if numeric columns have reasonable variance
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if df[col].std() == 0:
                warnings.append(f"Column '{col}' has zero variance (all values are identical)")
        
        # Check for unexpected data types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if it could be numeric
                try:
                    pd.to_numeric(df[col])
                    warnings.append(f"Column '{col}' is stored as object but appears to be numeric")
                except (ValueError, TypeError):
                    pass
        
        if warnings:
            message = "; ".join(warnings)
            return {'has_warnings': True, 'message': message}
        
        return {'has_warnings': False, 'message': 'No consistency issues found'}
