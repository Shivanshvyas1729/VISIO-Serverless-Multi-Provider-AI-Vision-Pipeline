# ⚡ Essential Terraform Commands Cheat Sheet

The foundational lifecycle commands you need to know for day-to-day operations:

### 1. The Core Lifecycle (The "Big Four")
| Command | What it Does | When to Use |
| :--- | :--- | :--- |
| `terraform init` | Initializes project, downloads provider plugins (AWS, etc.), and sets up backend state. | First command in any new project or when adding new providers. |
| `terraform plan` | Generates an execution dry-run showing what will be created (`+`), modified (`~`), or deleted (`-`). | Always run before applying changes to inspect the blast radius. |
| `terraform apply` | Provisions or updates real cloud resources to match your code. Prompts for `yes`. | When you are satisfied with `terraform plan`. |
| `terraform destroy` | Tears down **all** resources created by this Terraform configuration. | When decommissioning a project or shutting down dev environments to stop billing. |

### 2. Code Quality & Formatting
| Command | What it Does | When to Use |
| :--- | :--- | :--- |
| `terraform fmt` | Rewrites all `.tf` files into the canonical HashiCorp formatting standard. | Before git commits or PR reviews. |
| `terraform fmt -check` | Checks if files are properly formatted without modifying them (returns non-zero if not). | Ideal for CI/CD linting checks. |
| `terraform validate` | Verifies syntax, provider constraints, and resource reference consistency without touching the cloud. | Immediately after writing or editing `.tf` files. |

### 3. State & Inspection
| Command | What it Does | When to Use |
| :--- | :--- | :--- |
| `terraform show` | Prints human-readable output of current state or a saved plan file. | When inspecting details of live provisioned resources. |
| `terraform state list` | Lists all resource identifiers currently tracked in your `terraform.tfstate`. | To quickly see what Terraform currently manages. |
| `terraform state show <resource>` | Shows all live attributes, IDs, and metadata for a specific resource. | E.g., `terraform state show aws_s3_bucket.frontend_bucket`. |
| `terraform output` | Displays the values of all declared `outputs.tf` (endpoints, ARNs, names). | To grab API URLs or bucket names without opening AWS Console. |
| `terraform refresh` | Updates the local state file against real cloud resources without modifying infrastructure. | When checking if resources were modified outside Terraform (drift detection). |

### 4. Advanced & Targeted Operations
| Command | What it Does | When to Use |
| :--- | :--- | :--- |
| `terraform plan -out=tfplan` | Saves the exact plan execution to a binary file. | Best practice in production / CI/CD pipelines. |
| `terraform apply tfplan` | Applies the exact saved plan file without prompting or re-evaluating. | Guarantees what was reviewed is what gets deployed. |
| `terraform apply -auto-approve` | Applies changes immediately without asking for manual `yes` confirmation. | Automation scripts and non-destructive dev testing. |
| `terraform apply -target=<resource>` | Targets a single specific resource to create/update while ignoring the rest. | For emergency hotfixes or debugging isolated resources. |
| `terraform workspace list / new / select` | Manages multiple isolated states (e.g., `dev`, `staging`, `prod`) from one codebase. | Multi-environment branching workflows. |

---

# 🚀 Cloud Architecture & Terraform Master Notes

---

## 📌 Section 0: Master Global Prompt (For AI Mentorship & Code Generation)

> **Instructions for Use:** Copy and paste the prompt below into any AI assistant (Antigravity System Prompt, ChatGPT Custom Instructions, Claude System Prompt, or `.cursorrules`) to guarantee high-quality, safe, cost-conscious, and unbroken Terraform code.

```markdown
You are a Principal Cloud Architect and Lead DevOps Engineer acting as my mentor and implementation partner.

### My Role:
I am the Lead Architect and System Designer. I define high-level requirements and business goals.

### Your Role:
You teach me the architectural mental model, enforce enterprise safety and cost guardrails, and provide complete, 100% runnable, unbroken Terraform code without omissions or placeholders.

---

### 🚨 NON-NEGOTIABLE CORE CONSTRAINTS

#### 1. ZERO-TRUNCATION RULE (Complete, Unbroken Code)
- NEVER use shortcuts like `/* ... remaining code here ... */`, `// add more methods`, or `# TODO`.
- NEVER omit required sub-resources (e.g., if you write an API Gateway, write every method, integration, response, and stage completely).
- Every outputted file must be 100% syntactically complete, valid HCL, and immediately executable with `terraform init` and `terraform apply`.
- Output each file clearly labeled under its own file header: `main.tf`, `variables.tf`, `outputs.tf`, etc.

