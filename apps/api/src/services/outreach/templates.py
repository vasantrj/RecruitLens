EMAIL_TEMPLATES = {
    "invite_interview": {
        "subject": "Interview Invitation — {role_title}",
        "body": """Hi {candidate_name},

Thank you for applying for the {role_title} position. We were impressed with your background and would like to invite you for an interview.

Could you share your availability for the coming week?

Best regards,
The Hiring Team""",
    },
    "reject": {
        "subject": "Update on your application — {role_title}",
        "body": """Hi {candidate_name},

Thank you for taking the time to apply for the {role_title} position. After careful consideration, we've decided to move forward with other candidates at this time.

We appreciate your interest and encourage you to apply for future openings that match your background.

Best regards,
The Hiring Team""",
    },
    "next_round": {
        "subject": "Moving to the next round — {role_title}",
        "body": """Hi {candidate_name},

Good news — you've been selected to move to the next round for the {role_title} position. Our team will be in touch shortly with further details.

Best regards,
The Hiring Team""",
    },
}


def render_template(template_key: str, candidate_name: str, role_title: str) -> dict:
    template = EMAIL_TEMPLATES.get(template_key)
    if not template:
        raise ValueError(f"Unknown template: {template_key}")

    return {
        "subject": template["subject"].format(role_title=role_title),
        "body": template["body"].format(candidate_name=candidate_name, role_title=role_title),
    }