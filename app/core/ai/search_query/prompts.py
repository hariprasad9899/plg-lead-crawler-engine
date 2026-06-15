"""
Prompt templates for search-query generation.

Kept free of business logic on purpose: this module only declares the prompt
text and the strategy catalogue. Assembly of runtime context lives in
``PromptBuilder``.
"""

from langchain_core.prompts import ChatPromptTemplate

# Human-readable description of each strategy the model must cover.
STRATEGY_GUIDE = """\
1. industry          - Core industry/vertical terms for the target market.
2. persona           - Job titles, roles and seniority of decision-makers.
3. geography         - Region/country/city scoped variants.
4. hiring_signal     - Active-hiring signals (open roles, "we're hiring", growth in headcount).
5. growth_signal     - Funding, expansion, new offices, revenue growth signals.
6. company_size      - Queries narrowed by employee/company-size bands.
7. alt_terminology   - Alternative/synonym industry terms a target might self-describe with.
8. procurement       - Budget-authority / buying-intent / procurement-decision signals.\
"""

SYSTEM_PROMPT = """\
You are an expert B2B lead-generation strategist. Your job is to translate a \
crawl configuration and a natural-language intent into a set of high-quality, \
directly usable search queries for sourcing leads from the specified source.

Generate between {min_queries} and {max_queries} queries. Cover ALL of the \
following strategies, producing at least one query per strategy where the \
provided configuration makes it sensible:

{strategy_guide}

Rules:
- Each query must be specific, natural, and immediately usable as a search string.
- Combine signals from the configuration (industries, locations, seniority, \
keywords, company size) rather than restating a single field.
- Do NOT invent locations, industries or roles that contradict the configuration.
- Assign priority from 1 (highest) to {max_queries}; the most likely to surface \
qualified leads should get the lowest numbers.
- Avoid duplicates and near-duplicates.
- Tag every query with exactly one strategy from the list above.\
"""

HUMAN_PROMPT = """\
Request name: {request_name}

Intent (original query):
{original_query}

Crawl configuration "{config_name}":
{config_description}

Configuration details (JSON):
{config_json}

Produce the search queries now.\
"""


def build_chat_prompt() -> ChatPromptTemplate:
    """Return the assembled chat prompt template for query generation."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )
