"""
Extended ticket bank — 30 tickets including hard multi-issue scenarios.
"""

from env.models import SupportTicket

TICKET_BANK: list[SupportTicket] = [
    # ── Billing ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T001", subject="Double charged on my last invoice",
        body="Hi, I noticed I was charged twice for my subscription this month. The amounts are $29.99 on March 3rd and again on March 5th. Could you please refund the duplicate charge? My account is under priya.sharma@email.com. Thank you.",
        customer_name="Priya Sharma", customer_email="priya.sharma@email.com",
        created_at="2024-03-06T09:14:00Z",
        metadata={"gt_category": "billing", "gt_priority": "high", "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T002", subject="Need receipt for tax purposes",
        body="Hello, I need an official receipt for all my payments in 2023 for my annual tax return. Could you send a consolidated PDF to my email? Account: carlos.ruiz@domain.net",
        customer_name="Carlos Ruiz", customer_email="carlos.ruiz@domain.net",
        created_at="2024-01-15T14:22:00Z",
        metadata={"gt_category": "billing", "gt_priority": "medium", "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T003", subject="Unexpected charge after cancellation",
        body="I cancelled my account on February 28th but was still charged $49 on March 1st. I have the cancellation confirmation email. This is unacceptable and I want a full refund immediately.",
        customer_name="Ahmed Hassan", customer_email="a.hassan@webmail.com",
        created_at="2024-03-04T11:05:00Z",
        metadata={"gt_category": "billing", "gt_priority": "urgent", "gt_department": "billing_team"},
    ),

    # ── Technical ──────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T004", subject="App keeps crashing on iOS 17",
        body="Since I updated to iOS 17 the app crashes every time I try to open the analytics dashboard. I've reinstalled twice. Device: iPhone 14 Pro, App version 4.2.1. Crash happens within 3 seconds.",
        customer_name="Li Wei", customer_email="liwei@personal.io",
        created_at="2024-03-10T08:30:00Z",
        metadata={"gt_category": "technical", "gt_priority": "high", "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T005", subject="API returning 500 errors on bulk import",
        body="Our integration is failing. POST /v2/import returns HTTP 500 when the payload exceeds 500 records. Works fine under that. We're on the Business plan. This is blocking our nightly ETL job.",
        customer_name="Sarah Okonkwo", customer_email="sarah@techcorp.io",
        created_at="2024-03-11T22:45:00Z",
        metadata={"gt_category": "technical", "gt_priority": "urgent", "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T006", subject="How do I export data to CSV?",
        body="I've been looking through the settings but can't find the CSV export option that was mentioned in your tutorial video. Could you point me in the right direction?",
        customer_name="James Park", customer_email="jpark@gmail.com",
        created_at="2024-03-07T16:00:00Z",
        metadata={"gt_category": "technical", "gt_priority": "low", "gt_department": "tech_support"},
    ),

    # ── Account ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T007", subject="Cannot log in — account locked",
        body="I've been locked out of my account since this morning. I tried resetting the password but the reset email never arrives. I have a presentation in 2 hours and need access urgently.",
        customer_name="Fatima Al-Zahra", customer_email="fatima.z@company.ae",
        created_at="2024-03-12T07:55:00Z",
        metadata={"gt_category": "account", "gt_priority": "urgent", "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T008", subject="Want to upgrade to Enterprise plan",
        body="Our team has grown to 50 people and we need the Enterprise features (SSO, audit logs, dedicated support). Can you send pricing details and connect me with a sales rep?",
        customer_name="Michael Chen", customer_email="mchen@bigcorp.com",
        created_at="2024-03-09T13:10:00Z",
        metadata={"gt_category": "account", "gt_priority": "medium", "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T009", subject="Delete my account and all data",
        body="Please delete my account and all associated data under GDPR Article 17 (right to erasure). My email is nina@privatebox.eu. Please confirm deletion within 72 hours as required.",
        customer_name="Nina Müller", customer_email="nina@privatebox.eu",
        created_at="2024-03-08T09:30:00Z",
        metadata={"gt_category": "account", "gt_priority": "high", "gt_department": "account_management"},
    ),

    # ── Shipping ───────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T010", subject="Order arrived damaged",
        body="My order #ORD-88421 arrived today with the box completely crushed. The hardware inside appears broken — the screen has a crack. I paid $349 and need a replacement shipped immediately.",
        customer_name="Tom Eriksson", customer_email="t.eriksson@nordic.se",
        created_at="2024-03-13T15:20:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "high", "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T011", subject="Package stuck in customs for 2 weeks",
        body="Order #ORD-77810 has been stuck at Mumbai customs for 14 days. Tracking shows 'Held — awaiting documentation'. What documents do you need from me to clear it?",
        customer_name="Ravi Patel", customer_email="ravipatel@inbox.in",
        created_at="2024-03-05T10:00:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "medium", "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T012", subject="Wrong item delivered",
        body="I ordered a blue 500ml water bottle (SKU WB-500-BLU) but received a red 250ml bottle instead. Order #ORD-91033. Please send the correct item and arrange return pickup.",
        customer_name="Amara Diallo", customer_email="amara.d@mail.fr",
        created_at="2024-03-11T11:45:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "medium", "gt_department": "logistics"},
    ),

    # ── General ────────────────────────────────────────────────────────────
    SupportTicket(
        ticket_id="T013", subject="Suggestion: dark mode for the web app",
        body="I use your platform for hours every day and the bright white background is tiring. Many users on the community forum have requested dark mode. Any plans to add this?",
        customer_name="Olivia Johansson", customer_email="olivia.j@creative.se",
        created_at="2024-03-07T20:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "low", "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T014", subject="Partnership / reseller inquiry",
        body="We are a consulting firm in Brazil serving 200+ SMBs and would like to explore becoming an authorised reseller of your product. Who is the right person to contact?",
        customer_name="Bruno Costa", customer_email="bcosta@consult.com.br",
        created_at="2024-03-10T18:30:00Z",
        metadata={"gt_category": "general", "gt_priority": "low", "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T015", subject="How long is the free trial?",
        body="Hi! I'm thinking of signing up but want to know the trial length and whether a credit card is required upfront. Thanks!",
        customer_name="Yuki Tanaka", customer_email="yuki.t@jpmail.jp",
        created_at="2024-03-06T06:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "low", "gt_department": "general_support"},
    ),

    # ── HARD: Multi-issue tickets ──────────────────────────────────────────
    SupportTicket(
        ticket_id="T016",
        subject="FURIOUS: Charged twice, account locked, data missing — I want answers NOW",
        body=(
            "I am absolutely furious. THREE things have gone wrong simultaneously:\n\n"
            "1. I was charged $99 twice this month (March 3 and March 5). That is $99 stolen from me.\n"
            "2. When I tried to log in to check my invoices, I found my account is LOCKED. "
            "Password reset emails are not arriving.\n"
            "3. My entire project history from February is GONE. Three weeks of work — vanished.\n\n"
            "I am a paying Enterprise customer (Account: ENT-5521) and this is completely unacceptable. "
            "If this is not resolved within 24 hours I will be filing a chargeback and contacting my lawyer. "
            "I want a senior manager to call me immediately."
        ),
        customer_name="Marcus Webb", customer_email="marcus.webb@enterprise.com",
        created_at="2024-03-13T08:00:00Z",
        metadata={"gt_category": "billing", "gt_priority": "urgent", "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T017",
        subject="Production API down + wrong billing + need data export urgently",
        body=(
            "We have a production emergency. Our entire platform is down because your API "
            "is returning 503 errors since 6am. We have 10,000 users affected.\n\n"
            "On top of this, we noticed our invoice this month is $2,400 instead of the agreed $800. "
            "We are on the Startup plan — someone has incorrectly upgraded us.\n\n"
            "We also need an emergency data export of all our user records in CSV format "
            "before end of business today for a compliance audit.\n\n"
            "This needs IMMEDIATE attention. Every minute of downtime costs us $500."
        ),
        customer_name="Aisha Kamara", customer_email="aisha.cto@startup.io",
        created_at="2024-03-12T09:15:00Z",
        metadata={"gt_category": "technical", "gt_priority": "urgent", "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T018",
        subject="Damaged delivery + wrong item + refund not received from 3 weeks ago",
        body=(
            "I have been patient but I cannot wait anymore. Three separate issues:\n\n"
            "Order #ORD-44201 (3 weeks ago): I requested a refund for a damaged item. "
            "Still no refund after 21 days. You said 5-7 business days.\n\n"
            "Order #ORD-55810 (last week): Delivered completely wrong product. "
            "I ordered a laptop stand but received a mousepad.\n\n"
            "Order #ORD-66123 (yesterday): Package arrived with the box opened and "
            "the product clearly used. This is disgusting.\n\n"
            "I want all three issues resolved AND compensation for the time I have wasted."
        ),
        customer_name="Elena Vasquez", customer_email="elena.v@home.es",
        created_at="2024-03-14T14:30:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "urgent", "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T019",
        subject="Account takeover attempt + unauthorized charges + need GDPR erasure",
        body=(
            "I believe my account has been compromised. I received login notifications "
            "from IP addresses in countries I have never visited (Romania, Vietnam).\n\n"
            "I also see three unauthorized charges of $29.99 each in the past month "
            "that I did not make.\n\n"
            "Additionally, since I no longer feel safe using your platform, I want to "
            "invoke my GDPR right to erasure — please delete all my personal data "
            "within 72 hours and send written confirmation.\n\n"
            "This is a security emergency. Please escalate to your security team NOW."
        ),
        customer_name="Ingrid Svensson", customer_email="ingrid.s@secure.se",
        created_at="2024-03-13T22:00:00Z",
        metadata={"gt_category": "account", "gt_priority": "urgent", "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T020",
        subject="5 team members locked out + SSO broken + presentation in 1 hour",
        body=(
            "CRITICAL SITUATION. We have a board presentation in 60 minutes and "
            "5 of our 8 team members cannot log in. The SSO integration stopped "
            "working at 8am. Error: 'SAML assertion invalid'.\n\n"
            "Our IT admin (john.it@company.com) has tried reconfiguring the SSO "
            "settings but the portal keeps showing a 500 error when saving.\n\n"
            "We are on the Enterprise plan and were promised 99.9% uptime SLA. "
            "This is a direct SLA breach. We need this fixed in the next 30 minutes "
            "or we will be seeking SLA compensation."
        ),
        customer_name="Rachel Kim", customer_email="rachel.kim@corp.com",
        created_at="2024-03-14T08:45:00Z",
        metadata={"gt_category": "technical", "gt_priority": "urgent", "gt_department": "tech_support"},
    ),

    # ── Additional standard tickets ────────────────────────────────────────
    SupportTicket(
        ticket_id="T021", subject="Two-factor authentication not working",
        body="The 6-digit code sent to my phone never arrives. I've checked spam. Without 2FA I can't access my account at all. Please help — locked out for 3 days.",
        customer_name="Emma Nkosi", customer_email="emma.nkosi@za.net",
        created_at="2024-03-11T08:10:00Z",
        metadata={"gt_category": "technical", "gt_priority": "high", "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T022", subject="Overcharged for team seats",
        body="We added 2 extra seats on March 8th but the invoice shows 5 new seats. Please audit our account and refund the 3 extra charges. Account ID: ACC-10293.",
        customer_name="Omar Farouq", customer_email="o.farouq@startup.io",
        created_at="2024-03-09T09:00:00Z",
        metadata={"gt_category": "billing", "gt_priority": "high", "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T023", subject="Accessibility features request",
        body="I'm visually impaired and use NVDA screen reader. Several parts of the dashboard are inaccessible — buttons lack ARIA labels. Are there plans to improve WCAG 2.1 compliance?",
        customer_name="David Osei", customer_email="david.osei@accessibility.org",
        created_at="2024-03-10T14:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "medium", "gt_department": "general_support"},
    ),
    SupportTicket(
        ticket_id="T024", subject="Order not delivered after 3 weeks",
        body="I placed an order 21 days ago with estimated delivery of 5 days. Tracking still shows 'in transit'. This was a birthday gift and the occasion has passed. I want delivery or a full refund.",
        customer_name="Sofia Hernandez", customer_email="sofiah@correo.mx",
        created_at="2024-03-12T17:30:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "urgent", "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T025", subject="Need to transfer account ownership",
        body="Our original account owner left the company. I need to transfer ownership to myself (new CTO). I can provide board resolution docs if needed. Account: ACCT-8812.",
        customer_name="Priscilla Addo", customer_email="p.addo@enterprise.gh",
        created_at="2024-03-13T10:45:00Z",
        metadata={"gt_category": "account", "gt_priority": "high", "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T026", subject="Billing discrepancy on annual plan",
        body="I switched to the annual plan expecting a 20% discount as advertised. My invoice shows the full monthly rate x 12. I should have been charged $960 not $1,200. Please correct this.",
        customer_name="Thomas Bergmann", customer_email="t.bergmann@work.de",
        created_at="2024-03-08T11:30:00Z",
        metadata={"gt_category": "billing", "gt_priority": "medium", "gt_department": "billing_team"},
    ),
    SupportTicket(
        ticket_id="T027", subject="Integration with Slack not working",
        body="The Slack integration stopped posting notifications 3 days ago. I've reconnected it twice. Our workspace is on Slack Business+ and your app has the necessary permissions. Error: 'channel_not_found'.",
        customer_name="Keiko Nakamura", customer_email="keiko.n@designstudio.jp",
        created_at="2024-03-11T13:00:00Z",
        metadata={"gt_category": "technical", "gt_priority": "medium", "gt_department": "tech_support"},
    ),
    SupportTicket(
        ticket_id="T028", subject="Can I pause my subscription?",
        body="I'm going on sabbatical for 3 months and won't be using the service. Is there an option to pause my subscription instead of cancelling? I don't want to lose my data.",
        customer_name="Laura Fontaine", customer_email="laura.f@freelance.fr",
        created_at="2024-03-09T16:00:00Z",
        metadata={"gt_category": "account", "gt_priority": "low", "gt_department": "account_management"},
    ),
    SupportTicket(
        ticket_id="T029", subject="Express shipping not honoured",
        body="I paid $25 extra for express 2-day shipping on order #ORD-99201. It arrived on day 5. I want a refund of the express shipping fee since standard shipping would have been the same.",
        customer_name="Antoine Dubois", customer_email="a.dubois@paris.fr",
        created_at="2024-03-12T09:00:00Z",
        metadata={"gt_category": "shipping", "gt_priority": "medium", "gt_department": "logistics"},
    ),
    SupportTicket(
        ticket_id="T030", subject="Feature request: bulk export",
        body="We have 50,000 records and need to export them all. The current export caps at 1,000 per download. Could you add a bulk export option or an async export via email? This is blocking our monthly reporting.",
        customer_name="Nadia Petrov", customer_email="nadia.p@analytics.ru",
        created_at="2024-03-10T10:00:00Z",
        metadata={"gt_category": "general", "gt_priority": "medium", "gt_department": "general_support"},
    ),
]