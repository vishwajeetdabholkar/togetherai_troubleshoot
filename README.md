# Together AI Troubleshooting Tool

A comprehensive diagnostic tool for Together AI inference services that helps identify and resolve common issues with API connectivity, rate limits, model availability, and performance.

## Features

### 🚀 Quick Health Check
- **API Connectivity Testing**: Verifies connection to Together AI services
- **Authentication Validation**: Checks API key validity and format
- **Model Availability**: Tests if specified models are accessible
- **Performance Testing**: Measures inference response times
- **Rate Limit Monitoring**: Detects rate limiting issues

### 🔍 Error Code Reference
- Comprehensive lookup for HTTP status codes (400, 401, 404, 429, 500, 503)
- Common causes and specific solutions for each error type
- Best practices for error handling and retry logic

### 🎯 Customer Issue Diagnosis
- Pattern-based issue identification
- Automated troubleshooting recommendations
- Common issue scenarios with step-by-step solutions

### 📊 Monitoring & Alerting
- Essential metrics recommendations
- Alerting threshold guidelines
- Integration with monitoring tools

## Installation & Setup

### Python CLI Tool

1. **Save the main troubleshooting script** as `together_troubleshooter.py`

2. **Install required dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the tool**:
```bash
python together_troubleshooter.py
```

