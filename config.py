"""
Configuration file for Together AI troubleshooting scenarios
Contains error codes, common issues, and automated diagnostic rules
"""

# Error code mappings from Together AI documentation
ERROR_CODES = {
    400: {
        "name": "Bad Request",
        "common_causes": [
            "Invalid request format",
            "Missing required parameters (model, prompt)",
            "Invalid model name",
            "max_tokens exceeds model limit",
            "Invalid parameter values"
        ],
        "solutions": [
            "Validate request payload format",
            "Check model name against /models endpoint",
            "Reduce max_tokens parameter", 
            "Ensure all required fields are present",
            "Verify parameter data types"
        ]
    },
    401: {
        "name": "Unauthorized",
        "common_causes": [
            "Invalid API key",
            "Missing Authorization header",
            "Expired API key",
            "Incorrect header format"
        ],
        "solutions": [
            "Verify API key at api.together.ai",
            "Use format: 'Authorization: Bearer YOUR_API_KEY'",
            "Regenerate API key if needed",
            "Check API key permissions"
        ]
    },
    404: {
        "name": "Not Found",
        "common_causes": [
            "Invalid endpoint URL",
            "Model not available",
            "Incorrect API version"
        ],
        "solutions": [
            "Check endpoint URL spelling",
            "Verify model exists in /models list",
            "Use correct base URL: https://api.together.xyz"
        ]
    },
    429: {
        "name": "Rate Limit Exceeded",
        "common_causes": [
            "Too many requests per second (RPS)",
            "Too many tokens per second (TPS)", 
            "Burst traffic patterns",
            "Insufficient rate limit tier"
        ],
        "solutions": [
            "Implement exponential backoff",
            "Add request queuing",
            "Monitor rate limit headers",
            "Request higher limits",
            "Upgrade to Scale/Enterprise tier"
        ]
    },
    500: {
        "name": "Internal Server Error",
        "common_causes": [
            "Server-side processing error",
            "Model inference failure",
            "Temporary system issues"
        ],
        "solutions": [
            "Retry request after delay",
            "Check Together AI status page",
            "Try different model",
            "Contact support if persistent"
        ]
    },
    503: {
        "name": "Service Unavailable", 
        "common_causes": [
            "Server overload",
            "Scheduled maintenance",
            "Capacity issues",
            "Regional outages"
        ],
        "solutions": [
            "Check status.together.ai",
            "Implement retry with backoff",
            "Switch to dedicated instances",
            "Use different region if available"
        ]
    }
}

# Rate limit tiers and thresholds
RATE_LIMIT_TIERS = {
    "build_tier_1": {
        "rps": 1,
        "tps": 20000,
        "description": "Entry level, automatic increases available"
    },
    "build_tier_2": {
        "rps": 5, 
        "tps": 100000,
        "description": "Intermediate level with higher limits"
    },
    "scale": {
        "rps": "Custom",
        "tps": "Unlimited",
        "description": "Enterprise level with custom limits"
    }
}

# Common models and their characteristics
POPULAR_MODELS = {
    "mistralai/Mistral-7B-Instruct-v0.1": {
        "type": "Chat",
        "size": "7B",
        "context_length": 8192,
        "typical_latency_ms": 500,
        "good_for": ["General chat", "Fast responses"]
    },
    "meta-llama/Llama-2-7b-chat-hf": {
        "type": "Chat", 
        "size": "7B",
        "context_length": 4096,
        "typical_latency_ms": 600,
        "good_for": ["Conversational AI", "Code assistance"]
    },
    "meta-llama/Llama-2-70b-chat-hf": {
        "type": "Chat",
        "size": "70B", 
        "context_length": 4096,
        "typical_latency_ms": 2000,
        "good_for": ["Complex reasoning", "High quality responses"]
    },
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": {
        "type": "Chat",
        "size": "8x7B MoE",
        "context_length": 32768,
        "typical_latency_ms": 1200,
        "good_for": ["Long context", "Instruction following"]
    },
    "togethercomputer/RedPajama-INCITE-7B-Chat": {
        "type": "Chat",
        "size": "7B",
        "context_length": 2048,
        "typical_latency_ms": 400,
        "good_for": ["Fast inference", "Simple tasks"]
    }
}

# Embeddings models
EMBEDDING_MODELS = {
    "WhereIsAI/UAE-Large-V1": {
        "type": "Embeddings",
        "dimensions": 1024,
        "max_input_length": 512,
        "good_for": ["General embeddings", "Semantic search"]
    },
    "BAAI/bge-large-en-v1.5": {
        "type": "Embeddings", 
        "dimensions": 1024,
        "max_input_length": 512,
        "good_for": ["English text", "Retrieval"]
    }
}

