import json

tools = [
    {
        "name": "router",
        "description": "Routing to the path that leads to solution, giving an explanation for the choice, retriving parameters",
        "parameters": {
            "type": "object",
            "strict": True,
            "properties":  {
                "route": {
                    "type": "integer",
                    'enum': [-1, 0, 1, 2, 3],
                    "description": "This should be the selected route based on the question. If no route is selected, use -1.",
                },
                "reason": {
                    "type": "string",
                    "description": "An explanation for why the selected route was chosen.",
                },
                "params": {
                    "type": "object",
                    "description": "The extracted parameters needed to process the request.",
                },
            },
            "required": ["route", "reason", "params"],
        },
    }
]

def router_llm(lm_client, standalone):
    user_message = "User Question: " + standalone
    system_message = '''
    Flow Context for Routing Queries
    Process Overview:

    Customer Stages (L1, L2, L3):

    L1 (Basic Details): Capture personal details and perform e-KYC.
    L2 (Household Details): Record nominee, income, liabilities, and expenses.
    L3 (Bank Details): Verify account details for disbursement readiness.
    Customers must complete L1–L3 before advancing to group formation.

    Group Stages:

    Formation: Create groups (4–10 members) after individual completion of L1–L3.
    Verification: Groups are validated through VO checks (data accuracy, field verification, penny drop).
    Disbursement: Loans are approved and distributed post-verification.
    Key Identifiers:

    customer_id: Used for customer-specific issues (e.g., onboarding, KYC, income verification).
    group_id: Used for group-specific issues (e.g., formation, member details, disbursement errors).
    Common Query Types:

    Customer-specific issues: Require customer_id.
    Group-specific issues: Require group_id.
    Workflow/process questions: No parameters needed.
    Router LLM Task
    You are a router LLM tasked with detecting user intent and selecting the appropriate action. Based on the user query:

    Detect Intent: Determine whether the user seeks process-related guidance or is reporting an error/status inquiry.
    Select an Action:
    Route:
    -1: The query is incomplete or lacks required parameters. Request the missing information politely.
    0: Refer process documentation for guidance on procedures or workflows, even when the query is related to a group/customer but is asking about possibilities, go for this choice.
    1: Use API /api/v1/groups-pipeline when checking the overall status of a group, such as its current stage, success status, or next steps.
    Typically used for group-level status check to identify if there is an error like missing groups in disbursement lists or penny drop failures.
    Parameter required: group_id
    2: Use API /api/v1/customers-pipeline when investigating issues with a specific customer's onboarding or verification process.
    Typically used for individual-level error status check like KYC failures or credit check issues.
    Parameter required: customer_id
    3: Use API /api/v1/group-members when you need to fetch all customers within a group and their respective statuses.
    Typically used to identify specific customers holding up group progress (e.g., penny drop failures).
    Parameter required: group_id

    Input:
    User query

    Output Format:
    {
    'route' : Integer (e.g., -1, 0, 1, 2, 3).
    'reason': A concise explanation for the chosen action. If route -1, address the user directly for missing details.
    'params': Dictionary (e.g., {"group_id": "10101010"}).
    }

    Examples
    Query:
    "What is the current stage of group 10101010?"
    Output:
    {
    'route': 1
    'reason': "The query asks for the group's current stage and status."
    'params': {"group_id": "10101010"}
    }
    Query:
    "I’m facing an error while moving to Level 2."
    Output:
    {
    'route': -1
    'reason': "Could you provide the customer ID associated with this issue? This will help us check the status."
    'params': {}
    }
    Query:
    "How does penny drop validation work?"
    Output:
    {
    'route': 0
    'reason': "The query requests process-related information on penny drop validation."
    'params': {}
    }

    '''

    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = lm_client.chat.completions.create(
        model="gpt-4o",
        messages=msg,
        max_tokens=4000,
        temperature=0.0,
        functions=tools,
        function_call={"name": "router"},
    )

    print(response)
    arguments = json.loads(response.choices[0].message.function_call.arguments)

    route = arguments['route']
    reason = arguments['reason']
    parameters = arguments.get('params', {})
    return route, reason, parameters
    
    