4. **Set your API key** via environment variable or enter when prompted:
```bash
export TOGETHER_AI_API_KEY="your-api-key-here"
python together_troubleshooter.py
```
Get your API key from [api.together.ai](https://api.together.ai/settings/api-keys)

### Web Interface

1. **Save the HTML file** as `troubleshooter.html`
2. **Open in any modern web browser**
3. **Enter your API key** in the Quick Check tab
4. **Run diagnostics** or lookup error codes

## Usage Examples

### Scenario 1: Customer Reports High 503 Errors

**Input**: "Customer is experiencing high rate of 503 errors during peak hours"

**Tool Response**:
- Identifies service unavailability issue
- Provides specific troubleshooting steps
- Recommends implementation of retry logic
- Suggests capacity upgrades if needed

### Scenario 2: Rate Limiting Issues

**Input**: API returns 429 status codes

**Tool Actions**:
- Tests current rate limit status
- Analyzes request patterns
- Provides backoff strategies
- Links to rate limit increase form

### Scenario 3: Authentication Failures

**Input**: Consistent 401 errors

**Tool Response**:
- Validates API key format
- Tests authentication endpoint
- Provides correct header examples
- Guides through key regeneration

## Configuration Options

### Environment Variables
Configure the tool using environment variables:
```bash
export TOGETHER_AI_API_KEY="your-api-key"
export TOGETHER_AI_BASE_URL="https://api.together.xyz"
export TOGETHER_AI_TIMEOUT="30"
export TOGETHER_AI_MAX_RETRIES="3"
export TOGETHER_AI_LOG_LEVEL="INFO"
export TOGETHER_AI_PERF_TESTS="3"
export TOGETHER_AI_CONCURRENT="5"
```

### Models to Test
Default models for testing (can be customized):
- `mistralai/Mistral-7B-Instruct-v0.1`
- `meta-llama/Llama-2-7b-chat-hf`
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`

### Performance Thresholds
- **Real-time chat**: < 2s response time
- **API backend**: < 5s response time  
- **Batch processing**: < 30s response time

### Rate Limit Tiers
- **Build Tier 1**: 1 RPS, 20K TPS
- **Build Tier 2**: 5 RPS, 100K TPS
- **Scale/Enterprise**: Custom limits

### Enhanced Features
- **Robust Error Handling**: Exponential backoff with jitter, circuit breaker pattern
- **Concurrent Testing**: Multiple simultaneous requests for realistic performance testing
- **Token Metrics**: Tokens per second (TPS) measurements
- **Structured Logging**: Detailed logs saved to `together_ai_troubleshooter.log`
- **Connection Pooling**: Efficient HTTP connection reuse

## Diagnostic Tests

### 1. API Connectivity Test
```python
# Tests basic connection to Together AI
response = requests.get("https://api.together.xyz/models", headers=headers)
```

### 2. Authentication Test
```python
# Validates API key and authorization
headers = {"Authorization": f"Bearer {api_key}"}
```

### 3. Model Availability Test
```python
# Checks if specified models exist and are accessible
available_models = [model['id'] for model in response.json()]
```

### 4. Performance Test
```python
# Measures inference response times
start_time = time.time()
inference_response = requests.post(inference_endpoint, data=payload)
response_time = (time.time() - start_time) * 1000
```

### 5. Rate Limit Test
```python
# Analyzes rate limit headers and current usage
rate_limit_info = {k: v for k, v in headers.items() if 'rate-limit' in k.lower()}
```

## Error Code Reference

| Code | Name | Common Causes | Solutions |
|------|------|---------------|-----------|
| **400** | Bad Request | Invalid parameters, wrong model name | Validate payload, check model spelling |
| **401** | Unauthorized | Invalid API key, wrong header format | Verify API key, fix Authorization header |
| **404** | Not Found | Wrong endpoint, unavailable model | Check URL, verify model exists |
| **429** | Rate Limit | Too many requests, exceeded quota | Implement backoff, request limit increase |
| **500** | Server Error | Internal processing error | Retry request, check status page |
| **503** | Service Unavailable | Server overload, maintenance | Check status, implement retry logic |

## Best Practices

### Production Deployment
- ✅ Implement exponential backoff with jitter
- ✅ Use circuit breaker pattern for resilience
- ✅ Monitor rate limits and usage patterns
- ✅ Set appropriate timeout values
- ✅ Implement comprehensive error handling
- ✅ Use dedicated instances for guaranteed performance
- ✅ Have fallback models ready
- ✅ Cache responses when appropriate

### Development & Testing
- ✅ Use smaller models for faster iteration
- ✅ Implement rate limiting in test environment
- ✅ Test error scenarios thoroughly
- ✅ Validate input parameters before sending
- ✅ Use mock responses for unit testing

### Cost Optimization
- ✅ Choose right-sized models for your use case
- ✅ Implement request caching where possible
- ✅ Optimize prompts to reduce token usage
- ✅ Use batch processing for bulk operations
- ✅ Monitor usage and set budget alerts

## Monitoring Setup

### Essential Metrics
1. **Request Success Rate** (target: >99%)
2. **Average Response Time** (target: <2s for real-time)
3. **Rate Limit Utilization** (alert at >80%)
4. **Error Rate by Status Code** (alert at >5%)
5. **Token Usage Trends** (for cost monitoring)

### Alerting Thresholds
```yaml
error_rate:
  warning: 5%    # of total requests
  critical: 10%

response_time:
  warning: 5000ms
  critical: 10000ms

rate_limit_usage:
  warning: 80%   # of allocated limit
  critical: 95%
```

### Recommended Tools
- **Prometheus + Grafana** for metrics visualization
- **ELK Stack** for log analysis
- **DataDog** for comprehensive monitoring
- **Custom dashboards** for Together AI specific metrics

## Integration Examples

### Python Integration
```python
from together_troubleshooter import TogetherAITroubleshooter

# Initialize troubleshooter
troubleshooter = TogetherAITroubleshooter(api_key="your-api-key")

# Run full diagnostic
results = troubleshooter.run_full_diagnostic()

# Diagnose specific customer issue
diagnosis = troubleshooter.diagnose_customer_issue("Customer reports 503 errors")
```

### JavaScript/Node.js Integration
```javascript
// Basic connectivity test
async function testTogetherAI(apiKey) {
    try {
        const response = await fetch('https://api.together.xyz/models', {
            headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        return response.ok;
    } catch (error) {
        console.error('Connection failed:', error);
        return false;
    }
}
```

## Troubleshooting Workflow

### For Customer Support Teams

1. **Immediate Response** (< 5 minutes)
   - Run Quick Health Check
   - Identify error pattern from customer description
   - Provide initial troubleshooting steps

2. **Investigation** (< 30 minutes)
   - Review customer's usage patterns
   - Check Together AI status page
   - Test with customer's specific models/parameters
   - Analyze error frequency and timing

3. **Resolution** (< 2 hours)
   - Implement recommended solutions
   - Escalate to engineering if needed
   - Provide preventive measures
   - Schedule follow-up if necessary

### Escalation Criteria
- 503 errors persist for >30 minutes
- Multiple customers affected simultaneously
- Performance significantly worse than SLA
- Suspected service bugs or infrastructure issues

## Resources & Links

- **Together AI Status**: [status.together.ai](https://status.together.ai/)
- **API Documentation**: [docs.together.ai](https://docs.together.ai/)
- **Rate Limit Increase**: [together.ai/forms/rate-limit-increase](https://www.together.ai/forms/rate-limit-increase)
- **API Keys Management**: [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys)
- **Billing Dashboard**: [api.together.ai/settings/billing](https://api.together.ai/settings/billing)

## Contributing

To extend the troubleshooting tool:

1. **Add new diagnostic tests** in the `TogetherAITroubleshooter` class
2. **Update error patterns** in the configuration file
3. **Enhance customer issue patterns** for better diagnosis
4. **Improve monitoring recommendations** based on best practices

## Support

For issues with the troubleshooting tool itself:
1. Check the troubleshooting guide first
2. Review error logs and diagnostic output
3. Test with minimal configuration
4. Contact Together AI support for API-specific issues

---

*This tool helps maintain high availability and performance for Together AI powered applications by providing rapid issue identification and resolution guidance.*