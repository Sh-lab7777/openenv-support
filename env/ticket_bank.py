"""
A bank of realistic customer support tickets for training and evaluation.
Each ticket has a ground-truth category, priority, and department hint
stored in `metadata` — used by graders but NOT exposed in observations.
"""

from env.models import SupportTicket

TICKET_BANK: list[SupportTicket] = [
    # ── Billing ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T001",
        subject="Double charged on my last invoice",
        body=(
            "Hi, I noticed I was charged twice for my subscription this month. "
            "The amounts are $29.99 on March 3rd and again on March 5th. "
            "Could you please refund the duplicate charge? My account is under "
            "priya.sharma@email.com. Thank you."
        ),
        customer_name="Priya Sharma",
        customer_email="priya.sharma@email.com",
        created_at="2024-03-06T09:14:00Z",
        metadata={"gt_category": "billing", "gt_priority": "high",
                  "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T002",
        subject="Need receipt for tax purposes",
        body=(
            "Hello, I need an official receipt for all my payments in 2023 "
            "for my annual tax return. Could you send a consolidated PDF to "
            "my email? Account: carlos.ruiz@domain.net"
        ),
        customer_name="Carlos Ruiz",
        customer_email="carlos.ruiz@domain.net",
        created_at="2024-01-15T14:22:00Z",
        metadata={"gt_category": "billing", "gt_priority": "medium",
                  "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T003",
        subject="Unexpected charge after cancellation",
        body=(
            "I cancelled my account on February 28th but was still charged "
            "$49 on March 1st. I have the cancellation confirmation email. "
            "This is unacceptable and I want a full refund immediately."
        ),
        customer_name="Ahmed Hassan",
        customer_email="a.hassan@webmail.com",
        created_at="2024-03-04T11:05:00Z",
        metadata={"gt_category": "billing", "gt_priority": "urgent",
                  "gt_department": "billing_team"},
    ),

    # ── Technical ──────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T004",
        subject="App keeps crashing on iOS 17",
        body=(
            "Since I updated to iOS 17 the app crashes every time I try to "
            "open the analytics dashboard. I've reinstalled twice. Device: "
            "iPhone 14 Pro, App version 4.2.1. Crash happens within 3 seconds."
        ),
        customer_name="Li Wei",
        customer_email="liwei@personal.io",
        created_at="2024-03-10T08:30:00Z",
        metadata={"gt_category": "technical", "gt_priority": "high",
                  "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T005",
        subject="API returning 500 errors on bulk import",
        body=(
            "Our integration is failing. POST /v2/import returns HTTP 500 "
            "when the payload exceeds 500 records. Works fine under that. "
            "We're on the Business plan. This is blocking our nightly ETL job."
        ),
        customer_name="Sarah Okonkwo",
        customer_email="sarah@techcorp.io",
        created_at="2024-03-11T22:45:00Z",
        metadata={"gt_category": "technical", "gt_priority": "urgent",
                  "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T006",
        subject="How do I export data to CSV?",
        body=(
            "I've been looking through the settings but can't find the CSV "
            "export option that was mentioned in your tutorial video. "
            "Could you point me in the right direction?"
        ),
        customer_name="James Park",
        customer_email="jpark@gmail.com",
        created_at="2024-03-07T16:00:00Z",
        metadata={"gt_category": "technical", "gt_priority": "low",
                  "gt_department": "tech_support"},
    ),

    # ── Account ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T007",
        subject="Cannot log in — account locked",
        body=(
            "I've been locked out of my account since this morning. "
            "I tried resetting the password but the reset email never arrives. "
            "I have a presentation in 2 hours and need access urgently."
        ),
        customer_name="Fatima Al-Zahra",
        customer_email="fatima.z@company.ae",
        created_at="2024-03-12T07:55:00Z",
        metadata={"gt_category": "account", "gt_priority": "urgent",
                  "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T008",
        subject="Want to upgrade to Enterprise plan",
        body=(
            "Our team has grown to 50 people and we need the Enterprise "
            "features (SSO, audit logs, dedicated support). Can you send "
            "pricing details and connect me with a sales rep?"
        ),
        customer_name="Michael Chen",
        customer_email="mchen@bigcorp.com",
        created_at="2024-03-09T13:10:00Z",
        metadata={"gt_category": "account", "gt_priority": "medium",
                  "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T009",
        subject="Delete my account and all data",
        body=(
            "Please delete my account and all associated data under GDPR "
            "Article 17 (right to erasure). My email is nina@privatebox.eu. "
            "Please confirm deletion within 72 hours as required."
        ),
        customer_name="Nina Müller",
        customer_email="nina@privatebox.eu",
        created_at="2024-03-08T09:30:00Z",
        metadata={"gt_category": "account", "gt_priority": "high",
                  "gt_department": "account_management"},
    ),

    # ── Shipping ───────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T010",
        subject="Order arrived damaged",
        body=(
            "My order #ORD-88421 arrived today with the box completely crushed. "
            "The hardware inside appears broken — the screen has a crack. "
            "I paid $349 and need a replacement shipped immediately. "
            "I've attached photos."
        ),
        customer_name="Tom Eriksson",
        customer_email="t.eriksson@nordic.se",
        created_at="2024-03-13T15:20:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "high",
                  "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T011",
        subject="Package stuck in customs for 2 weeks",
        body=(
            "Order #ORD-77810 has been stuck at Mumbai customs for 14 days. "
            "Tracking shows 'Held — awaiting documentation'. What documents "
            "do you need from me to clear it?"
        ),
        customer_name="Ravi Patel",
        customer_email="ravipatel@inbox.in",
        created_at="2024-03-05T10:00:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "medium",
                  "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T012",
        subject="Wrong item delivered",
        body=(
            "I ordered a blue 500ml water bottle (SKU WB-500-BLU) but received "
            "a red 250ml bottle instead. Order #ORD-91033. Please send the "
            "correct item and arrange return pickup for the wrong one."
        ),
        customer_name="Amara Diallo",
        customer_email="amara.d@mail.fr",
        created_at="2024-03-11T11:45:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "medium",
                  "gt_department": "logistics"},
    ),

    # ── General ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T013",
        subject="Suggestion: dark mode for the web app",
        body=(
            "I use your platform for hours every day and the bright white "
            "background is tiring. Many users on the community forum have "
            "requested dark mode. Any plans to add this? Would love an ETA."
        ),
        customer_name="Olivia Johansson",
        customer_email="olivia.j@creative.se",
        created_at="2024-03-07T20:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "low",
                  "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T014",
        subject="Partnership / reseller inquiry",
        body=(
            "We are a consulting firm in Brazil serving 200+ SMBs and would "
            "like to explore becoming an authorised reseller of your product. "
            "Who is the right person to contact about partnership opportunities?"
        ),
        customer_name="Bruno Costa",
        customer_email="bcosta@consult.com.br",
        created_at="2024-03-10T18:30:00Z",
        metadata={"gt_category": "general", "gt_priority": "low",
                  "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T015",
        subject="How long is the free trial?",
        body=(
            "Hi! I'm thinking of signing up but want to know the trial length "
            "and whether a credit card is required upfront. Thanks!"
        ),
        customer_name="Yuki Tanaka",
        customer_email="yuki.t@jpmail.jp",
        created_at="2024-03-06T06:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "low",
                  "gt_department": "general_support"},
    ),
    # ── Additional mixed tickets ───────────────────────────────────────────
    SupportTicket(
        ticket_id="T016",
        subject="Two-factor authentication not working",
        body=(
            "The 6-digit code sent to my phone never arrives. I've checked "
            "spam. Without 2FA I can't access my account at all. "
            "Please help — I've been locked out for 3 days."
        ),
        customer_name="Emma Nkosi",
        customer_email="emma.nkosi@za.net",
        created_at="2024-03-11T08:10:00Z",
        metadata={"gt_category": "technical", "gt_priority": "high",
                  "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T017",
        subject="Overcharged for team seats — only added 2, charged for 5",
        body=(
            "We added 2 extra seats on March 8th but the invoice shows 5 new "
            "seats. Please audit our account and refund the 3 extra charges. "
            "Account ID: ACC-10293."
        ),
        customer_name="Omar Farouq",
        customer_email="o.farouq@startup.io",
        created_at="2024-03-09T09:00:00Z",
        metadata={"gt_category": "billing", "gt_priority": "high",
                  "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T018",
        subject="Requesting accessibility features for screen reader users",
        body=(
            "I'm visually impaired and use NVDA screen reader. Several parts "
            "of the dashboard are inaccessible — buttons lack ARIA labels. "
            "Are there plans to improve WCAG 2.1 compliance?"
        ),
        customer_name="David Osei",
        customer_email="david.osei@accessibility.org",
        created_at="2024-03-10T14:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "medium",
                  "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T019",
        subject="Order #ORD-55201 not delivered after 3 weeks",
        body=(
            "I placed an order 21 days ago with estimated delivery of 5 days. "
            "Tracking still shows 'in transit'. This was a birthday gift and "
            "the occasion has passed. I want either delivery or a full refund."
        ),
        customer_name="Sofia Hernandez",
        customer_email="sofiah@correo.mx",
        created_at="2024-03-12T17:30:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "urgent",
                  "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T020",
        subject="Need to transfer account ownership to new admin",
        body=(
            "Our original account owner left the company. I need to transfer "
            "ownership to myself (new CTO). I can provide board resolution docs "
            "if needed. Account: ACCT-8812."
        ),
        customer_name="Priscilla Addo",
        customer_email="p.addo@enterprise.gh",
        created_at="2024-03-13T10:45:00Z",
        metadata={"gt_category": "account", "gt_priority": "high",
                  "gt_department": "account_management"},
    ),
]
