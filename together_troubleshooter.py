#!/usr/bin/env python3
"""
Together AI Inference Troubleshooting Tool

A comprehensive tool to diagnose common issues with Together AI's inference services
including rate limits, API errors, model availability, and performance issues.
"""

import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import logging
import os
import asyncio
import aiohttp
from functools import wraps
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class DiagnosticResult:
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING", "INFO"
    message: str
    details: Dict = None
    recommendation: str = ""


def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60, backoff_factor=2):
    """Decorator for retrying functions with exponential backoff and jitter"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {total_delay:.2f}s")
                    time.sleep(total_delay)
            
            raise last_exception
        return wrapper
    return decorator


class RobustHTTPClient:
    """HTTP client with retry logic, connection pooling, and circuit breaker"""
    
    def __init__(self, timeout=30, max_retries=3):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.timeout = timeout
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False
    
    def _check_circuit_breaker(self):
        """Check if circuit breaker should be opened/closed"""
        if self.circuit_open:
            if time.time() - self.last_failure_time > self.circuit_breaker_timeout:
                self.circuit_open = False
                self.failure_count = 0
                logging.info("Circuit breaker closed - resuming requests")
            else:
                raise Exception("Circuit breaker is open - too many recent failures")
    
    def request(self, method, url, **kwargs):
        """Make HTTP request with circuit breaker protection"""
        self._check_circuit_breaker()
        
        try:
            kwargs.setdefault('timeout', self.timeout)
            response = self.session.request(method, url, **kwargs)
            
            # Reset failure count on success
            if response.status_code < 500:
                self.failure_count = 0
            
            return response
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.circuit_breaker_threshold:
                self.circuit_open = True
                logging.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e
    
    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)


class TogetherAITroubleshooter:
    def __init__(self, api_key: str, base_url: str = None, config: Dict = None):
        # Configuration management
        self.config = self._load_config(config)
        self.api_key = api_key
        self.base_url = base_url or self.config.get('base_url', 'https://api.together.xyz')
        
        # Setup logging
        self._setup_logging()
        
        # Initialize robust HTTP client
        self.http_client = RobustHTTPClient(
            timeout=self.config.get('timeout', 30),
            max_retries=self.config.get('max_retries', 3)
        )
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.results = []
    
    def _load_config(self, config: Dict = None) -> Dict:
        """Load configuration from multiple sources with environment variable support"""
        default_config = {
            'base_url': 'https://api.together.xyz',
            'timeout': 30,
            'max_retries': 3,
            'performance_test_iterations': 3,
            'concurrent_test_requests': 5,
            'circuit_breaker_threshold': 5,
            'circuit_breaker_timeout': 60,
            'log_level': 'INFO',
            'performance_thresholds': {
                'real_time_chat': 2000,
                'api_backend': 5000,
                'batch_processing': 30000
            }
        }
        
        # Override with environment variables
        env_config = {
            'base_url': os.getenv('TOGETHER_AI_BASE_URL'),
            'timeout': int(os.getenv('TOGETHER_AI_TIMEOUT', '30')),
            'max_retries': int(os.getenv('TOGETHER_AI_MAX_RETRIES', '3')),
            'log_level': os.getenv('TOGETHER_AI_LOG_LEVEL', 'INFO')
        }
        
        # Merge configurations
        final_config = default_config.copy()
        final_config.update({k: v for k, v in env_config.items() if v is not None})
        if config:
            final_config.update(config)
            
        return final_config
    
    def _setup_logging(self):
        """Setup structured logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('together_ai_troubleshooter.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def add_result(self, result: DiagnosticResult):
        """Add a diagnostic result"""
        self.results.append(result)
        print(f"[{result.status}] {result.test_name}: {result.message}")
        if result.recommendation:
            print(f"  → Recommendation: {result.recommendation}")

    @retry_with_backoff(max_retries=3, base_delay=1)
    def test_api_connectivity(self) -> DiagnosticResult:
        """Test basic API connectivity with robust error handling"""
        try:
            self.logger.info("Testing API connectivity...")
            # Test with a simple model list request using robust HTTP client
            response = self.http_client.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                return DiagnosticResult(
                    "API Connectivity",
                    "PASS",
                    f"Successfully connected to Together AI API (Status: {response.status_code})",
                    {"response_time_ms": response.elapsed.total_seconds() * 1000}
                )
            elif response.status_code == 401:
                return DiagnosticResult(
                    "API Connectivity",
                    "FAIL",
                    "Authentication failed - Invalid API key",
                    {"status_code": response.status_code},
                    "Check your API key in Settings > API Keys at api.together.ai"
                )
            else:
                return DiagnosticResult(
                    "API Connectivity",
                    "FAIL",
                    f"API request failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text[:200]},
                    "Check Together AI status page at status.together.ai"
                )
                
        except requests.exceptions.Timeout:
            return DiagnosticResult(
                "API Connectivity",
                "FAIL",
                "Request timed out after 10 seconds",
                None,
                "Check your network connection and Together AI status"
            )
        except requests.exceptions.ConnectionError:
            return DiagnosticResult(
                "API Connectivity",
                "FAIL",
                "Unable to connect to Together AI API",
                None,
                "Check your internet connection and firewall settings"
            )

    def test_rate_limits(self, model: str = "mistralai/Mistral-7B-Instruct-v0.1") -> DiagnosticResult:
        """Test current rate limit status"""
        try:
            # Make a simple completion request to check rate limit headers
            payload = {
                "model": model,
                "prompt": "Hello",
                "max_tokens": 1,
                "temperature": 0.1
            }
            
            response = self.http_client.post(
                f"{self.base_url}/inference",
                headers=self.headers,
                json=payload
            )
            
            # Check rate limit headers
            headers = response.headers
            rate_limit_info = {}
            
            for header in headers:
                if 'rate-limit' in header.lower() or 'ratelimit' in header.lower():
                    rate_limit_info[header] = headers[header]
            
            if response.status_code == 429:
                retry_after = headers.get('retry-after', 'Unknown')
                return DiagnosticResult(
                    "Rate Limits",
                    "FAIL",
                    f"Rate limit exceeded (429 error)",
                    {"retry_after": retry_after, "rate_limit_headers": rate_limit_info},
                    "Implement exponential backoff or request rate limit increase at together.ai/forms/rate-limit-increase"
                )
            elif response.status_code == 200:
                return DiagnosticResult(
                    "Rate Limits",
                    "PASS",
                    "Rate limits OK - request completed successfully",
                    {"rate_limit_headers": rate_limit_info}
                )
            else:
                return DiagnosticResult(
                    "Rate Limits",
                    "WARNING",
                    f"Unexpected status code: {response.status_code}",
                    {"status_code": response.status_code, "rate_limit_headers": rate_limit_info}
                )
                
        except Exception as e:
            return DiagnosticResult(
                "Rate Limits",
                "FAIL",
                f"Error testing rate limits: {str(e)}",
                None,
                "Check API connectivity and model availability"
            )

    def test_model_availability(self, models_to_test: List[str]) -> List[DiagnosticResult]:
        """Test availability of specific models"""
        results = []
        
        try:
            # Get available models using robust HTTP client
            response = self.http_client.get(f"{self.base_url}/v1/models", headers=self.headers)
            
            if response.status_code != 200:
                results.append(DiagnosticResult(
                    "Model Availability",
                    "FAIL",
                    f"Cannot fetch model list (Status: {response.status_code})",
                    None,
                    "Check API connectivity"
                ))
                return results
            
            available_models = [model.get('id', '') for model in response.json()]
            
            for model in models_to_test:
                if model in available_models:
                    results.append(DiagnosticResult(
                        f"Model: {model}",
                        "PASS",
                        "Model is available",
                        {"model": model}
                    ))
                else:
                    results.append(DiagnosticResult(
                        f"Model: {model}",
                        "FAIL",
                        "Model not found in available models",
                        {"model": model, "available_count": len(available_models)},
                        "Check model name spelling or use /models endpoint to see available models"
                    ))
                    
        except Exception as e:
            results.append(DiagnosticResult(
                "Model Availability",
                "FAIL",
                f"Error checking models: {str(e)}",
                None,
                "Check API connectivity"
            ))
            
        return results

    async def _make_async_request(self, session, url, headers, payload):
        """Make async HTTP request for concurrent testing"""
        start_time = time.time()
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    response_data = await response.json()
                    tokens_generated = len(response_data.get('output', {}).get('choices', [{}])[0].get('text', '').split())
                    return {
                        'success': True,
                        'response_time': response_time,
                        'tokens_generated': tokens_generated,
                        'status_code': response.status
                    }
                else:
                    return {
                        'success': False,
                        'response_time': response_time,
                        'error': f"Status {response.status}",
                        'status_code': response.status
                    }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': (end_time - start_time) * 1000,
                'error': str(e),
                'status_code': None
            }

    async def test_inference_performance_async(self, model: str, num_tests: int = None) -> DiagnosticResult:
        """Test inference performance with concurrent requests and detailed metrics"""
        try:
            num_tests = num_tests or self.config.get('performance_test_iterations', 3)
            concurrent_requests = self.config.get('concurrent_test_requests', 5)
            
            self.logger.info(f"Testing performance with {num_tests} requests, {concurrent_requests} concurrent")
            
            test_prompts = [
                "What is the capital of France?",
                "Write a haiku about technology.",
                "Explain quantum computing in simple terms.",
                "Describe the benefits of renewable energy.",
                "How does machine learning work?"
            ]
            
            # Prepare requests
            requests_data = []
            for i in range(num_tests):
                prompt = test_prompts[i % len(test_prompts)]
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": 50,
                    "temperature": 0.7
                }
                requests_data.append(payload)
            
            # Execute concurrent requests
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                tasks = []
                for payload in requests_data:
                    task = self._make_async_request(
                        session, 
                        f"{self.base_url}/inference", 
                        self.headers, 
                        payload
                    )
                    tasks.append(task)
                
                # Execute in batches to avoid overwhelming the API
                results = []
                for i in range(0, len(tasks), concurrent_requests):
                    batch = tasks[i:i + concurrent_requests]
                    batch_results = await asyncio.gather(*batch, return_exceptions=True)
                    results.extend(batch_results)
                    
                    # Small delay between batches
                    if i + concurrent_requests < len(tasks):
                        await asyncio.sleep(0.5)
            
            # Process results
            successful_requests = [r for r in results if isinstance(r, dict) and r.get('success')]
            failed_requests = [r for r in results if isinstance(r, dict) and not r.get('success')]
            
            if successful_requests:
                response_times = [r['response_time'] for r in successful_requests]
                tokens_generated = [r.get('tokens_generated', 0) for r in successful_requests]
                
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                total_tokens = sum(tokens_generated)
                avg_tokens_per_second = total_tokens / (sum(response_times) / 1000) if response_times else 0
                
                # Determine status based on performance thresholds
                thresholds = self.config.get('performance_thresholds', {})
                api_backend_threshold = thresholds.get('api_backend', 5000)
                
                status = "PASS"
                recommendation = ""
                
                if avg_time > api_backend_threshold:
                    status = "WARNING"
                    recommendation = f"Response times exceed {api_backend_threshold}ms threshold - consider using smaller models or dedicated instances"
                elif avg_time > api_backend_threshold * 2:
                    status = "FAIL"
                    recommendation = "Response times are extremely high - check model availability and system status"
                
                return DiagnosticResult(
                    "Inference Performance",
                    status,
                    f"Avg: {avg_time:.0f}ms, Min: {min_time:.0f}ms, Max: {max_time:.0f}ms, TPS: {avg_tokens_per_second:.1f}",
                    {
                        "avg_response_time_ms": avg_time,
                        "min_response_time_ms": min_time,
                        "max_response_time_ms": max_time,
                        "successful_requests": len(successful_requests),
                        "failed_requests": len(failed_requests),
                        "total_tokens_generated": total_tokens,
                        "avg_tokens_per_second": avg_tokens_per_second,
                        "concurrent_requests_tested": concurrent_requests,
                        "errors": [r.get('error', 'Unknown error') for r in failed_requests]
                    },
                    recommendation
                )
            else:
                return DiagnosticResult(
                    "Inference Performance",
                    "FAIL",
                    "All performance tests failed",
                    {"errors": [r.get('error', 'Unknown error') for r in failed_requests]},
                    "Check model availability and API status"
                )
                
        except Exception as e:
            self.logger.error(f"Performance test error: {str(e)}")
            return DiagnosticResult(
                "Inference Performance",
                "FAIL",
                f"Performance test error: {str(e)}",
                None,
                "Check API connectivity and model availability"
            )

    def test_inference_performance(self, model: str, num_tests: int = 3) -> DiagnosticResult:
        """Synchronous wrapper for async performance testing"""
        return asyncio.run(self.test_inference_performance_async(model, num_tests))

    def test_billing_status(self) -> DiagnosticResult:
        """Test billing and account status"""
        try:
            # This is a placeholder - Together AI doesn't have a public billing endpoint
            # In practice, you'd check your dashboard or use any available account endpoints
            
            return DiagnosticResult(
                "Billing Status",
                "INFO",
                "Cannot automatically check billing status",
                None,
                "Manually check your billing status at api.together.ai Settings > Billing"
            )
            
        except Exception as e:
            return DiagnosticResult(
                "Billing Status",
                "FAIL",
                f"Error checking billing: {str(e)}",
                None,
                "Check your account at api.together.ai"
            )

    def test_error_patterns(self, model: str) -> DiagnosticResult:
        """Test for common error patterns"""
        try:
            # Test various error conditions
            test_cases = [
                {
                    "name": "Invalid model",
                    "payload": {"model": "non-existent-model", "prompt": "test", "max_tokens": 1},
                    "expected_status": 400
                },
                {
                    "name": "Empty prompt",
                    "payload": {"model": model, "prompt": "", "max_tokens": 1},
                    "expected_status": 400
                },
                {
                    "name": "Excessive max_tokens",
                    "payload": {"model": model, "prompt": "test", "max_tokens": 100000},
                    "expected_status": 400
                }
            ]
            
            error_results = []
            
            for test_case in test_cases:
                response = self.http_client.post(
                    f"{self.base_url}/inference",
                    headers=self.headers,
                    json=test_case["payload"]
                )
                
                if response.status_code == test_case["expected_status"]:
                    error_results.append(f"✓ {test_case['name']}: Correctly handled")
                else:
                    error_results.append(f"✗ {test_case['name']}: Unexpected status {response.status_code}")
                
                time.sleep(0.5)  # Brief pause between tests
            
            return DiagnosticResult(
                "Error Handling",
                "INFO",
                "Error pattern test completed",
                {"test_results": error_results}
            )
            
        except Exception as e:
            return DiagnosticResult(
                "Error Handling",
                "FAIL",
                f"Error testing patterns: {str(e)}",
                None
            )

    def run_full_diagnostic(self, models_to_test: List[str] = None) -> Dict:
        """Run complete diagnostic suite"""
        print("=== Together AI Inference Troubleshooting Tool ===\n")
        
        if models_to_test is None:
            models_to_test = [
                "mistralai/Mistral-7B-Instruct-v0.1",
                "meta-llama/Llama-2-7b-chat-hf",
                "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
            ]
        
        # Test 1: API Connectivity
        self.add_result(self.test_api_connectivity())
        
        # Test 2: Rate Limits
        if self.results[-1].status != "FAIL":
            self.add_result(self.test_rate_limits(models_to_test[0]))
        
        # Test 3: Model Availability
        if self.results[-1].status != "FAIL":
            model_results = self.test_model_availability(models_to_test)
            for result in model_results:
                self.add_result(result)
        
        # Test 4: Performance Test (only if basic tests pass)
        working_models = [r.details.get('model') for r in self.results 
                         if r.test_name.startswith('Model:') and r.status == 'PASS']
        
        if working_models:
            self.add_result(self.test_inference_performance(working_models[0]))
        
        # Test 5: Billing Status
        self.add_result(self.test_billing_status())
        
        # Test 6: Error Patterns
        if working_models:
            self.add_result(self.test_error_patterns(working_models[0]))
        
        # Generate summary
        summary = self.generate_summary()
        print("\n" + "="*50)
        print("DIAGNOSTIC SUMMARY")
        print("="*50)
        print(summary)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "test": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "recommendation": r.recommendation
                }
                for r in self.results
            ],
            "summary": summary
        }

    def generate_summary(self) -> str:
        """Generate a summary of all diagnostic results"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        warnings = len([r for r in self.results if r.status == "WARNING"])
        
        summary = f"""
