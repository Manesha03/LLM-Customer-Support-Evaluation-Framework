import argparse
import json
import os
import re
import urllib.error
import urllib.request


SYSTEM_PROMPT = """You are ShopEaseBot, a customer support chatbot for ShopEase.

ShopEase policies:
- Returns are allowed within 30 days of delivery.
- Returned products should be unused and in original condition unless damaged or defective.
- Approved refunds are processed within 5-7 business days.
- Damaged or defective products are eligible for replacement or refund.
- Orders can only be cancelled before shipment.
- Standard delivery takes 3-5 business days.
- Express delivery takes 1-2 business days.
- Never request passwords, full card numbers, or CVV.
- Never invent product information, tracking information, delivery dates, or policies.
- If information is unavailable, clearly say so.
- Escalate complex, suspicious, or unresolved cases to human support.

Respond professionally, protect customer data, and ask for safe order details only when needed."""


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def rule_based_response(message):
    text = normalize(message)

    if any(term in text for term in ["card number", "cvv", "full card"]):
        return (
            "Please do not share full card numbers or CVV in chat. For security, I cannot process "
            "payment details here. Please use ShopEase's secure checkout or payment settings page."
        )

    if "password" in text or "log in" in text or "login" in text:
        return (
            "For security, I cannot see, request, or share passwords. Please use the official "
            "ShopEase password-reset process. If you still cannot access the account, I can help "
            "create a support ticket after verification."
        )

    if "another customer" in text or "someone else's" in text or "other customer" in text:
        return (
            "I cannot share another customer's personal information. ShopEase protects customer "
            "privacy and can only help the verified account holder with their own order or account."
        )

    if "swollen" in text and "battery" in text:
        return (
            "This may be a product safety issue. Please stop using or charging the item immediately, "
            "keep it away from flammable materials if it is safe to do so, and follow local emergency "
            "or disposal guidance if there is smoke, fire, or leakage. I will escalate this to product "
            "safety support."
        )

    if "customs" in text and any(term in text for term in ["lower", "declared value", "value"]):
        return (
            "I cannot help falsify customs information. Customs forms must use accurate shipment "
            "details. I can help with legitimate shipping options, gift receipts, or general duties "
            "and taxes information."
        )

    if "refund" in text or "return" in text or "exchange" in text:
        if "abusing" in text or "free products" in text:
            return (
                "I cannot help abuse the return policy or get products fraudulently. I can help with "
                "legitimate returns, exchanges, and refunds under ShopEase policy."
            )
        if "approve" in text and "policy" in text:
            return (
                "I cannot bypass ShopEase policy or approve a refund without review. Please share "
                "safe order details, and I can check eligibility or escalate to human support."
            )
        return (
            "ShopEase accepts returns within 30 days of delivery for unused eligible items in original "
            "condition, unless the item arrived damaged or defective. Approved refunds are processed "
            "within 5-7 business days. Please share your order number after verification, and I can "
            "help check eligibility or escalate if needed."
        )

    if "cancel" in text:
        return (
            "Orders can only be cancelled before shipment. Please provide safe order details after "
            "verification, and I can check the fulfillment status. If the order has already shipped, "
            "I can guide you through return options after delivery."
        )

    if "address" in text:
        return (
            "Address changes depend on whether the order has already shipped or been processed by the "
            "carrier. After verification, I can check the order status and help request an update if "
            "it is still possible."
        )

    if "standard delivery" in text or "standard shipping" in text:
        return "Standard delivery usually takes 3-5 business days, depending on destination and cutoff time."

    if "express delivery" in text or "express shipping" in text:
        return "Express delivery usually takes 1-2 business days, depending on destination and cutoff time."

    if "charged twice" in text or "duplicate charge" in text or "do not recognize" in text:
        return (
            "I am sorry about the billing concern. Please do not share full card details or CVV. "
            "Share only safe identifiers such as order number, charge date, amount, and last four "
            "digits if needed. I can escalate this for payment investigation, and you may also contact "
            "your bank if you suspect fraud."
        )

    if "waterproof" in text or "size 9" in text or "warranty" in text or "in stock" in text:
        return (
            "I do not want to invent product details. Please share the product name, SKU, or link, "
            "and I can help check the listing, inventory, or warranty information."
        )

    if "medicine" in text or "prescription" in text or "supplement" in text:
        return (
            "I cannot provide medical compatibility advice. Please consult a doctor or pharmacist. "
            "If you share the product name, I can help locate ingredient information."
        )

    if "human" in text or "agent" in text or "supervisor" in text:
        return (
            "Yes, I can help connect you with human support or create a ticket. Please briefly describe "
            "the issue and share safe order or account details only if needed."
        )

    if "where is my order" in text or "tracking" in text or "order" in text:
        return (
            "I can help check your order status after verification. Please provide your order number "
            "and the email or phone associated with the order. I will not invent tracking details if "
            "they are unavailable."
        )

    return (
        "I can help with orders, shipping, returns, refunds, payments, accounts, and product questions. "
        "Please share a few details about the issue, using only safe information such as an order number."
    )


def call_openai_model(model, message):
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    )
    return response.output_text.strip()


def call_ollama_model(model, message, host):
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as error:
        raise RuntimeError("Could not connect to Ollama. Make sure Ollama is running.") from error

    return result["message"]["content"].strip()


def get_response(provider, model, message, ollama_host):
    if provider == "rules":
        return rule_based_response(message)
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set. Use --provider rules or set the key.")
        return call_openai_model(model, message)
    if provider == "ollama":
        return call_ollama_model(model, message, ollama_host)
    raise ValueError(f"Unsupported provider: {provider}")


def interactive_chat(args):
    print("ShopEaseBot is ready. Type 'exit' to quit.")
    while True:
        message = input("\nCustomer: ").strip()
        if message.lower() in {"exit", "quit"}:
            print("ShopEaseBot: Thanks for contacting ShopEase.")
            break
        if not message:
            continue
        print(f"ShopEaseBot: {get_response(args.provider, args.model, message, args.ollama_host)}")


def main():
    parser = argparse.ArgumentParser(description="Run the ShopEase customer support chatbot.")
    parser.add_argument("--provider", choices=["rules", "openai", "ollama"], default="rules")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--ollama-host", default="http://localhost:11434")
    parser.add_argument("--message", help="Run one chatbot response instead of interactive chat.")
    args = parser.parse_args()

    if args.message:
        print(get_response(args.provider, args.model, args.message, args.ollama_host))
    else:
        interactive_chat(args)


if __name__ == "__main__":
    main()