# Performance thresholds for different use cases
PERFORMANCE_THRESHOLDS = {
    "real_time_chat": {
        "max_latency_ms": 2000,
        "warning_latency_ms": 1000,
        "description": "Interactive chat applications"
    },
    "batch_processing": {
        "max_latency_ms": 30000,
        "warning_latency_ms": 10000, 
        "description": "Non-interactive batch jobs"
    },
    "api_backend": {
        "max_latency_ms": 5000,
        "warning_latency_ms": 2000,
        "description": "API backend services"
    }
}

# Troubleshooting decision tree
DIAGNOSTIC_RULES = [
    {
        "condition": "status_code == 503",
        "priority": "high",
        "category": "availability",
        "message": "Service unavailable - likely capacity or maintenance issue",
        "actions": [
            "Check status.together.ai for incidents", 
            "Implement retry with exponential backoff",
            "Consider dedicated instances for guaranteed capacity"
        ]
    },
    {
        "condition": "status_code == 429 and 'rate limit' in error_message",
        "priority": "high", 
        "category": "rate_limiting",
        "message": "Rate limit exceeded - need to reduce request frequency",
        "actions": [
            "Check current rate limit in Settings > Billing",
            "Implement request queuing",
            "Request rate limit increase if justified",
            "Add exponential backoff"
        ]
    },
    {
        "condition": "status_code == 401",
        "priority": "high",
        "category": "authentication", 
        "message": "Authentication failure - API key issue",
        "actions": [
            "Verify API key format and validity",
            "Check Authorization header format",
            "Regenerate API key if compromised",
            "Ensure API key has required permissions"
        ]
    },
    {
        "condition": "response_time_ms > 10000",
        "priority": "medium",
        "category": "performance",
        "message": "High latency detected - performance issue",
        "actions": [
            "Try smaller/faster model",
            "Check system load and capacity",
            "Optimize prompt length and complexity",
            "Consider dedicated instances"
        ]
    },
    {
        "condition": "status_code == 400 and 'model' in error_message",
        "priority": "medium",
        "category": "configuration",
        "message": "Invalid model specification",
        "actions": [
            "Check model name against /models endpoint",
            "Verify model is available in your tier",
            "Check spelling and case sensitivity",
            "Try alternative similar model"
        ]
    },
    {
        "condition": "status_code == 400 and 'max_tokens' in error_message", 
        "priority": "medium",
        "category": "configuration",
        "message": "Token limit exceeded for model",
        "actions": [
            "Reduce max_tokens parameter",
            "Check model's context length limit",
            "Split request into smaller chunks",
            "Use model with higher token limit"
        ]
    },
    {
        "condition": "connection_timeout",
        "priority": "medium",
        "category": "connectivity",
        "message": "Network connectivity issue",
        "actions": [
            "Check internet connection",
            "Verify firewall settings",
            "Test with different network",
            "Increase client timeout values"
        ]
    }
]

# Customer issue patterns and responses
CUSTOMER_ISSUE_PATTERNS = {
    "high_503_errors": {
        "description": "Customer reporting frequent 503 Service Unavailable errors",
        "investigation_steps": [
            "Check Together AI status page for incidents",
            "Review customer's request patterns for traffic spikes", 
            "Verify if customer is on appropriate tier for their usage",
            "Check if specific models are experiencing issues",
            "Review retry logic implementation"
        ],
        "solutions": [
            "Implement exponential backoff with jitter",
            "Add circuit breaker pattern",
            "Recommend dedicated instances for guaranteed capacity",
            "Suggest load balancing across multiple models",
            "Upgrade to higher tier if needed"
        ],
        "escalation_criteria": [
            "503 errors persist for >30 minutes",
            "Multiple customers affected",
            "No incidents on status page",
            "Customer has dedicated instances still failing"
        ]
    },
    "rate_limit_exceeded": {
        "description": "Customer hitting rate limits frequently",
        "investigation_steps": [
            "Check customer's current rate limit tier and usage",
            "Analyze request patterns for bursts vs steady load",
            "Review if rate limit headers are being monitored",
            "Verify proper retry implementation",
            "Check if multiple API keys are being used properly"
        ],
        "solutions": [
            "Implement request queuing to smooth traffic",
            "Add rate limit monitoring and alerting", 
            "Request rate limit increase with justification",
            "Suggest upgrading to Scale/Enterprise tier",
            "Optimize batch processing to reduce RPS"
        ],
        "escalation_criteria": [
            "Customer has legitimate high-volume use case",
            "Rate limit increase needed urgently",
            "Technical solutions not sufficient"
        ]
    },
    "slow_performance": {
        "description": "Customer experiencing slow response times",
        "investigation_steps": [
            "Measure actual response times for customer's models",
            "Check if customer is using appropriate model size",
            "Review prompt complexity and length",
            "Verify customer's geographic location vs server regions",
            "Check if customer is on shared vs dedicated infrastructure"
        ],
        "solutions": [
            "Recommend smaller/faster models for latency-sensitive use cases",
            "Suggest prompt optimization techniques",
            "Consider dedicated instances for consistent performance",
            "Implement async processing for long-running requests",
            "Use streaming responses where applicable"
        ],
        "escalation_criteria": [
            "Performance significantly worse than SLA",
            "Performance degradation across multiple models",
            "Customer has dedicated instances with poor performance"
        ]
    },
    "authentication_failures": {
        "description": "Customer unable to authenticate API requests",
        "investigation_steps": [
            "Verify API key format and validity",
            "Check if API key was recently regenerated",
            "Review Authorization header implementation",
            "Test with known working API key",
            "Check for any account billing issues"
        ],
        "solutions": [
            "Guide through API key regeneration process",
            "Provide correct header format examples",
            "Check account status and billing",
            "Verify API permissions and scope"
        ],
        "escalation_criteria": [
            "API key appears valid but still failing",
            "Authentication works intermittently",
            "Account-level issues detected"
        ]
    },
    "model_unavailable": {
        "description": "Customer cannot access specific models",
        "investigation_steps": [
            "Check if model exists in current model catalog",
            "Verify model availability in customer's tier",
            "Check for model deprecation or updates",
            "Review any special access requirements",
            "Test model availability with internal tools"
        ],
        "solutions": [
            "Provide current model list and alternatives",
            "Guide through tier upgrade if needed",
            "Suggest similar models with equivalent capabilities",
            "Update to newer model versions if deprecated"
        ],
        "escalation_criteria": [
            "Model should be available but returns errors",
            "Customer has paid tier but cannot access expected models",
            "Model availability inconsistent"
        ]
    },
    "unexpected_errors": {
        "description": "Customer experiencing unusual or intermittent errors",
        "investigation_steps": [
            "Collect detailed error logs and request/response examples",
            "Check error frequency and patterns",
            "Review recent changes to customer's implementation",
            "Test with simplified request payloads",
            "Check for any infrastructure issues"
        ],
        "solutions": [
            "Implement comprehensive error handling",
            "Add detailed logging and monitoring",
            "Provide error reproduction steps",
            "Suggest alternative approaches"
        ],
        "escalation_criteria": [
            "Errors cannot be reproduced or explained",
            "Errors indicate potential service bugs",
            "Customer impact is severe"
        ]
    }
}