Test Results: {passed} PASSED, {failed} FAILED, {warnings} WARNINGS out of {total_tests} total tests

Critical Issues:
"""
        
        critical_issues = [r for r in self.results if r.status == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                summary += f"• {issue.test_name}: {issue.message}\n"
                if issue.recommendation:
                    summary += f"  Action: {issue.recommendation}\n"
        else:
            summary += "• None detected\n"
        
        summary += "\nRecommended Actions:\n"
        
        # Provide specific troubleshooting advice based on results
        if any(r.test_name == "API Connectivity" and r.status == "FAIL" for r in self.results):
            summary += "• Check your internet connection and API key\n"
            summary += "• Visit status.together.ai to check service status\n"
        
        if any("429" in r.message for r in self.results):
            summary += "• Implement rate limiting in your application\n"
            summary += "• Consider requesting higher rate limits\n"
            summary += "• Use exponential backoff for retries\n"
        
        if any(r.test_name.startswith("Model:") and r.status == "FAIL" for r in self.results):
            summary += "• Verify model names using the /models endpoint\n"
            summary += "• Check if models require special access or billing tier\n"
        
        performance_results = [r for r in self.results if r.test_name == "Inference Performance"]
        if performance_results and performance_results[0].status in ["WARNING", "FAIL"]:
            summary += "• Consider using smaller or faster models\n"
            summary += "• Check if you're on a busy tier - consider upgrading\n"
        
        return summary

    def diagnose_customer_issue(self, customer_report: str) -> str:
        """Diagnose specific customer-reported issues"""
        customer_report = customer_report.lower()
        
        if "503" in customer_report:
            return """
