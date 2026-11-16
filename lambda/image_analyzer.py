import json
import os
import boto3
import base64
import urllib.request
import urllib.error

rekognition = boto3.client("rekognition")
bedrock_runtime = boto3.client("bedrock-runtime")


def generate_with_qwen_groq(labels, api_key):
    """
    Generates a natural descriptive sentence using Qwen 3.8 on Groq's high-speed LPU.
    """
    prompt = (
        f"You are an AI vision assistant. Based on these detected image labels: {', '.join(labels)}. "
        f"Generate ONE concise, natural, and vivid English sentence describing what is in the scene. "
        f"Output ONLY the sentence, without conversational filler."
    )

    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 80,
        "temperature": 0.6
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "VISIO-Image-Analyzer/1.0"
        },
        data=json.dumps(payload).encode("utf-8"),
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()


def generate_with_bedrock(labels):
    """
    Generates a sentence using AWS Bedrock (Mistral or Amazon Nova).
    """
    prompt = (
        f"<s>[INST] Based on these detected labels: {', '.join(labels)}. "
        f"Generate ONE clear and natural English sentence describing what is in the image. [/INST]"
    )

    bedrock_payload = {
        "prompt": prompt,
        "max_tokens": 80,
        "temperature": 0.5,
        "top_p": 0.9
    }

    bedrock_response = bedrock_runtime.invoke_model(
        body=json.dumps(bedrock_payload),
        modelId="mistral.mistral-small-2402-v1:0",
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(bedrock_response["body"].read())
    return response_body["outputs"][0]["text"].strip()


def lambda_handler(event, context):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    try:
        body = json.loads(event.get("body", "{}"))
        image_base64 = body.get("image")
        provider = body.get("provider", "qwen")  # default to qwen
        groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not image_base64:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "No image provided"})
            }

        image_bytes = base64.b64decode(image_base64)

        # 1. Detect labels with Amazon Rekognition
        rekognition_response = rekognition.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=80
        )

        labels = [label["Name"] for label in rekognition_response["Labels"]]

        if not labels:
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "labels": [],
                    "description": "No labels detected in the image."
                })
            }

        description = None
        engine_used = None

        # 2. Text generation via user-selected engine
        if provider == "qwen":
            if groq_api_key:
                try:
                    description = generate_with_qwen_groq(labels, groq_api_key)
                    engine_used = "Qwen 3.8 (Groq LPU)"
                except Exception as qwen_err:
                    print("Qwen on Groq failed:", str(qwen_err))
                    # Attempt fallback to Bedrock
                    try:
                        description = generate_with_bedrock(labels)
                        engine_used = "AWS Bedrock (Fallback)"
                    except Exception as fallback_err:
                        print("Fallback to Bedrock also failed:", str(fallback_err))
            else:
                description = f"Detected: {', '.join(labels)}. (Note: Set 'groq_api_key' in terraform.tfvars to enable Qwen 3.8 generative descriptions)."
                engine_used = "Rekognition Only (Qwen API Key Not Configured)"

        elif provider == "bedrock":
            try:
                description = generate_with_bedrock(labels)
                engine_used = "AWS Bedrock (Mistral)"
            except Exception as bedrock_err:
                print("Bedrock failed:", str(bedrock_err))
                # Attempt fallback to Qwen if key exists
                if groq_api_key:
                    try:
                        description = generate_with_qwen_groq(labels, groq_api_key)
                        engine_used = "Qwen 3.8 (Fallback)"
                    except Exception as fallback_qwen_err:
                        print("Fallback to Qwen also failed:", str(fallback_qwen_err))

        # Default fallback if LLM calls failed
        if not description:
            description = f"Detected in image: {', '.join(labels)}."
            engine_used = "AWS Rekognition"

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({
                "labels": labels,
                "description": description,
                "engine": engine_used
            })
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }
