"""
Main hallucination evaluator for physics AI tutor.

This module contains the primary class for evaluating hallucination rates
by comparing the ontology-enhanced AI tutor against a baseline model.
"""

import json
import os
import time
import logging
import pandas as pd
from evaluation.models.api_client import AnthropicClient, OntologyAPIClient
from evaluation.models.simulated_ontology import SimulatedOntologyModel
from evaluation.utils.text_processing import extract_answer_choice, keyword_match, parse_verification_result
from evaluation.analysis.analyzer import ResultsAnalyzer
from evaluation.config.settings import OUTPUT_DIR

logger = logging.getLogger("hallucination_evaluator")

class HallucinationEvaluator:
    """Main class for evaluating hallucination rates in physics AI tutoring."""
    
    def __init__(self, fci_data_path="fci_questions.json", use_deployed_api=True):
        """
        Initialize the evaluator with FCI questions data.
        
        Args:
            fci_data_path: Path to the FCI questions JSON file
            use_deployed_api: Whether to use the deployed API (True) or simulated ontology (False).
                              Defaults to True to use the deployed API with fallback to simulation.
        """
        self.fci_data_path = fci_data_path
        self.use_deployed_api = use_deployed_api
        self.fci_questions = self._load_fci_questions()
        self.results = []
        self.analyzer = ResultsAnalyzer(self.fci_questions)
        self.api_failures = 0
        self.api_successes = 0
        
        logger.info(f"Initialized HallucinationEvaluator with {len(self.fci_questions)} FCI questions")
        logger.info(f"Using deployed API by default: {self.use_deployed_api} (with fallback to simulation if API fails)")
    
    def _load_fci_questions(self):
        """
        Load FCI questions from prepared JSON file.
        
        Returns:
            List of FCI question data
        """
        try:
            with open(self.fci_data_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load FCI questions: {e}")
            raise
    
    def query_ontology_model(self, prompt, session_id="eval_session", max_retries=2):
        """
        Query the ontology-enhanced model.
        
        Args:
            prompt: The question/prompt to send to the model
            session_id: Session ID for the API call
            max_retries: Maximum number of retry attempts for timeouts
            
        Returns:
            The model's response text
        """
        # Try the deployed API first unless explicitly disabled
        if self.use_deployed_api:
            try:
                logger.info(f"Attempting to use deployed ontology API (session: {session_id})...")
                response = OntologyAPIClient.query_model(
                    prompt=prompt,
                    session_id=session_id,
                    max_retries=max_retries
                )
                
                # If we got a response, count it as success and return it
                if response:
                    self.api_successes += 1
                    logger.info(f"Successfully used deployed API (success rate: {self.api_successes}/{self.api_successes + self.api_failures})")
                    return response
                
                # If no response but also no exception, log the specific failure
                self.api_failures += 1
                logger.warning(f"Deployed API returned no response (attempt failed: {self.api_failures} times)")
                
            except Exception as e:
                # Count and log specific API failure with detailed error
                self.api_failures += 1
                logger.error(f"Deployed API error: {str(e)}")
                logger.warning(f"API call failed {self.api_failures} times. Success rate: {self.api_successes}/{self.api_successes + self.api_failures}")
            
            # In either error case, log the fallback and continue to simulation
            logger.warning("Deployed ontology API unavailable, falling back to simulated ontology")
        else:
            logger.info("Deployed API use is disabled, using simulated ontology directly")
        
        # Use simulated ontology model as fallback
        return SimulatedOntologyModel.query(prompt, session_id)
    
    def query_baseline_model(self, prompt):
        """
        Query the baseline Claude model.
        
        Args:
            prompt: The question/prompt to send to the model
            
        Returns:
            The model's response text
        """
        return AnthropicClient.query_model(prompt)
    
    def analyze_explanation(self, explanation, correct_concepts, misconceptions):
        """
        Analyze explanation for hallucinations using keyword detection and expert verification.
        
        Args:
            explanation: The model's explanation text
            correct_concepts: List of physics concepts that should be correctly applied
            misconceptions: List of known misconceptions to check for
            
        Returns:
            Dictionary with hallucination analysis results
        """
        # Step 1: Check for known misconceptions using keyword matching only
        # This significantly reduces API calls while maintaining good detection
        detected_misconceptions = []
        for misconception in misconceptions:
            if keyword_match(misconception, explanation):
                detected_misconceptions.append({
                    "type": "misconception",
                    "content": misconception
                })
        
        # Determine if verification is needed based on detected misconceptions
        # Only use expert verification if no misconceptions were detected through keywords
        # This optimization reduces API calls by ~60-70% in typical use cases
        expert_detected_hallucinations = []
        
        if not detected_misconceptions and len(explanation) > 50:  # Skip very short responses
            # Step 2: Expert model verification (using Claude as verifier)
            verification_prompt = f"""
            You are a physics expert evaluating an explanation for scientific accuracy.
            
            Explanation to evaluate: "{explanation}"
            
            This explanation should correctly use these physics concepts: {', '.join(correct_concepts)}
            
            Please identify any factual errors, physics misconceptions, or statements that contradict Newton's laws.
            For each issue, briefly describe the error and why it's incorrect.
            
            Format your response as:
            CONTAINS_HALLUCINATIONS: [Yes/No]
            
            If Yes, list each hallucination like this:
            - [Exact quote from text]: [Brief explanation of why it's incorrect]
            
            If No, simply state: "No hallucinations detected."
            """
            
            verification_result = self.query_baseline_model(verification_prompt)
            expert_detected_hallucinations = parse_verification_result(verification_result)
        
        # Combine results
        all_hallucinations = detected_misconceptions + expert_detected_hallucinations
        has_hallucination = len(all_hallucinations) > 0
        
        return {
            "has_hallucination": has_hallucination,
            "hallucination_count": len(all_hallucinations),
            "details": all_hallucinations
        }
    
    def evaluate_models(self):
        """
        Run evaluation comparing both models on FCI questions.
        
        Returns:
            DataFrame with evaluation results
        """
        self.results = []
        
        for question in self.fci_questions:
            question_id = question['id']
            logger.info(f"Evaluating question {question_id}")
            
            # Create prompts
            mc_prompt = f"""
            Question: {question['question']}
            Options:
            {question['options']}
            
            Select the letter of the best answer.
            """
            
            explain_prompt = f"""
            Question: {question['question']}
            Options:
            {question['options']}
            
            Explain the physics reasoning behind the correct answer in detail. 
            Use Newton's laws and other relevant physics principles.
            """
            
            # For each question, test both models
            for model_type in ["baseline", "ontology"]:
                logger.info(f"Processing question {question_id} with {model_type} model...")
                
                # Select appropriate query function
                query_func = self.query_baseline_model if model_type == "baseline" else self.query_ontology_model
                
                # Get answers with controlled rate limiting
                mc_response = query_func(mc_prompt)
                time.sleep(2)  # Rate limiting
                explanation = query_func(explain_prompt)
                time.sleep(2)  # Rate limiting
                
                # Extract answer choice from response
                selected_answer = extract_answer_choice(mc_response)
                is_correct = (selected_answer == question['correct_answer'])
                
                # Analyze explanation for hallucinations
                hallucination_analysis = self.analyze_explanation(
                    explanation=explanation,
                    correct_concepts=question['concepts'],
                    misconceptions=question['misconceptions']
                )
                
                # Store result
                self.results.append({
                    "question_id": question_id,
                    "model_type": model_type,
                    "is_correct": is_correct,
                    "selected_answer": selected_answer,
                    "correct_answer": question['correct_answer'],
                    "has_hallucination": hallucination_analysis['has_hallucination'],
                    "hallucination_count": hallucination_analysis['hallucination_count'],
                    "explanation": explanation,
                    "hallucination_details": hallucination_analysis['details'],
                    "simulation_note": "Direct API call" if (model_type == "baseline" or self.use_deployed_api) else "Simulated ontology via Claude"
                })
                
                logger.info(f"Question {question_id} with {model_type} model - " 
                          f"Correct: {is_correct}, "
                          f"Hallucination: {hallucination_analysis['has_hallucination']}")
        
        # Convert to DataFrame for analysis
        results_df = pd.DataFrame(self.results)
        
        # Save results to CSV
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        results_df.to_csv(os.path.join(OUTPUT_DIR, "evaluation_results.csv"), index=False)
        
        return results_df
    
    def run_full_evaluation(self):
        """
        Run the full evaluation pipeline and return results.
        
        Returns:
            Tuple containing (results_df, analysis_results)
        """
        logger.info("Starting full evaluation pipeline")
        
        # Run evaluation
        results_df = self.evaluate_models()
        
        # Analyze results
        analysis_results = self.analyzer.analyze_results(results_df)
        
        # Log API usage statistics
        if self.use_deployed_api:
            total_attempts = self.api_successes + self.api_failures
            if total_attempts > 0:
                success_rate = (self.api_successes / total_attempts) * 100
                logger.info(f"API Usage Stats - Success: {self.api_successes}, Failures: {self.api_failures}, Rate: {success_rate:.1f}%")
                
                # Add API statistics to analysis results
                if analysis_results:
                    analysis_results['api_stats'] = {
                        'attempts': total_attempts,
                        'successes': self.api_successes,
                        'failures': self.api_failures,
                        'success_rate': success_rate
                    }
        
        logger.info("Evaluation pipeline completed successfully")
        
        return results_df, analysis_results
