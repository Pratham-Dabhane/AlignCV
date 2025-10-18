"""
Job Ingestion System - Phase 5/6

Scrapes and ingests jobs from multiple sources.
Normalizes data and stores in PostgreSQL.
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobScraper:
    """Base class for job scrapers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape jobs from source.
        
        Returns:
            List of normalized job dictionaries
        """
        raise NotImplementedError
    
    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw job data to standard format.
        
        Args:
            raw_data: Raw job data from source
            
        Returns:
            Normalized job dictionary
        """
        raise NotImplementedError
    
    def generate_job_id(self, title: str, company: str, url: str) -> str:
        """
        Generate unique job ID from job details.
        
        Args:
            title: Job title
            company: Company name
            url: Job URL
            
        Returns:
            Unique job ID (SHA-256 hash)
        """
        unique_string = f"{self.source_name}:{company}:{title}:{url}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]


class MockJobScraper(JobScraper):
    """
    Mock job scraper for testing.
    
    Returns sample job listings.
    """
    
    def __init__(self):
        super().__init__("mock")
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Return sample job listings."""
        logger.info("Generating mock job listings")
        
        sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp",
                "description": """We're looking for a Senior Software Engineer to join our team. 
                Requirements: 5+ years Python experience, FastAPI, PostgreSQL, AWS. 
                Responsibilities include building scalable APIs, mentoring junior developers, 
                and working with AI/ML systems. Strong knowledge of Docker, Kubernetes preferred.""",
                "url": "https://example.com/jobs/1",
                "location": "San Francisco, CA",
                "tags": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
                "salary_min": 150000,
                "salary_max": 200000,
                "employment_type": "full-time",
                "experience_level": "senior"
            },
            {
                "title": "Machine Learning Engineer",
                "company": "AI Innovations",
                "description": """Join our ML team building cutting-edge AI solutions. 
                Requirements: PhD or MS in CS/ML, TensorFlow/PyTorch, Python, cloud infrastructure. 
                Work on NLP, computer vision, and recommendation systems. 
                Experience with transformers, LLMs, and distributed training required.""",
                "url": "https://example.com/jobs/2",
                "location": "Remote",
                "tags": ["Machine Learning", "Python", "TensorFlow", "PyTorch", "NLP"],
                "salary_min": 180000,
                "salary_max": 250000,
                "employment_type": "full-time",
                "experience_level": "senior"
            },
            {
                "title": "Backend Developer",
                "company": "StartupXYZ",
                "description": """Looking for a backend developer to build our core platform. 
                Requirements: 3+ years experience with Node.js or Python, REST APIs, SQL databases. 
                You'll work on microservices, API design, and database optimization. 
                Familiarity with Redis, message queues, and CI/CD pipelines a plus.""",
                "url": "https://example.com/jobs/3",
                "location": "New York, NY",
                "tags": ["Python", "Node.js", "REST API", "SQL", "Redis"],
                "salary_min": 120000,
                "salary_max": 160000,
                "employment_type": "full-time",
                "experience_level": "mid"
            },
            {
                "title": "Data Scientist",
                "company": "DataCo",
                "description": """Seeking a Data Scientist to drive insights from large datasets. 
                Requirements: Strong Python, SQL, statistics, and ML knowledge. 
                Experience with pandas, scikit-learn, data visualization tools. 
                Build predictive models, analyze user behavior, create dashboards.""",
                "url": "https://example.com/jobs/4",
                "location": "Boston, MA",
                "tags": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas"],
                "salary_min": 130000,
                "salary_max": 180000,
                "employment_type": "full-time",
                "experience_level": "mid"
            },
            {
                "title": "Full Stack Developer",
                "company": "WebDev Inc",
                "description": """Full stack developer needed for web applications. 
                Requirements: React, TypeScript, Node.js, PostgreSQL, AWS/GCP. 
                Build responsive UIs, RESTful APIs, and deploy to cloud. 
                Experience with Next.js, GraphQL, and modern DevOps practices preferred.""",
                "url": "https://example.com/jobs/5",
                "location": "Austin, TX",
                "tags": ["React", "TypeScript", "Node.js", "PostgreSQL", "AWS"],
                "salary_min": 110000,
                "salary_max": 150000,
                "employment_type": "full-time",
                "experience_level": "mid"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudOps",
                "description": """DevOps Engineer to manage infrastructure and CI/CD. 
                Requirements: Kubernetes, Docker, Terraform, AWS/Azure, Python/Bash scripting. 
                Automate deployments, monitor systems, optimize performance. 
                Experience with monitoring tools, GitOps, and security best practices.""",
                "url": "https://example.com/jobs/6",
                "location": "Seattle, WA",
                "tags": ["Kubernetes", "Docker", "Terraform", "AWS", "Python"],
                "salary_min": 140000,
                "salary_max": 190000,
                "employment_type": "full-time",
                "experience_level": "senior"
            },
            {
                "title": "AI Research Scientist",
                "company": "Research Labs",
                "description": """AI Researcher to work on novel ML algorithms. 
                Requirements: PhD in CS/ML, publications in top venues, deep learning expertise. 
                Research areas: LLMs, multimodal learning, reinforcement learning. 
                Strong math background, PyTorch/JAX, and research engineering skills.""",
                "url": "https://example.com/jobs/7",
                "location": "Palo Alto, CA",
                "tags": ["AI", "Deep Learning", "PyTorch", "Research", "NLP"],
                "salary_min": 200000,
                "salary_max": 300000,
                "employment_type": "full-time",
                "experience_level": "senior"
            },
            {
                "title": "Frontend Developer",
                "company": "UX First",
                "description": """Frontend developer for beautiful, responsive web apps. 
                Requirements: React, Vue, or Angular, TypeScript, CSS/SASS, REST APIs. 
                Build component libraries, optimize performance, ensure accessibility. 
                Experience with design systems and modern build tools.""",
                "url": "https://example.com/jobs/8",
                "location": "Los Angeles, CA",
                "tags": ["React", "TypeScript", "CSS", "REST API", "UI/UX"],
                "salary_min": 100000,
                "salary_max": 140000,
                "employment_type": "full-time",
                "experience_level": "mid"
            },
            {
                "title": "Database Administrator",
                "company": "Data Solutions",
                "description": """DBA to manage and optimize our database infrastructure. 
                Requirements: PostgreSQL, MySQL, database performance tuning, backup/recovery. 
                Monitor query performance, design schemas, implement replication. 
                Experience with database security, indexing strategies, and capacity planning.""",
                "url": "https://example.com/jobs/9",
                "location": "Chicago, IL",
                "tags": ["PostgreSQL", "MySQL", "SQL", "Database", "Performance"],
                "salary_min": 110000,
                "salary_max": 150000,
                "employment_type": "full-time",
                "experience_level": "mid"
            },
            {
                "title": "Software Engineering Intern",
                "company": "BigTech",
                "description": """Summer internship for CS students. 
                Requirements: CS student, knowledge of Python/Java, data structures, algorithms. 
                Work on real projects, mentorship from senior engineers, learn industry practices. 
                No prior experience required, just passion for coding!""",
                "url": "https://example.com/jobs/10",
                "location": "Mountain View, CA",
                "tags": ["Python", "Java", "Internship", "Computer Science"],
                "salary_min": 40000,
                "salary_max": 60000,
                "employment_type": "internship",
                "experience_level": "entry"
            }
        ]
        
        normalized_jobs = []
        for job in sample_jobs:
            normalized = self.normalize_job(job)
            normalized_jobs.append(normalized)
        
        logger.info(f"Generated {len(normalized_jobs)} mock jobs")
        return normalized_jobs
    
    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize mock job data."""
        job_id = self.generate_job_id(
            raw_data["title"],
            raw_data["company"],
            raw_data["url"]
        )
        
        return {
            "job_id": job_id,
            "source": self.source_name,
            "title": raw_data["title"],
            "company": raw_data["company"],
            "description": raw_data["description"],
            "url": raw_data["url"],
            "location": raw_data.get("location"),
            "tags": raw_data.get("tags", []),
            "salary_min": raw_data.get("salary_min"),
            "salary_max": raw_data.get("salary_max"),
            "employment_type": raw_data.get("employment_type"),
            "experience_level": raw_data.get("experience_level"),
        }


