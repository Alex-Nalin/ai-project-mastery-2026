FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Calculate the ROI of a marketing campaign that cost $50,000 and generated $175,000 in revenue."
    },
    {
        "role": "assistant",
        "content": """Let me calculate this step by step:

1. **Revenue Generated**: $175,000
2. **Campaign Cost**: $50,000
3. **Net Profit**: $175,000 - $50,000 = $125,000
4. **ROI Formula**: (Net Profit / Cost) × 100
5. **Calculation**: ($125,000 / $50,000) × 100 = 250%

**Final Answer**: The campaign ROI is 250%.

This means for every dollar spent, the company earned $2.50 in return."""
    },
    {
        "role": "user",
        "content": "A subscription service has 10,000 users paying $29/month. Monthly churn is 5%. What's the monthly revenue and how many users leave each month?"
    },
    {
        "role": "assistant",
        "content": """Let me work through this:

1. **Monthly Revenue**: 10,000 users × $29 = $290,000/month
2. **Monthly Churn**: 10,000 × 5% = 500 users leave each month
3. **Revenue Impact of Churn**: 500 × $29 = $14,500 lost revenue/month

**Final Answer**: Monthly revenue is $290,000, and 500 users churn each month, representing $14,500 in lost recurring revenue.

To maintain growth, the company needs to acquire at least 500 new users per month just to break even."""
    }
]
