# LLM Evaluation Framework for an E-Commerce Customer Support Chatbot

This project evaluates whether an LLM-powered customer support chatbot can provide correct, relevant, safe, and useful responses for a fictional e-commerce store.

## Application Chosen

Customer Support Chatbot for a fictional e-commerce store named **ShopEase**.

The chatbot is evaluated on its ability to answer customer questions about orders, delivery, refunds, payments, accounts, products, promotions, accessibility, safety, and escalation requests.

## Step 1: Scenario and Policies

Before scoring an LLM, the project defines ShopEase's business rules in `docs/business_policies.md`. These policies are the source of truth for expected answers.

They cover:

- Orders and tracking
- Delivery and shipping
- Returns and refunds
- Payments and billing
- Account support and privacy
- Product information
- Ambiguous and edge cases
- Safety and adversarial requests

## Project Contents

- `docs/business_policies.md` - fictional store scenario, business policies, and evaluation criteria.
- `data/test_cases.csv` - 60 ShopEase test cases with expected outputs and blank evaluation fields.
- `data/customer_support_test_cases.json` - 55 independently designed test cases with expected outputs and scoring criteria.
- `data/model_outputs.csv` - sample LLM responses used for the included evaluation run.
- `src/evaluate.py` - scoring script that calculates quantitative metrics and failure patterns.
- `reports/final_technical_report.md` - final technical report with methodology, results, and recommendations.
- `reports/evaluation_results.json` - generated evaluation output from the sample run.

## Metrics

The evaluator calculates:

- Overall pass rate
- Average score
- Category-level score
- Risk-level score
- Escalation accuracy
- Policy compliance rate
- Safety compliance rate
- Hallucination rate
- Failure pattern counts

Each test case is scored against required answer elements, forbidden answer elements, escalation expectations, policy compliance, and safety requirements.

## Step 2: Test Cases

The main Step 2 dataset is `data/test_cases.csv`. It contains 60 independently designed test cases with this distribution:

| Category | Test Cases |
|---|---:|
| Orders & Tracking | 10 |
| Delivery & Shipping | 10 |
| Returns & Refunds | 10 |
| Payments & Billing | 10 |
| Account Support | 8 |
| Product Information | 5 |
| Ambiguous / Edge Cases | 4 |
| Safety / Adversarial | 3 |
| **Total** | **60** |

The CSV includes:

- `test_id`
- `category`
- `customer_message`
- `expected_output`
- `expected_criteria`
- `actual_llm_output`
- `correctness_score`
- `relevance_score`
- `completeness_score`
- `policy_compliance`
- `hallucination`
- `safety`
- `task_success`
- `failure_reason`

## Run Evaluation

### Step 3 Runner

Use this command to test the evaluation pipeline without calling an API:

```bash
python src/run_evaluation.py --dry-run
```

This creates:

- `results/evaluation_results.csv`
- `results/summary.txt`

To run against an API-accessible OpenAI model, first install dependencies:

```bash
pip install -r requirements.txt
```

Then set your API key in PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Run the 60 ShopEase prompts:

```bash
python src/run_evaluation.py --model gpt-5-mini
```

To use hybrid scoring with an LLM judge for correctness, relevance, and completeness:

```bash
python src/run_evaluation.py --model gpt-5-mini --judge-model gpt-5-mini
```

The tested model name and UTC test date are saved in `results/summary.txt`.

### Earlier JSON Evaluator

```bash
python src/evaluate.py --cases data/customer_support_test_cases.json --outputs data/model_outputs.csv --report reports/evaluation_results.json
```

The script reads model outputs from CSV. To evaluate a different LLM, replace `data/model_outputs.csv` with responses from that model while keeping the same `case_id` values.

## CSV Format

```csv
case_id,response
CS001,"Your response here"
```

## Summary Result From Included Sample Run

The included sample outputs represent a moderately capable customer support chatbot. They are intentionally imperfect so the framework can demonstrate failure detection and pattern analysis.
