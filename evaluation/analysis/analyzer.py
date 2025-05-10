"""
Analysis controller for hallucination evaluation results.

This module provides the main class for analyzing evaluation results
and generating reports.
"""

import os
import json
import logging
import pandas as pd
from evaluation.analysis.statistics import calculate_metrics, perform_statistical_tests, find_exemplary_cases
from evaluation.analysis.visualization import generate_comparison_charts
from evaluation.config.settings import OUTPUT_DIR

logger = logging.getLogger("hallucination_evaluator")

class ResultsAnalyzer:
    """Controller for analyzing and reporting evaluation results."""
    
    def __init__(self, fci_questions):
        """
        Initialize the analyzer with FCI questions data.
        
        Args:
            fci_questions: List of FCI question data
        """
        self.fci_questions = fci_questions
    
    def analyze_results(self, results_df):
        """
        Analyze results and generate statistics and visualizations.
        
        Args:
            results_df: DataFrame with evaluation results
            
        Returns:
            Dictionary with analysis results
        """
        if len(results_df) == 0:
            logger.warning("No results to analyze")
            return None
            
        # Calculate metrics
        metrics = calculate_metrics(results_df)
        
        # Perform statistical tests
        statistical_tests = perform_statistical_tests(results_df)
        
        # Generate visualizations
        generate_comparison_charts(results_df)
        
        # Find exemplary cases for qualitative analysis
        exemplary_cases = find_exemplary_cases(results_df, self.fci_questions)
        
        # Combine all results
        analysis_results = {
            'metrics': metrics,
            'statistical_tests': statistical_tests,
            'exemplary_cases': exemplary_cases
        }
        
        # Save analysis results to JSON
        self._save_analysis_results(analysis_results)
        
        return analysis_results
    
    def _save_analysis_results(self, analysis_results):
        """
        Save analysis results to a JSON file.
        
        Args:
            analysis_results: Dictionary with analysis results
        """
        try:
            # Convert pandas Series to regular dictionaries for JSON serialization
            if 'metrics' in analysis_results:
                metrics = analysis_results['metrics']
                serializable_metrics = {}
                for key, value in metrics.items():
                    serializable_metrics[key] = value.to_dict()
                analysis_results['metrics'] = serializable_metrics
            
            # Save to file
            with open(os.path.join(OUTPUT_DIR, 'evaluation_analysis.json'), 'w') as f:
                json.dump(analysis_results, f, indent=2)
                
            logger.info("Analysis results saved to evaluation_analysis.json")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