503 Service Unavailable - Possible Causes:
• Together AI servers are temporarily overloaded
• Scheduled maintenance or capacity issues
• Regional outages or network problems

Recommended Actions:
1. Check status.together.ai for known issues
2. Implement retry logic with exponential backoff
3. Consider switching to dedicated instances for guaranteed capacity
4. If persistent, contact Together AI support
"""
        
        elif "429" in customer_report or "rate limit" in customer_report:
            return """
429 Rate Limit Exceeded - Possible Causes:
• Exceeding requests per second (RPS) limits
• Exceeding tokens per second (TPS) limits  
• Burst traffic patterns overwhelming limits

Recommended Actions:
1. Implement request queuing and rate limiting
2. Use exponential backoff for retries
3. Monitor rate limit headers in responses
4. Request higher limits at together.ai/forms/rate-limit-increase
5. Consider upgrading to Scale or Enterprise tiers
"""
        
        elif "401" in customer_report or "authentication" in customer_report:
            return """
401 Authentication Failed - Possible Causes:
• Invalid or expired API key
• API key not included in Authorization header
• Incorrect header format

Recommended Actions:
1. Verify API key at api.together.ai Settings > API Keys
2. Ensure header format: "Authorization: Bearer YOUR_API_KEY"
3. Regenerate API key if compromised
4. Check if API key has required permissions
"""
        
        elif "400" in customer_report or "bad request" in customer_report:
            return """
