import streamlit as st
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

st.title("AI Prompt Optimizer")
st.write("Welcome to your prompt improvement tool!")

#Anthropic API key connection functionality
def test_claude_connection():
    """Test if Claude API is working"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say hello in exactly 5 words"}]
        )
        return True, response.content[0].text
    except Exception as e:
        return False, str(e)

# NEW: API connection test
if st.button("🧪 Test Claude Connection"):
    with st.spinner("Testing Claude API..."):
        success, message = test_claude_connection()
        if success:
            st.success(f"✅ Claude connected! Response: {message}")
        else:
            st.error(f"❌ Connection failed: {message}")

st.divider()  # Visual separator


#Use_cases defined - covers use case guidance and tips
USE_CASES = {
    "General": {
        "description": "Basic prompt improvement",
        "tips": []
    },
    "Creative Writing": {
        "description": "Stories, poems, creative content",
        "tips": ["Add genre/style", "Specify tone", "Include character details"]
    },
    "Code Generation": {
        "description": "Programming assistance",
        "tips": ["Specify language", "Include context", "Add constraints"]
    },
    "Data Analysis": {
        "description": "Research and analysis tasks", 
        "tips": ["Define scope", "Specify format", "Include data context"]
    },
    "Business Writing": {
        "description": "Emails, reports, proposals",
        "tips": ["Specify audience", "Include purpose", "Set professional tone"]
    }
}

# Usecase selector
use_case = st.selectbox(
    "What type of AI task is this?",
    options=list(USE_CASES.keys()),
    help="Select your use case for specialized suggestions"
)

# Usecase description
if use_case != "General":
    st.info(f"📋 {USE_CASES[use_case]['description']}")

# Basic UI input screen
user_prompt = st.text_area("Enter your prompt:", 
                          placeholder="Type your AI prompt here...")



#Prompt analysis function define
def analyze_prompt(prompt, use_case="General"):
    """Uses Claude with optimized prompting following Anthropic's best and efficient practices. Uses Claude with rating system(1-5 stars) to analyze and improve prompts.  """
    try:
        #Claude client
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Efficient prompt to Claude (keeps costs low)
        claude_prompt = f"""<role> You are an expert prompt engineer specializing in {use_case.lower()} tasks. You'll be polite and concise. Do not beat around the bush and give direct answers as well as provide your path of reasoning. </role>:

<task>
First, Rate this prompt using these research-based criteria:

**Specificity**: Clear, concrete requirements vs vague requests
**Context**: Sufficient background information provided  
**Structure**: Organized, logical flow of instructions
**Constraints**: Appropriate limits (length, format, style)
**Examples**: Includes samples or clarifying details where helpful
**Actionability**: AI can execute the request successfully

Rating Scale:
★☆☆☆☆ (1/5) - Poor: Lacks 4+ criteria, likely to produce unusable output
★★☆☆☆ (2/5) - Needs work: Missing 2-3 key criteria, inconsistent results expected  
★★★☆☆ (3/5) - Good: Meets basic requirements, has visible improvement opportunities
★★★★☆ (4/5) - Very good: Strong prompt with minor optimizations possible (production-ready)
★★★★★ (5/5) - Excellent: Exemplary prompt, minimal improvements possible

Then, provide analysis following these guidelines:
1. Briefly identify what works well (1-2 sentences)
2. List 2-3 specific improvements with rationale
3. Include 1-2 realistic examples of issues the current prompt might cause (e.g., "This prompt might generate inconsistent formats" or "Users could get overly lengthy responses")
4. Provide a concise, optimized rewrite
5. Keep response under 600 words total

Consider {use_case.lower()}-specific requirements in your evaluation.
</task>

<user_prompt>
{prompt}
</user_prompt>

<output_format>
Start with: "RATING: X/5 stars" 
Then provide:
- What works: [brief strengths]
- Potential issues: [1-2 realistic problems users might encounter]
- Key improvements: [2-3 specific suggestions]
- Optimized version: [rewritten prompt]
</output_format>"""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,  # Limits cost
            messages=[{"role": "user", "content": claude_prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"⚠️ Claude API error: {str(e)}"

if st.button("Analyze Prompt"):
    if user_prompt and user_prompt.strip():
        st.success(f"Original prompt: {user_prompt}")
        
        analysis = analyze_prompt(user_prompt, use_case)

        # Extract and display rating
        if "RATING:" in analysis:
            rating_part = analysis.split("RATING:")[1].split("stars")[0].strip()
            rating_number = rating_part.split("/")[0]
            
            # Display rating with stars
            st.subheader("📊 Prompt Quality Rating")
            star_display = "★" * int(rating_number) + "☆" * (5 - int(rating_number))
            st.markdown(f"### {star_display} ({rating_number}/5 stars)")
            
            # ADD THE RATING CONTEXT HERE:
            if int(rating_number) >= 4:
                st.info("🎯 Excellent prompt! Any suggestions are minor optimizations.")
            elif int(rating_number) == 3:
                st.warning("⚠️ Good foundation with clear improvement opportunities.")
            else:
                st.error("🔧 This prompt needs significant improvements to work reliably.")

            # Display analysis 
            analysis_text = analysis.split("stars", 1)[1] if "stars" in analysis else analysis
            st.subheader("🤖 AI Analysis:")
            st.write(analysis_text.strip())
        else:
            st.warning("No rating found in Claude's response.")
            st.subheader("🤖 AI Analysis:")
            st.write(analysis)
            
    else:
        st.error("Please enter a prompt first!")