#### 2. AGGRESSIVE COST GUARDRAILS (Never Surprise My Credit Card)
- **Mandatory Environment Flag:** Every project must include an `environment` variable (`dev` vs `prod`).
- **Dev-First Cost Optimization:** In `dev`, default to Free-Tier or the lowest possible cost:
  - RDS: `multi_az = false`, `instance_class = "db.t4g.micro"`, `skip_final_snapshot = true`.
  - Networking: Avoid creating multi-AZ NAT Gateways in `dev` ($32+/mo each). Use a single shared NAT Gateway or VPC Endpoints.
  - Compute: Burstable instances (`t4g`/`t3`), auto-scaling with `min_size = 0` or `1`.
  - CloudWatch Logs: Always set `retention_in_days = 7` (never default to infinite retention).
- **Cost Estimate Table:** For every architecture proposed, provide a realistic estimated monthly cost table comparing `dev` vs `prod`.

#### 3. STRICT SECURITY & BLAST RADIUS SAFETY
- **Zero Trust IAM:** Grant only the exact actions and resource ARNs required. Never use `Resource = "*"` with admin actions.
- **Network Isolation:** Databases and internal microservices MUST live in private subnets. Never allow inbound traffic from `0.0.0.0/0` on database (5432, 3306) or admin (22, 3389) ports.
- **Zero Hardcoded Secrets:** Passwords and keys must always be generated via `random_password` and stored in AWS Secrets Manager or SSM Parameter Store.
- **Data Protection:** 
  - Enable KMS encryption at rest for S3, RDS, and EBS by default.
  - Enable `deletion_protection = var.environment == "prod" ? true : false` on databases and state storage.

---

### 🔄 THE 4-PHASE RESPONSE PROTOCOL

Whenever I present an infrastructure task, you MUST structure your answer in these 4 phases:

#### Phase 1: The Architect's Mental Model ("What to Think")
1. **Data Flow:** Step-by-step tracing from user interaction to cloud services.
2. **Security & Boundary Map:** How traffic traverses public vs. private subnets and IAM trust boundaries.
3. **Dependency Graph:** What must be provisioned first, second, and last.

#### Phase 2: Human Developer Spec & Cost Comparison
- Formal Engineering Checklist (Components, Acceptance Criteria).
- Monthly Cost Comparison Table (`dev` vs `prod` breakdown with warnings on stealth charges).

#### Phase 3: Complete, Unbroken Terraform Code ([WHY / HOW / WHEN])
Provide complete, unbroken files (`variables.tf`, `main.tf`, `outputs.tf`).
For every major block or architectural decision, explain:
- **WHY:** Why is this resource needed? What problem does it solve? What breaks without it?
- **HOW:** How does Terraform configure it, and how does the cloud provider execute it?
- **WHEN:** When is this pattern ideal vs. when should an alternative be used?

#### Phase 4: Verification & Teardown Protocol
- Exact terminal commands to validate (`terraform validate`, `terraform plan`).
- How to safely destroy resources (`terraform destroy`) without leaving orphan disks or elastic IPs billing in the background.
```

---

## 🧠 Section 1: The Cloud Architect Mental Model ("What to Think")

Before writing any Terraform code, an engineer never jumps straight into HCL. They run through a **3-step mental pipeline**:

```
[ User Browser ]
       │
       ▼ (1. Trace the Data Flow)
[ S3 Static Website ]  ──>  [ API Gateway (/analyze) ]  ──>  [ Lambda Function ]  ──>  [ Rekognition / Bedrock ]
                                                                      │
                                                                      ▼ (2. Define Security Boundaries)
                                                               [ IAM Roles & Policies ]
