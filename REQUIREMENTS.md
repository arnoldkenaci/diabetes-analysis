# Proof-of-Concept Web App: Automated Dataset Analysis & Insights

Build a proof-of-concept web app that performs automated analysis on a dataset and provides actionable insights. The app should integrate:

- An SQL database (PostgreSQL)
- A notification service for alerts
- A live LLM API of your choice

---

## 🧪 Dataset Analysis

- **Dataset:** Use a dummy dataset of your choice  
  _Example: regional marketing campaign performance data (Google/Facebook Ads)_
- **Database:** Host the dataset in **PostgreSQL**
- **Automation:** Implement an automated analysis process  
  _Examples:_
  - Identify anomalies
  - Calculate metrics
  - Summarize trends
  - Triggered on schedule or specific events

---

## 📢 Notification

When the analysis finds significant results (e.g., anomalies, threshold-crossing values), send a notification to the user via **email**.

- **Notification includes:**
  - A short description of the findings
  - A link to the [🔎 Interactive Dashboard](#-interactive-dashboard)
  - Actionable recommendations based on findings

✅ **Do:** Use email or Slack for alerts  
❌ **Don’t:** Use browser-based notifications or in-app banners

---

## 🔎 Interactive Dashboard

Build a simple, interactive dashboard to display analysis results.

- **Features:**
  - View and filter the dataset
  - Highlight significant results
  - Display AI-generated recommendations inline

---

## 🤖 AI Integration

Use a **free LLM API** to:

- Generate **recommendations** based on data insights
- Summarize dataset trends in **natural language**

_Refer to a list of available free LLM APIs_

---

## 🚀 Hosting

- The web application should **run locally**

---

## 🛠️ Tech Stack

- **Backend:** Python with PostgreSQL integration
- **Frontend:** React, Angular, or Vue
- **Notification Service:** Any (email, Slack, etc.)
- **AI:** Live LLM API

---

## 📄 README Instructions

Include a `README.md` with:

- Setup instructions for running and testing the app locally
- Key architectural decisions
- Assumptions made during development

---

## ⚠️ Constraints

- Notifications must only trigger when **meaningful findings** are detected
- Implement **rate limiting** for API calls to the LLM

---

## ➕ Additions

Adding features beyond the listed requirements is encouraged.

---

## 💡 Tips

Be prepared to discuss:

- Additional features you believe would enhance this app
- How you would implement those features in future iterations
