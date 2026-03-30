import asyncio
from app.db.supabase_client import supabase
from app.services.embedding_service import get_embedding

# Sample FAQ data
SAMPLE_FAQS = [
    {"question": "How do I find a therapist?", "answer": "You can find a therapist by searching our directory, filtered by specialty, location, and insurance. Alternatively, we can provide personalized recommendations through a brief matching questionnaire."},
    {"question": "What is Cognitive Behavioral Therapy (CBT)?", "answer": "CBT is a common type of talk therapy that helps you become aware of inaccurate or negative thinking so you can view challenging situations more clearly and respond to them in a more effective way."},
    {"question": "Do you accept insurance?", "answer": "Yes, many of our therapists are in-network with major insurance providers like Blue Cross, Aetna, and Cigna. You can verify your specific coverage on our billing page."},
    {"question": "How long is a typical therapy session?", "answer": "Standard individual therapy sessions usually last between 45 to 50 minutes. Some therapists offer longer sessions for couples or families upon request."},
    {"question": "Is online therapy effective?", "answer": "Yes, research indicates that tele-therapy is just as effective as in-person sessions for many common conditions like anxiety and depression, with the added benefit of convenience."},
    {"question": "What if I don't click with my therapist?", "answer": "It's completely normal to take a few tries to find the right fit. We offer easy switching to a new therapist through your dashboard at no additional cost."},
    {"question": "How much does therapy cost without insurance?", "answer": "Out-of-pocket rates vary by therapist but typically range from $100 to $250 per session. Some therapists offer sliding scale fees based on income."},
    {"question": "Can I get a diagnosis through your platform?", "answer": "Yes, our licensed psychologists and psychiatrists can provide clinical diagnoses after thorough assessments, which can be shared with your primary care physician if requested."},
    {"question": "Is my privacy protected?", "answer": "Absolutely. We use HIPAA-compliant technology and end-to-end encryption for all video sessions and communications to ensure your data and conversations remain private."},
    {"question": "What is the difference between a psychologist and a psychiatrist?", "answer": "Psychologists primarily use talk therapy and behavioral interventions, while psychiatrists are medical doctors who can prescribe medication in addition to providing therapy."}
]

async def seed_data():
    print("Seeding FAQs...")
    for item in SAMPLE_FAQS:
        print(f"Adding: {item['question']}")
        embedding = await get_embedding(item['question'] + " " + item['answer'])
        data = {
            "question": item['question'],
            "answer": item['answer'],
            "embedding": embedding
        }
        await supabase.table("faqs").insert(data).execute()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
