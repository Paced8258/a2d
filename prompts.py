SYSTEM_PROMPT = """You are Anti-To-Do, a pragmatic operations and productivity strategist for knowledge workers.
Your job: identify low-leverage tasks the user should STOP doing manually to reclaim time so they can focus on high-leverage tasks.

Principles:
- Prioritize leverage: eliminate, automate, batch, or delegate.
- Be role- and industry-aware. Avoid stereotypes. Avoid intimate/personal assumptions.
- Keep items concrete and verifiable in a workweek.
- Return only what’s requested, in the specified JSON schema.
"""

# RECOMMENDATIONS_INSTRUCTIONS = """Using the user's details, produce 30-40 Anti-To-Do items split into 6 categories tailored to the user's role and industry.

# For EACH item, include:
# - item: short imperative (e.g., "Stop manually triaging routine support emails—route via rules + tags")
# - rationale: 1–2 sentences tied to the role/industry/pains
# - category: one of [eliminate, automate, batch, delegate]
# - estimated_gain_minutes: integer minutes saved per week (50–600 typical)
# - difficulty: [low, medium, high] (how hard to implement)

# Output JSON:
# {
#   "items": [
#     {"item": "...", "rationale": "...", "category": "automate", "estimated_gain_minutes": 180, "difficulty": "low"},
#     ...
#   ]
# }
# """


RECOMMENDATIONS_INSTRUCTIONS = """Using the user's details, produce 30-40 Anti-To-Do items organized by task categories tailored to the user's role and industry. 
Produce 5-7 items per category across 6 categories. For each item, include a rationale tied to the user's role/industry/pains.
Keep item descriptions concise (2-5 words) like the examples shown.

Output JSON:
{
  "categories": [
    {
      "category_name": "Documents & Writing",
      "emoji": "📝",
      "items": [
        {
          "item": "Draft documents",
          "rationale": "Streamline initial content creation for PRDs, specs, or briefs.",
          "estimated_gain_minutes": 60,
          "difficulty": "low"
        },
        {
          "item": "Get and give feedback",
          "rationale": "Efficiently manage review cycles for documents and designs.",
          "estimated_gain_minutes": 45,
          "difficulty": "low"
        }
      ]
    },
    {
      "category_name": "Meetings & Agendas",
      "emoji": "📅",
      "items": [
        {
          "item": "Agendas, summaries, action items",
          "rationale": "Ensure every meeting has a clear purpose and documented outcomes.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        }
      ]
    }
  ]
}
"""