400 Bad Request - Possible Causes:
• Invalid request format or parameters
• Missing required fields (model, prompt)
• Invalid model name or unavailable model
• Excessive max_tokens parameter

Recommended Actions:
1. Validate request payload against API documentation
2. Check model name using /models endpoint
3. Ensure max_tokens is within model limits
4. Verify all required fields are present
"""
        
        elif "timeout" in customer_report or "slow" in customer_report:
            return """
Timeout/Slow Response Issues - Possible Causes:
• Large models taking longer to generate responses
• High system load during peak hours
• Complex prompts requiring more processing
• Network latency issues

Recommended Actions:
1. Increase client timeout values
2. Use smaller/faster models for time-critical applications
3. Implement async processing for long requests
4. Consider dedicated instances for consistent performance
5. Optimize prompts to be more specific and concise
"""
        
        else:
            return """
General Troubleshooting Steps:
1. Run full diagnostic using this tool
2. Check Together AI status page
3. Verify API key and permissions
4. Test with different models and simple prompts
5. Implement proper error handling and retries
6. Monitor rate limits and usage patterns
7. Contact Together AI support with specific error details
"""


def main():
    """Example usage of the troubleshooting tool"""
    
    # Get API key from user or environment
    api_key = os.getenv('TOGETHERAI_API_KEY') or os.getenv('TOGETHER_AI_API_KEY') or input("Enter your Together AI API key: ").strip()
    
    if not api_key:
        print("API key is required to run diagnostics")
        print("Set TOGETHER_AI_API_KEY environment variable or enter it manually")
        return
    
    # Load configuration from environment or use defaults
    config = {
        'log_level': os.getenv('TOGETHER_AI_LOG_LEVEL', 'INFO'),
        'timeout': int(os.getenv('TOGETHER_AI_TIMEOUT', '30')),
        'performance_test_iterations': int(os.getenv('TOGETHER_AI_PERF_TESTS', '3')),
        'concurrent_test_requests': int(os.getenv('TOGETHER_AI_CONCURRENT', '5'))
    }
    
    # Initialize troubleshooter with configuration
    troubleshooter = TogetherAITroubleshooter(api_key, config=config)
    
    # Get models to test
    models_input = input("Enter models to test (comma-separated, or press Enter for defaults): ").strip()
    
    if models_input:
        models_to_test = [model.strip() for model in models_input.split(",")]
    else:
        models_to_test = None
    
    # Run diagnostics
    results = troubleshooter.run_full_diagnostic(models_to_test)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"together_ai_diagnostic_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {filename}")
    
    # Example customer issue diagnosis
    print("\n" + "="*50)
    print("CUSTOMER ISSUE DIAGNOSIS")
    print("="*50)
    
    issue_report = input("Describe customer issue (or press Enter to skip): ").strip()
    
    if issue_report:
        diagnosis = troubleshooter.diagnose_customer_issue(issue_report)
        print(diagnosis)


if __name__ == "__main__":
    main()