```

### 1. Reverse Engineer the Data Flow
* Trace requests from end-user action down to storage/AI:
  * User visits a domain → Needs **S3 Static Website Hosting**.
  * User uploads image / submits data → Needs public HTTPS endpoint → **API Gateway**.
  * Request needs processing → Needs serverless compute → **AWS Lambda**.
  * Code calls external services → Needs **Amazon Rekognition** & **Amazon Bedrock**.

### 2. Map Security Boundaries (Least Privilege)
* AWS is **Zero-Trust**: Everything is denied by default.
* API Gateway cannot call Lambda without an explicit `aws_lambda_permission`.
* Lambda cannot write logs or call Bedrock without an `aws_iam_role` and attached `aws_iam_policy`.
* S3 is private by default; public website access requires explicit `aws_s3_bucket_public_access_block` adjustments and an `aws_s3_bucket_policy`.

### 3. Build the Dependency Graph (Terraform's DAG)
Terraform compiles resources into a Directed Acyclic Graph. Children must reference parent outputs:

```text
[ IAM Role ] ──> [ Lambda Function ] ──> [ API Gateway Integration ] ──> [ Deployment & Stage ]
```

---

## 📋 Section 2: Human Developer Spec & Checklist (RFC Ticket)

### Project: Serverless AI Image Analyzer (`terraform/` folder)

| Area | Resource Needed | Acceptance Criteria |
| :--- | :--- | :--- |
| **Config** | `variable.tf` | Dynamic region, environment flag (`dev`/`prod`), and project naming prefix. |
| **Security** | IAM Role & Policies | AssumeRole for `lambda.amazonaws.com`, CloudWatch log streams, Rekognition `DetectLabels`, and Bedrock `InvokeModel`. |
| **Compute** | AWS Lambda | Auto-packaged from `../lambda/`, Python 3.9 runtime, 30s timeout, SHA256 code hash tracking. |
| **API** | API Gateway (REST) | Endpoint `/analyze` (POST), `AWS_PROXY` pass-through, full CORS `OPTIONS` mock integration. |
| **Frontend** | S3 Bucket & Auto-Upload | Static site configuration (`index.html`), public read policy, randomized bucket suffix, and automated upload of `front-end/` files. |
| **Outputs** | `output.tf` | Export API Gateway Invoke URL and S3 Website Endpoint for immediate access. |

---

## 🔍 Section 3: Terraform Code Anatomy ([WHY / HOW / WHEN])

### Layer 1: Provider & Variables
* **WHY:** Pins API versions so future provider releases don't break infrastructure during CI/CD.
* **HOW:** Terraform downloads the binary provider from the HashiCorp Registry and executes AWS calls against `var.aws_region`.
* **WHEN:** Required for every Terraform root module.

### Layer 2: IAM Identity & Permissions
* **WHY:** Gives Lambda an identity (`sts:AssumeRole`) and grants access to CloudWatch, Rekognition, and Bedrock. Without this, runtime throws `AccessDeniedException`.
* **HOW:** `jsonencode()` generates valid AWS policy JSON. Policies are linked to the role via `aws_iam_role_policy_attachment`.
* **WHEN:** Every compute resource in AWS that accesses other services must have an attached IAM role.

### Layer 3: Serverless Compute & Dynamic Packaging
* **WHY:** Avoids manual zip uploads. Automatically detects file changes in code.
* **HOW:** `data.archive_file` zips `../lambda/`. `source_code_hash` triggers redeployment whenever local python code changes.
* **WHEN:** Ideal for microservices under 50MB. For larger machine learning packages, use container images on ECR.

### Layer 4: API Gateway & CORS Preflight
* **WHY:** Lambda has no public IP/URL. API Gateway provides public HTTPS routing, rate limiting, and CORS handling for browser apps.
* **HOW:**
  * `type = "AWS_PROXY"` passes full HTTP request payload to Lambda.
  * The `OPTIONS` method + `MOCK` integration returns preflight headers (`Access-Control-Allow-Origin: *`).
  * `triggers = sha1(...)` forces an API Gateway deployment when methods or integrations change.
* **WHEN:** Use REST API for enterprise features/CORS; consider HTTP API for ultra-simple, cheap low-latency proxying.

### Layer 5: S3 Static Web Hosting & Automatic Frontend Upload
* **WHY:** Eliminates 24/7 web server (EC2) costs for frontend hosting and removes manual S3 upload steps.
* **HOW:** `random_id` guarantees globally unique bucket names. `aws_s3_object` loops through `front-end/` files, computes MD5 hashes (`etag`), and assigns proper MIME types (`content_type`).
* **WHEN:** Perfect for Single Page Applications (React, Vue, vanilla HTML/JS).

---

## 🤝 Section 4: What AI Can Handle vs. "Extra Knowledge" You Need

```
You (Architect / Tech Lead)           AI (Junior DevOps Engine)         You (Operations & Safety)
 ┌──────────────────────┐             ┌────────────────────────┐        ┌───────────────────────┐
 │ 1. Define Spec &     │ ──────────> │ 2. Writes HCL Code,    │ ─────> │ 3. Run plan/apply &   │
 │    Architecture      │             │    Python & Frontend   │        │    verify state/costs │
 └──────────────────────┘             └────────────────────────┘        └───────────────────────┘
                                                   ▲                               │ (On AWS Errors)
                                                   │                               ▼
                                                   └────────────────────── Feed error back to AI
