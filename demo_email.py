#!/usr/bin/env python3
"""
Demo Cold Email Generator
This script shows what the cold email generation would look like
without requiring an OpenAI API call.
"""

import os
import pandas as pd
import chromadb
from typing import Dict, Any, List

def initialize_chroma_collection() -> chromadb.Collection:
    """Initialize ChromaDB collection for portfolio."""
    try:
        client = chromadb.PersistentClient(path="vectorstore")
        collection = client.get_or_create_collection(
            name="portfolio",
            metadata={"hnsw:space": "cosine"}
        )
        return collection
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

def populate_portfolio(collection: chromadb.Collection, df: pd.DataFrame) -> None:
    """Populate the collection with portfolio data."""
    try:
        # Add new data (don't clear existing to avoid ChromaDB issues)
        for idx, row in df.iterrows():
            collection.add(
                documents=[row['Techstack']],
                metadatas=[{"links": row['Links']}],
                ids=[f"demo_{idx}"]  # Use unique IDs
            )
        print(f"Added {len(df)} portfolio items to collection")
    except Exception as e:
        print(f"Error populating portfolio: {e}")
        raise

def get_relevant_links(collection: chromadb.Collection, skills: List[str], n_results: int = 2) -> List[Dict[str, Any]]:
    """Get relevant portfolio links based on skills."""
    try:
        query_text = " ".join(skills)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        links = []
        for i in range(len(results['metadatas'][0])):
            links.append({
                'links': results['metadatas'][0][i]['links']
            })
        return links
    except Exception as e:
        print(f"Error getting relevant links: {e}")
        raise

def demo_cold_email(job: Dict[str, Any], links: List[Dict[str, Any]]) -> str:
    """Generate a demo cold email based on job description and portfolio links."""
    
    # This is what the AI would generate
    demo_email = f"""
Subject: Senior Software Engineer Opportunity - AtliQ's Proven Solutions

Dear Hiring Manager,

I hope this email finds you well. I came across your opening for a {job['role']} position and was immediately drawn to the opportunity to contribute to your team's success.

At AtliQ, we specialize in AI & Software Consulting, helping businesses automate and optimize their processes through scalable solutions that reduce costs and improve efficiency. With our extensive experience in delivering enterprise-grade applications, I believe we can provide exceptional value to your organization.

Based on your requirements for {job['experience']} experience and expertise in {', '.join(job['skills'])}, I'd like to highlight some relevant projects from our portfolio:

"""
    
    for link in links:
        demo_email += f"• {link['links']}\n"
    
    demo_email += f"""
These projects demonstrate our capabilities in {', '.join(job['skills'][:2])} and showcase our ability to deliver robust, scalable solutions that drive business growth.

I would welcome the opportunity to discuss how AtliQ can support your {job['role']} needs and explore potential collaboration opportunities. Would you be available for a brief call next week to discuss your requirements in more detail?

Thank you for considering AtliQ for your software development needs.

Best regards,
Anu
Business Development Executive | AtliQ
Email: anu@atliq.com
Phone: +1 (555) 123-4567
"""
    
    return demo_email.strip()

def main():
    """Main function to demonstrate the email generation process."""
    try:
        print("🚀 Cold Email Generator Demo")
        print("=" * 50)
        
        print("\n📋 Sample Job Description:")
        sample_job = {
            "role": "Senior Software Engineer",
            "experience": "5+ years",
            "skills": ["Python", "React", "Node.js", "MongoDB"],
            "description": "We are looking for a Senior Software Engineer to join our team. The ideal candidate will have strong experience in full-stack development, with expertise in Python, React, Node.js, and MongoDB. They will be responsible for designing and implementing scalable solutions, mentoring junior developers, and contributing to architectural decisions."
        }
        
        print(f"Role: {sample_job['role']}")
        print(f"Experience: {sample_job['experience']}")
        print(f"Skills: {', '.join(sample_job['skills'])}")
        
        print("\n🗄️ Initializing ChromaDB collection...")
        collection = initialize_chroma_collection()
        
        print("\n📊 Reading portfolio data...")
        df = pd.read_csv("my_portfolio.csv")
        
        print("\n💾 Populating portfolio collection...")
        populate_portfolio(collection, df)
        
        print("\n🔍 Getting relevant links...")
        links = get_relevant_links(collection, sample_job['skills'])
        print(f"Found {len(links)} relevant portfolio links:")
        for link in links:
            print(f"  - {link['links']}")
        
        print("\n📧 Generating demo cold email...")
        email = demo_cold_email(sample_job, links)
        
        print("\n" + "=" * 80)
        print("📬 GENERATED COLD EMAIL:")
        print("=" * 80)
        print(email)
        print("=" * 80)
        
        print("\n✅ Demo completed successfully!")
        print("\n💡 To use the real AI-powered version:")
        print("1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Add billing information to your OpenAI account")
        print("3. Set OPENAI_API_KEY in your .env file")
        print("4. Run: python emailgen.py")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