# Monitoring and alerting recommendations
MONITORING_RECOMMENDATIONS = {
    "essential_metrics": [
        "Request success rate (%)",
        "Average response time (ms)",
        "Rate limit utilization (%)",
        "Error rate by status code",
        "Token usage per time period"
    ],
    "alerting_thresholds": {
        "error_rate": {
            "warning": 5,  # % of requests
            "critical": 10
        },
        "response_time": {
            "warning": 5000,  # ms
            "critical": 10000
        },
        "rate_limit_usage": {
            "warning": 80,  # % of limit
            "critical": 95
        }
    },
    "recommended_tools": [
        "Prometheus + Grafana for metrics",
        "ELK Stack for log analysis", 
        "DataDog for comprehensive monitoring",
        "Custom dashboards for Together AI specific metrics"
    ]
}

# Best practices for different use cases
BEST_PRACTICES = {
    "production_deployment": [
        "Implement exponential backoff with jitter",
        "Use circuit breaker pattern for resilience",
        "Monitor rate limits and usage patterns",
        "Set appropriate timeout values",
        "Implement proper error handling and logging",
        "Use dedicated instances for guaranteed performance",
        "Have fallback models ready",
        "Cache responses when appropriate"
    ],
    "development_testing": [
        "Use smaller models for faster iteration",
        "Implement rate limiting in test environment",
        "Test error scenarios thoroughly",
        "Validate input parameters before sending",
        "Use mock responses for unit testing",
        "Test with various prompt lengths and complexities"
    ],
    "cost_optimization": [
        "Choose right-sized models for your use case",
        "Implement request caching where possible",
        "Optimize prompts to reduce token usage",
        "Use batch processing for bulk operations",
        "Monitor usage and set budget alerts",
        "Consider fine-tuning for specialized tasks"
    ]
}

# Quick diagnostic questions for customer support
DIAGNOSTIC_QUESTIONS = [
    "What specific error message or status code are you receiving?",
    "When did the issue start occurring?",
    "What is the frequency of the issue (always, intermittent, specific times)?",
    "Which models are you trying to use?",
    "What is your current rate limit tier?",
    "Can you provide a sample request that's failing?",
    "Are you implementing any retry logic?",
    "Have you checked the Together AI status page?",
    "Are you experiencing this across all your applications or just specific ones?",
    "What is your typical request volume per minute/hour?"
]

# Status page and resource URLs
RESOURCES = {
    "status_page": "https://status.together.ai/",
    "documentation": "https://docs.together.ai/",
    "api_reference": "https://docs.together.ai/reference/",
    "rate_limit_increase": "https://www.together.ai/forms/rate-limit-increase",
    "support_contact": "https://www.together.ai/contact",
    "billing_page": "https://api.together.ai/settings/billing",
    "api_keys": "https://api.together.ai/settings/api-keys",
    "models_endpoint": "https://api.together.xyz/models"
}