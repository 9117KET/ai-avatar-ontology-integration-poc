"""
Statistical analysis utilities for hallucination evaluation.

This module provides functions for calculating statistical metrics and 
performing hypothesis testing on evaluation results.
"""

import logging
import pandas as pd
import numpy as np
from scipy import stats

logger = logging.getLogger("hallucination_evaluator")

def calculate_metrics(results_df):
    """
    Calculate basic performance metrics for each model.
    
    Args:
        results_df: DataFrame with evaluation results
        
    Returns:
        Dictionary with metrics by model type
    """
    # Make sure boolean columns are converted to integer (0/1) for calculations
    for col in ['is_correct', 'has_hallucination']:
        if col in results_df.columns:
            results_df[col] = results_df[col].astype(int)
    
    # Group by model type
    grouped = results_df.groupby('model_type')
    
    # Calculate metrics
    metrics = {
        'accuracy': grouped['is_correct'].mean(),
        'hallucination_rate': grouped['has_hallucination'].mean(),
        'avg_hallucinations': grouped['hallucination_count'].mean()
    }
    
    return metrics

def perform_statistical_tests(results_df):
    """
    Perform statistical tests to compare baseline and ontology models.
    
    Args:
        results_df: DataFrame with evaluation results
        
    Returns:
        Dictionary with statistical test results
    """
    # Extract hallucination data for both models
    baseline_hallu = results_df[results_df['model_type'] == 'baseline']['has_hallucination']
    ontology_hallu = results_df[results_df['model_type'] == 'ontology']['has_hallucination']
    
    # Calculate statistics if we have enough data
    statistical_tests = {}
    if len(baseline_hallu) > 0 and len(ontology_hallu) > 0:
        try:
            # Paired t-test for hallucination rate if we have matched pairs
            if len(baseline_hallu) == len(ontology_hallu):
                t_stat, p_value = stats.ttest_rel(baseline_hallu, ontology_hallu)
            else:
                t_stat, p_value = stats.ttest_ind(baseline_hallu, ontology_hallu)
                
            # Calculate effect size (Cohen's d)
            # By this point values should already be numeric (0/1) not boolean
            # Safely handle case where there's no variance (e.g., all 0s)
            pooled_std = float(pd.concat([baseline_hallu, ontology_hallu]).std())
            if pooled_std > 0:
                effect_size = (float(baseline_hallu.mean()) - float(ontology_hallu.mean())) / pooled_std
            else:
                # If standard deviation is 0, we can't calculate a meaningful effect size
                # This happens when all values are the same (e.g., all 0s or all 1s)
                if baseline_hallu.mean() == ontology_hallu.mean():
                    effect_size = 0.0  # No effect when means are equal
                else:
                    # If means differ but variance is 0, this indicates a very large effect
                    # Use the sign of the difference to determine direction
                    effect_size = 2.0 * (1.0 if baseline_hallu.mean() > ontology_hallu.mean() else -1.0)
            
            statistical_tests = {
                'p_value': float(p_value),  # Convert to native Python float
                'effect_size': float(effect_size),  # Convert to native Python float
                'is_significant': bool(p_value < 0.05),  # Convert to native Python bool
                't_statistic': float(t_stat)
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            statistical_tests = {
                'error': str(e)
            }
    
    return statistical_tests

def find_exemplary_cases(results_df, fci_questions):
    """
    Find exemplary cases where ontology prevented hallucinations.
    
    Args:
        results_df: DataFrame with evaluation results
        fci_questions: List of FCI question data
        
    Returns:
        List of exemplary cases
    """
    exemplary_cases = []
    
    # Get questions where baseline hallucinated but ontology didn't
    paired_results = results_df.pivot(
        index='question_id', 
        columns='model_type', 
        values=['has_hallucination', 'explanation', 'is_correct']
    )
    
    if len(paired_results) == 0:
        return exemplary_cases
        
    # Find questions where baseline hallucinated but ontology didn't
    for question_id in paired_results.index:
        try:
            baseline_hallucinated = paired_results[('has_hallucination', 'baseline')].loc[question_id]
            ontology_hallucinated = paired_results[('has_hallucination', 'ontology')].loc[question_id]
            
            # Convert to Python booleans to avoid numpy boolean operations
            if bool(baseline_hallucinated) and not bool(ontology_hallucinated):
                # This is an exemplary case
                question_data = next((q for q in fci_questions if q['id'] == question_id), None)
                
                if question_data:
                    exemplary_cases.append({
                        'question_id': question_id,
                        'question': question_data['question'],
                        'baseline_explanation': paired_results[('explanation', 'baseline')].loc[question_id],
                        'ontology_explanation': paired_results[('explanation', 'ontology')].loc[question_id],
                        'concepts': question_data['concepts'],
                        'misconceptions': question_data['misconceptions']
                    })
        except Exception as e:
            logger.warning(f"Error processing exemplary case for question {question_id}: {e}")
    
    return exemplary_cases