# Few-shot examples to anchor style
FEW_SHOT_EXAMPLE_PM = {
  "role_normalized": "Product Manager",
  "industry": "Tech",
  "pains": "Meetings; context switching; documentation overhead",
  "categories": [
    {
      "category_name": "Documents & Writing",
      "emoji": "📝",
      "items": [
        {
          "item": "Draft documents",
          "rationale": "Streamline initial content creation for PRDs, specs, or briefs.",
          "estimated_gain_minutes": 60,
          "difficulty": "low"
        },
        {
          "item": "Get and give feedback",
          "rationale": "Efficiently manage review cycles for documents and designs.",
          "estimated_gain_minutes": 45,
          "difficulty": "low"
        },
        {
          "item": "Create PRDs, specs, briefs",
          "rationale": "Focus on clear and concise product definition documents.",
          "estimated_gain_minutes": 120,
          "difficulty": "medium"
        },
        {
          "item": "Summarize long Slack/email threads",
          "rationale": "Quickly extract key decisions and action items from lengthy discussions.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        },
        {
          "item": "TL;DRs for execs",
          "rationale": "Provide concise summaries for executive stakeholders to save their time.",
          "estimated_gain_minutes": 20,
          "difficulty": "low"
        }
      ]
    },
    {
      "category_name": "Meetings & Agendas",
      "emoji": "📅",
      "items": [
        {
          "item": "Agendas, summaries, action items",
          "rationale": "Ensure every meeting has a clear purpose and documented outcomes.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        },
        {
          "item": "Follow-up/thank-you emails",
          "rationale": "Automate or template post-meeting communications to maintain relationships.",
          "estimated_gain_minutes": 15,
          "difficulty": "low"
        },
        {
          "item": "Customer-call recaps to Slack",
          "rationale": "Quickly share key insights from customer interactions with the team.",
          "estimated_gain_minutes": 20,
          "difficulty": "low"
        },
        {
          "item": "Discussion → Spec",
          "rationale": "Efficiently translate meeting discussions into actionable specifications.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Calendar review & optimization",
          "rationale": "Regularly audit and refine calendar to reduce unnecessary meetings.",
          "estimated_gain_minutes": 45,
          "difficulty": "medium"
        }
      ]
    },
    {
      "category_name": "Research & Analysis",
      "emoji": "🔍",
      "items": [
        {
          "item": "Track competitors",
          "rationale": "Stay informed about market trends and competitor moves without manual effort.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Summarize NPS/survey results",
          "rationale": "Quickly grasp customer sentiment from feedback data.",
          "estimated_gain_minutes": 90,
          "difficulty": "medium"
        },
        {
          "item": "Competitive pricing comparisons",
          "rationale": "Automate data collection for pricing analysis to inform strategy.",
          "estimated_gain_minutes": 45,
          "difficulty": "medium"
        },
        {
          "item": "Market-trend tracking",
          "rationale": "Monitor industry shifts and emerging opportunities efficiently.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        },
        {
          "item": "Summarize A/B test results",
          "rationale": "Rapidly interpret experiment outcomes to make data-driven decisions.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        }
      ]
    },
    {
      "category_name": "Storytelling & Communication",
      "emoji": "🎤",
      "items": [
        {
          "item": "Find customer stories",
          "rationale": "Identify compelling user narratives for marketing and product validation.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Make slides pretty",
          "rationale": "Delegate or automate aesthetic improvements for presentations.",
          "estimated_gain_minutes": 90,
          "difficulty": "low"
        },
        {
          "item": "Explain product functionality",
          "rationale": "Develop clear and concise explanations for new features.",
          "estimated_gain_minutes": 45,
          "difficulty": "medium"
        },
        {
          "item": "Draft investor updates",
          "rationale": "Streamline the creation of regular communications for investors.",
          "estimated_gain_minutes": 120,
          "difficulty": "high"
        },
        {
          "item": "Blog ↔ Social ↔ Video",
          "rationale": "Repurpose content across multiple channels efficiently.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Create demo scripts",
          "rationale": "Standardize product demonstrations for consistency and efficiency.",
          "estimated_gain_minutes": 90,
          "difficulty": "medium"
        },
        {
          "item": "Translate technical docs into support articles",
          "rationale": "Bridge the gap between engineering and customer support documentation.",
          "estimated_gain_minutes": 120,
          "difficulty": "high"
        }
      ]
    },
    {
      "category_name": "Hiring & People",
      "emoji": "👥",
      "items": [
        {
          "item": "Prep for interviews",
          "rationale": "Streamline preparation for candidate interviews.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        },
        {
          "item": "Summarize hiring-panel notes",
          "rationale": "Quickly synthesize feedback from multiple interviewers.",
          "estimated_gain_minutes": 20,
          "difficulty": "low"
        },
        {
          "item": "Source hard-to-find candidates",
          "rationale": "Leverage tools or networks to identify specialized talent.",
          "estimated_gain_minutes": 90,
          "difficulty": "high"
        },
        {
          "item": "Write job descriptions",
          "rationale": "Create clear and compelling job descriptions efficiently.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Create onboarding checklists",
          "rationale": "Standardize the onboarding process for new hires.",
          "estimated_gain_minutes": 45,
          "difficulty": "low"
        },
        {
          "item": "Draft performance-review feedback",
          "rationale": "Streamline the process of providing constructive feedback.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        }
      ]
    },
    {
      "category_name": "Building",
      "emoji": "🔧",
      "items": [
        {
          "item": "Triage bugs",
          "rationale": "Efficiently prioritize and assign incoming bug reports.",
          "estimated_gain_minutes": 30,
          "difficulty": "low"
        },
        {
          "item": "Fix small UX issues",
          "rationale": "Address minor user experience improvements in a focused manner.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Keep docs up to date",
          "rationale": "Ensure product documentation reflects current features and functionality.",
          "estimated_gain_minutes": 45,
          "difficulty": "medium"
        },
        {
          "item": "Acknowledge GitHub issues",
          "rationale": "Automate initial responses to GitHub issues to keep contributors informed.",
          "estimated_gain_minutes": 15,
          "difficulty": "low"
        },
        {
          "item": "Release notes / changelog",
          "rationale": "Generate release notes automatically from version control history.",
          "estimated_gain_minutes": 60,
          "difficulty": "medium"
        },
        {
          "item": "Code admin: tests, tracking, etc.",
          "rationale": "Streamline administrative tasks related to code quality and monitoring.",
          "estimated_gain_minutes": 90,
          "difficulty": "high"
        }
      ]
    }
  ]
}

def build_recommendations_prompt(role_raw, industry_raw, pains_raw, role_normalized=None, onet_code=None):
    # Build a compact, deterministic content block
    header = {
        "role_input": role_raw,
        "industry_input": industry_raw,
        "pains_input": pains_raw,
        "role_normalized": role_normalized or "",
        "onet_code": onet_code or ""
    }
    return {
        "system": SYSTEM_PROMPT,
        "instructions": RECOMMENDATIONS_INSTRUCTIONS,
        "few_shot": FEW_SHOT_EXAMPLE_PM,
        "context": header
    }