# 👁️ VISIO — Serverless Multi-Provider AI Vision Pipeline

> An enterprise-grade, fault-tolerant computer vision and generative AI platform provisioned 100% via **Infrastructure as Code (Terraform)** on **AWS**, featuring a multi-provider AI router powered by **Amazon Rekognition**, **Groq LPUs (Qwen 3.8)**, and **AWS Bedrock**.

---

## 🏗️ Architecture Overview

```
[ User Browser (SPA) ]
        │
        ▼ (HTTPS)
[ S3 Static Website ]  ──>  [ API Gateway (REST + CORS) ]
                                      │
                                      ▼
                            [ AWS Lambda Backend ]
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼ (Step 1: Visual Detection)              ▼ (Step 2: Sentence Generation)
        [ Amazon Rekognition ]                    [ Multi-Model Router ]
        Detects labels (e.g., Lion, Wild)                  │
                                            ┌──────────────┴──────────────┐
                                            ▼ (Option A)                  ▼ (Option B)
                                   [ Groq Cloud LPU ]             [ AWS Bedrock ]
                                    Qwen 3.8 (150ms)           Amazon Nova / Mistral
```

---

## ✨ Key Features

* **100% Automated Infrastructure as Code (IaC):** Single-command deployment (`terraform apply`) for IAM roles, Lambda compute, API Gateway routing, S3 web hosting, and dynamic hash-based frontend file syncing (`etag = filemd5(...)`).
* **Multi-Provider AI Routing:** Avoids vendor lock-in by allowing users to toggle in real-time between **Groq LPU (Qwen 3.8)** for ultra-low latency and **AWS Bedrock** for native enterprise workloads.
* **Fault-Tolerant Graceful Degradation:** The pipeline automatically catches provider restrictions and falls back safely, ensuring visual labels render even during upstream model rate-limits.
* **Modern Dark-Mode UI:** Zero-dependency Single Page Application (HTML5, modern CSS variables, Vanilla JS) communicating with API Gateway via asynchronous REST calls.
* **Cost & Security Optimized:** Zero 24/7 idle server costs (pure serverless pay-per-use), IAM least-privilege policies, and zero hardcoded credentials.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **IaC & Automation** | Terraform (HashiCorp AWS, Random & Archive Providers) |
| **Cloud Provider** | Amazon Web Services (AWS) |
| **Compute** | AWS Lambda (Python 3.9 Runtime) |
| **API & Routing** | Amazon API Gateway (REST API with CORS Preflight) |
| **Computer Vision** | Amazon Rekognition (`DetectLabels`) |
| **Generative LLMs** | Groq LPU (`qwen/qwen3.8-27b`) & AWS Bedrock (`amazon.nova-micro-v1:0`) |
| **Frontend Storage** | Amazon S3 (Static Website Configuration) |
| **Frontend UI** | HTML5, Vanilla JavaScript (ES6+ Fetch API), CSS3 (Modern Glassmorphism) |

---

## 🚀 Quickstart & Deployment

### Prerequisites
* [AWS CLI installed & configured](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) (`aws configure`)
* [Terraform >= 1.5](https://www.terraform.io/downloads.html) installed
* Free API key from [Groq Cloud](https://console.groq.com/keys)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/visio-ai-vision-pipeline.git
cd visio-ai-vision-pipeline/terraform
```

### 2. Configure Variables
Create a `terraform.tfvars` file (this is gitignored for security):
```hcl
aws_region   = "us-east-1"
groq_api_key = "gsk_your_actual_groq_api_key_here"
```

### 3. Deploy
```bash
terraform init
terraform apply -auto-approve
```

### 4. Open the Website
Terraform will output your live URL:
```text
Outputs:
frontend_website_endpoint = "ai-image-analyzer-frontend-xxxx.s3-website-us-east-1.amazonaws.com"
api_gateway_url = "https://xxxx.execute-api.us-east-1.amazonaws.com/v1"
```
Click the frontend endpoint, upload any image, and see real-time AI vision analysis!
