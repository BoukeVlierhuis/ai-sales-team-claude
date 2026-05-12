# Objection Playbook

## Top Objections

### "We already have Mixpanel/Amplitude."
**Underlying concern:** "Why pay for another tool that looks at the same events?"
**Response:** Mixpanel and Amplitude tell you what happened. Lighthouse triggers what happens next. We sit downstream of your warehouse and your analytics tool — we read the same events, but we act on them via email, Slack, and in-app.
**Evidence:** Plotly Studio case study — they kept Amplitude and added us for the action layer.

### "Our engineering team needs to ship an SDK."
**Underlying concern:** "This will take three months we don't have."
**Response:** No SDK. We read from your existing warehouse (Snowflake/BigQuery/Redshift) or your Segment stream. Standard install is 90 minutes.
**Evidence:** Crowdstack went live in 2 days.

### "We're not big enough for this."
**Underlying concern:** Budget or perceived complexity.
**Response:** Starter is $1,200/month and turns on in an afternoon. The math: if you save your CSM 5 hours a week of manual onboarding outreach, the tool pays for itself.

### "Can we just build this in our existing email tool?"
**Underlying concern:** Avoiding tool sprawl.
**Response:** You can; teams who try usually come back inside 6 months. The thing that's hard to build is the event-to-play binding logic, not the email send. We've built that part 80 times.