class RSSJobScraper(JobScraper):
    """
    Generic RSS feed job scraper.
    
    Can be used for Indeed RSS, RemoteOK, and other RSS-based job boards.
    """
    
    def __init__(self, source_name: str, feed_url: str):
        super().__init__(source_name)
        self.feed_url = feed_url
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape jobs from RSS feed."""
        logger.info(f"Scraping RSS feed: {self.feed_url}")
        
        try:
            feed = feedparser.parse(self.feed_url)
            jobs = []
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                job = self.normalize_job(entry)
                if job:
                    jobs.append(job)
            
            logger.info(f"Scraped {len(jobs)} jobs from RSS feed")
            return jobs
            
        except Exception as e:
            logger.error(f"RSS scraping error: {e}")
            return []
    
    def normalize_job(self, entry: Any) -> Optional[Dict[str, Any]]:
        """Normalize RSS feed entry to job format."""
        try:
            title = entry.get("title", "")
            link = entry.get("link", "")
            description = entry.get("summary", entry.get("description", ""))
            
            # Extract company from title (format: "Job Title - Company")
            company = "Unknown"
            if " - " in title:
                parts = title.split(" - ")
                title = parts[0].strip()
                company = parts[1].strip()
            
            job_id = self.generate_job_id(title, company, link)
            
            return {
                "job_id": job_id,
                "source": self.source_name,
                "title": title,
                "company": company,
                "description": description,
                "url": link,
                "location": None,
                "tags": [],
                "salary_min": None,
                "salary_max": None,
                "employment_type": "full-time",
                "experience_level": None,
            }
        except Exception as e:
            logger.error(f"Error normalizing RSS entry: {e}")
            return None


async def ingest_jobs_from_sources() -> List[Dict[str, Any]]:
    """
    Ingest jobs from all configured sources.
    
    Returns:
        List of normalized job dictionaries
    """
    all_jobs = []
    
    # Mock scraper for testing
    mock_scraper = MockJobScraper()
    mock_jobs = await mock_scraper.scrape()
    all_jobs.extend(mock_jobs)
    
    # Add RSS scrapers here when ready
    # rss_scraper = RSSJobScraper("indeed", "https://rss.indeed.com/...")
    # rss_jobs = await rss_scraper.scrape()
    # all_jobs.extend(rss_jobs)
    
    logger.info(f"Total jobs ingested: {len(all_jobs)}")
    return all_jobs