```

### What AI Can Handle 100%:
* Generating complete HCL resource syntax, variables, outputs, and JSON policies.
* Wiring complex integrations (API Gateway → Lambda → IAM).
* Generating backend code (`image_analyzer.py`) and frontend interfaces (`index.html`).

### The 4 Pieces of "Extra Knowledge" You Still Need:
1. **AWS CLI & Authentication:** Knowing how to configure AWS credentials (`aws configure`) and IAM credentials on your machine.
2. **Terraform Lifecycle & State:** Understanding `init`, `plan`, `apply`, `destroy`, and guarding the `terraform.tfstate` file from manual edits or accidental deletion.
3. **Reading Real AWS Errors:** Recognizing permission errors (`AccessDeniedException`), region availability limits, and feeding them back to AI for fixes.
4. **Cost Awareness & Blast Radius:** Never letting AI spin up expensive 24/7 resources in `dev` without your explicit review.

---

## 🗄️ Section 5: Multi-AZ AWS RDS Architecture & Cost Control

### Mental Model & Failover Mechanics:
* **Primary DB (AZ-a):** Active database handling all reads and writes.
* **Standby DB (AZ-b):** Synchronous replica in another physical data center.
* **Failover:** If AZ-a fails, AWS automatically updates the DNS record to point to AZ-b (~60s downtime, zero data loss).
* **Cost Impact:** Multi-AZ runs two instances 24/7 → **Doubles your database compute bill.**

### Developer Safeguards:
1. **The Dev vs. Prod Switch:**
   ```hcl
   multi_az            = var.environment == "prod" ? true : false
   instance_class      = var.environment == "prod" ? "db.r6g.large" : "db.t4g.micro"
   skip_final_snapshot = var.environment == "prod" ? false : true
   deletion_protection = var.environment == "prod" ? true : false
   ```
2. **DB Subnet Group Rule:** AWS strictly requires private subnets in **at least 2 distinct Availability Zones**, even for single-AZ instances.
3. **Security Group Chaining:** Never allow `0.0.0.0/0` on database ports. Only allow traffic from the Application Security Group:
   ```hcl
   security_groups = [aws_security_group.app_sg.id]
   ```
4. **Secrets Management:** Generate passwords dynamically via `random_password` and store them in `aws_secretsmanager_secret`.

---

## 🌐 Section 6: Amazon API Gateway Technical Reference

Amazon API Gateway is a fully managed AWS service that acts as a single "front door" for applications to access backend data and logic.

### Core Capabilities:
* **Backend Integrations:** Routes traffic to AWS Lambda, EC2, ECS, or HTTP endpoints.
* **Security & Auth:** Enforces HTTPS, IAM authentication, Amazon Cognito User Pools, and Lambda Authorizers.
* **Traffic Control:** Request throttling, rate limiting, and API key usage plans.
* **Observability:** Native CloudWatch logging and AWS X-Ray distributed tracing.

### Types of APIs Supported:

| API Type | Communication Model | Best Use Case | Key Features & Pricing |
| :--- | :--- | :--- | :--- |
| **HTTP API** | Synchronous (Request/Response) | High-performance, low-latency microservices | Up to 70% cheaper (~&#36;1.00/million requests), built-in OIDC/JWT auth. |
| **REST API** | Synchronous (Request/Response) | Enterprise APIs with full lifecycle needs | WAF integration, request validation, API keys, usage plans (~&#36;3.50/million requests). |
| **WebSocket API** | Stateful, Full-Duplex (Two-Way) | Real-time chat, dashboards, multiplayer games | Persistent connections, routes messages based on content payload. |

---
*Last Updated: 2026-11-17 | Maintained by DevOps & Cloud Architecture Team*
