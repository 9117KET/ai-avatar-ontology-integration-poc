"""
Command-line interface for running the hallucination evaluation.

This script provides a user-friendly interface to run the evaluation
with different options and parameters.
"""

import argparse
import logging
import os
import sys
from evaluation.models.hallucination_evaluator import HallucinationEvaluator
from evaluation.utils.logging_setup import setup_logging
from evaluation.config.settings import OUTPUT_DIR

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Run hallucination evaluation for the AI Physics Tutor"
    )
    
    parser.add_argument(
        "--fci-data", 
        default="fci_questions.json",
        help="Path to the FCI questions JSON file"
    )
    
    parser.add_argument(
        "--output-dir", 
        default="./results",
        help="Directory to save evaluation results"
    )
    
    parser.add_argument(
        "--questions", 
        type=int,
        help="Number of questions to evaluate (default: all)"
    )
    
    parser.add_argument(
        "--models", 
        choices=["baseline", "ontology", "both"],
        default="both",
        help="Which models to evaluate"
    )
    
    parser.add_argument(
        "--disable-deployed-api",
        action="store_true",
        help="Disable the deployed API and only use simulated ontology (default: deployed API is used with fallback)"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging()
    logger_runner = logging.getLogger("run_evaluation")
    
    # Create output directory if it doesn't exist and set as environment variable
    if args.output_dir != "./results":
        os.environ["OUTPUT_DIR"] = args.output_dir
    
    os.makedirs(os.environ.get("OUTPUT_DIR", OUTPUT_DIR), exist_ok=True)
    logger_runner.info(f"Output directory: {os.environ.get('OUTPUT_DIR', OUTPUT_DIR)}")
    
    # Validate FCI data file
    if not os.path.exists(args.fci_data):
        logger_runner.error(f"FCI data file not found: {args.fci_data}")
        sys.exit(1)
    
    try:
        # Initialize evaluator
        logger_runner.info("Initializing hallucination evaluator...")
        evaluator = HallucinationEvaluator(
            fci_data_path=args.fci_data,
            use_deployed_api=not args.disable_deployed_api
        )
        
        # Limit questions if specified
        if args.questions:
            evaluator.fci_questions = evaluator.fci_questions[:args.questions]
            logger_runner.info(f"Limited evaluation to {args.questions} questions")
        
        # Run evaluation
        logger_runner.info("Running evaluation...")
        results_df, analysis = evaluator.run_full_evaluation()
        
        # Print summary
        if analysis:
            print("\n=== EVALUATION SUMMARY ===")
            
            model_types = ["baseline", "ontology"]
            if args.models != "both":
                model_types = [args.models]
            
            for model_type in model_types:
                if model_type in analysis['metrics']['accuracy']:
                    print(f"\n{model_type.upper()} MODEL:")
                    print(f"  Hallucination rate: {analysis['metrics']['hallucination_rate'][model_type]:.2f}")
                    print(f"  Accuracy: {analysis['metrics']['accuracy'][model_type]:.2f}")
                    print(f"  Avg. hallucinations per response: {analysis['metrics']['avg_hallucinations'][model_type]:.2f}")
            
            if 'statistical_tests' in analysis and len(model_types) > 1:
                print("\nSTATISTICAL ANALYSIS:")
                p_value = analysis['statistical_tests'].get('p_value')
                if p_value:
                    significance = "Significant" if p_value < 0.05 else "Not significant"
                    print(f"  Difference in hallucination rates: {significance} (p={p_value:.4f})")
                
                effect_size = analysis['statistical_tests'].get('effect_size')
                if effect_size:
                    effect_description = "Large" if abs(effect_size) > 0.8 else "Medium" if abs(effect_size) > 0.5 else "Small"
                    print(f"  Effect size: {effect_description} (Cohen's d={effect_size:.2f})")
            
            exemplary_cases = analysis.get('exemplary_cases', [])
            if exemplary_cases:
                print(f"\nFound {len(exemplary_cases)} cases where ontology prevented hallucinations")
                
            print(f"\nDetailed results saved to {os.environ.get('OUTPUT_DIR', OUTPUT_DIR)}/")
            
        logger_runner.info("Evaluation completed successfully")
        
    except Exception as e:
        logger_runner.error(f"Error running evaluation: {e}")
        import traceback
        logger_runner.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
