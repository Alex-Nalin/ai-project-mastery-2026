"""
AI Lead Generation Demo - Document Analysis Tool
This demo showcases AI capabilities to potential clients.
When they hit usage limits, they're prompted to book a consultation.
"""

import gradio as gr
import os
from anthropic import Anthropic
import json
from datetime import datetime

# Initialize Claude Opus 4.8
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Track usage per session (in-memory for demo)
session_usage = {}

def analyze_document(document_text: str, analysis_type: str, email: str = ""):
    """
    Analyze a document and demonstrate AI capabilities.
    After 3 free uses, prompt for consultation booking.
    """
    
    session_id = os.getenv("SPACE_ID", "local") + "_" + str(hash(email))
    
    # Track usage
    if session_id not in session_usage:
        session_usage[session_id] = 0
    session_usage[session_id] += 1
    
    free_uses_remaining = max(0, 3 - session_usage[session_id])
    
    # Check if user has exceeded free tier
    if session_usage[session_id] > 3 and not email:
        return {
            "error": True,
            "message": "You've used all free analyses!",
            "book_consultation": True,
            "free_uses_remaining": 0
        }
    
    # Prepare system prompt based on analysis type
    system_prompts = {
        "executive_summary": "You are an executive summarizer. Provide a concise, actionable summary.",
        "sentiment": "Analyze the sentiment and emotional tone of this document.",
        "key_insights": "Extract 5-7 key insights, data points, and actionable takeaways.",
        "readability": "Analyze readability, suggest improvements, and provide a Flesch-Kincaid estimate."
    }
    
    system_prompt = system_prompts.get(analysis_type, system_prompts["executive_summary"])
    
    try:
        response = client.messages.create(
            model="claude-mythos-5-20260401",
            max_tokens=1500,
            system=f"{system_prompt}\n\nFormat your response in clear markdown with sections.",
            messages=[{
                "role": "user",
                "content": f"Please analyze this document:\n\n{document_text[:5000]}"
            }]
        )
        
        result = response.content[0].text
        
        return {
            "error": False,
            "result": result,
            "free_uses_remaining": free_uses_remaining,
            "book_consultation": free_uses_remaining == 0
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Analysis failed: {str(e)}",
            "free_uses_remaining": free_uses_remaining,
            "book_consultation": False
        }

def gradio_interface(document_text, analysis_type, email):
    """Gradio wrapper for the analysis function"""
    
    result = analyze_document(document_text, analysis_type, email)
    
    if result.get("error"):
        if result.get("book_consultation"):
            return f"""
# 🎯 You've Hit the Demo Limit!

You've experienced what our AI can do. Now let's talk about what it can do for YOUR business.

**Book a free 30-minute consultation to discuss:**
- Custom AI solutions for your specific needs
- Enterprise pricing and volume discounts
- Integration with your existing workflows
- Compliance and security requirements

**[👉 Click Here to Book Your Consultation](https://calendly.com/your-consultation-link)**

*Or reply to this message with your phone number and best time to call.*
""", gr.update(visible=True)
        else:
            return f"❌ Error: {result.get('message')}", gr.update(visible=False)
    
    # Format success response with subtle upsell
    free_remaining = result["free_uses_remaining"]
    upsell_message = ""
    
    if free_remaining == 1:
        upsell_message = "\n\n⚠️ **One free analysis remaining!** [Book a consultation](https://calendly.com/your-link) to unlock unlimited usage."
    elif free_remaining == 2:
        upsell_message = f"\n\n📊 You have {free_remaining} free analyses remaining. Need more? [Let's talk](https://calendly.com/your-link)."
    
    return f"""
# Analysis Results

{result['result']}

---

{upsell_message}
""", gr.update(visible=False)

# Build the Gradio interface
with gr.Blocks(title="AI Document Analysis Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 AI Document Analysis Demo
    
    Experience the power of Claude Opus 4.8 for document analysis.
    **Try 3 free analyses** — no credit card required.
    
    *This demo showcases what's possible. Let's build something custom for your business.*
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            document_input = gr.Textbox(
                label="Paste your document text",
                placeholder="Paste any business document, article, or report here...",
                lines=10
            )
            
            with gr.Row():
                analysis_type = gr.Dropdown(
                    choices=["executive_summary", "sentiment", "key_insights", "readability"],
                    value="executive_summary",
                    label="Analysis Type"
                )
                email_input = gr.Textbox(
                    label="Your Email (optional)",
                    placeholder="email@example.com",
                    info="Provide email to unlock more analyses"
                )
            
            analyze_btn = gr.Button("Analyze Document", variant="primary")
        
        with gr.Column(scale=3):
            output = gr.Markdown(label="Analysis Results")
            consultation_cta = gr.Markdown(visible=False)
    
    analyze_btn.click(
        fn=gradio_interface,
        inputs=[document_input, analysis_type, email_input],
        outputs=[output, consultation_cta]
    )
    
    gr.Markdown("""
    ---
    ### 💼 For Enterprise Use
    
    This demo uses a single model. In production, we build multi-agent systems that:
    - Analyze documents at scale (thousands per day)
    - Integrate with your existing tools (Slack, Notion, Salesforce)
    - Maintain brand voice and compliance requirements
    - Provide analytics on content performance
    
    **[Schedule a demo →](https://calendly.com/your-consultation-link)**
    """)

if __name__ == "__main__":
    demo.launch()
