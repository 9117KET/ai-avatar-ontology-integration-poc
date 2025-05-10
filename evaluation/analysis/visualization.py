"""
Data visualization utilities for hallucination evaluation.

This module provides functions for generating charts and visualizations 
to compare model performance.
"""

import os
import logging
import matplotlib.pyplot as plt
from evaluation.config.settings import OUTPUT_DIR

logger = logging.getLogger("hallucination_evaluator")

def generate_comparison_charts(results_df):
    """
    Generate comparison charts for visualization.
    
    Args:
        results_df: DataFrame with evaluation results
    """
    try:
        # Set style (using a built-in matplotlib style)
        plt.style.use('ggplot')  # Alternative styles: 'fivethirtyeight', 'bmh', etc.
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Metrics for comparison
        metrics = {
            'Accuracy': 'is_correct',
            'Hallucination Rate': 'has_hallucination'
        }
        
        # Colors for models
        colors = {
            'baseline': 'skyblue',
            'ontology': 'lightgreen'
        }
        
        # Plot metrics
        for i, (metric_name, metric_col) in enumerate(metrics.items()):
            ax = ax1 if i == 0 else ax2
            
            # Group by model type and calculate mean
            grouped_data = results_df.groupby('model_type')[metric_col].mean()
            
            # Create bar plot
            bars = ax.bar(
                grouped_data.index,
                grouped_data.values,
                color=[colors[model] for model in grouped_data.index],
                alpha=0.7,
                edgecolor='black',
                linewidth=1
            )
            
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.01,
                    f'{height:.2f}',
                    ha='center',
                    va='bottom',
                    fontweight='bold'
                )
            
            # Customize plot
            ax.set_title(f'{metric_name} by Model Type', fontsize=14)
            ax.set_ylim(0, 1.1)
            ax.set_ylabel(metric_name, fontsize=12)
            ax.set_xlabel('Model Type', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to output directory
        plt.savefig(os.path.join(OUTPUT_DIR, 'model_comparison.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Generated comparison charts successfully")
        
    except Exception as e:
        logger.error(f"Error generating comparison charts: {e}")
