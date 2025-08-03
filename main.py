
from fastapi import FastAPI, Query, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.responses import JSONResponse
import csv
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "supersecretapikey123"

# File paths
CSV_FILE = "webhook_data.csv"
CHARTS_DIR = "charts"

# Google Sheets Configuration
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1Z2V3vJMgfDi71eYxU2-7iC0Yj8eE-vNseIssjiNUxA0/edit?usp=sharing"
SPREADSHEET_ID = "1Z2V3vJMgfDi71eYxU2-7iC0Yj8eE-vNseIssjiNUxA0"
GOOGLE_CREDENTIALS_FILE = "google-credentials.json"

# Create charts directory if it doesn't exist
os.makedirs(CHARTS_DIR, exist_ok=True)

def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI(title="Brokerage Load Search API with Google Sheets Integration")

# Allow HappyRobot to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample in-memory load database
loads = [
    {
        "load_id": "7890",
        "origin": "Chicago, IL",
        "destination": "Dallas, TX",
        "pickup_datetime": "2025-08-01T09:00:00",
        "delivery_datetime": "2025-08-02T17:00:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1200,
        "notes": "High-priority",
        "weight": 30000,
        "commodity_type": "Electronics",
        "num_of_pieces": 26,
        "miles": 950,
        "dimensions": "48x102"
    },
    {
        "load_id": "7891",
        "origin": "Queens, NY",
        "destination": "Orlando, FL",
        "pickup_datetime": "2025-08-01T08:00:00",
        "delivery_datetime": "2025-08-03T15:00:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1500,
        "notes": "Reefer required",
        "weight": 25000,
        "commodity_type": "Perishables",
        "num_of_pieces": 22,
        "miles": 1080,
        "dimensions": "48x102"
    }
]

class Load(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str]
    weight: int
    commodity_type: str
    num_of_pieces: int
    miles: int
    dimensions: str

class WebhookData(BaseModel):
    timestamp: str
    booking_intent: Optional[str]
    counter_offer: Optional[str]
    agreed_rate: Optional[str]
    negotiation_attempts: Optional[str]
    sentiment: Optional[str]
    call_outcome: Optional[str]
    raw_payload: Optional[Dict[str, Any]]

class DataManager:
    def __init__(self):
        self.csv_file = CSV_FILE
        self.charts_dir = CHARTS_DIR
        self.spreadsheet_id = SPREADSHEET_ID
        self.csv_fields = [
            "id", "timestamp", "booking_intent", "counter_offer", "agreed_rate",
            "negotiation_attempts", "sentiment", "call_outcome", "raw_payload"
        ]
        self.google_client = None
        self.spreadsheet = None
        
    def get_google_client(self):
        """Initialize Google Sheets client"""
        if self.google_client is None:
            try:
                # Check if credentials file exists
                if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                    logger.error(f"Google credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
                    logger.error("Please create google-credentials.json with your Google Sheets API credentials")
                    return None
                
                # Define the scope
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                # Load credentials
                credentials = Credentials.from_service_account_file(
                    GOOGLE_CREDENTIALS_FILE, scopes=scope
                )
                
                # Create client
                self.google_client = gspread.authorize(credentials)
                logger.info("Google Sheets client initialized successfully")
                
            except Exception as e:
                logger.error(f"Error initializing Google Sheets client: {str(e)}")
                return None
        
        return self.google_client
    
    def get_spreadsheet(self):
        """Get or create the Google Spreadsheet"""
        if self.spreadsheet is None:
            client = self.get_google_client()
            if client is None:
                return None
            
            try:
                # Try to open existing spreadsheet
                self.spreadsheet = client.open_by_key(self.spreadsheet_id)
                logger.info(f"Opened existing spreadsheet: {self.spreadsheet.title}")
            except gspread.SpreadsheetNotFound:
                logger.error(f"Spreadsheet not found with ID: {self.spreadsheet_id}")
                return None
            except Exception as e:
                logger.error(f"Error accessing spreadsheet: {str(e)}")
                return None
        
        return self.spreadsheet
    
    def get_next_id(self) -> int:
        """Get the next ID for the record"""
        if not os.path.exists(self.csv_file):
            return 1
        
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            records = list(reader)
            if not records:
                return 1
            return max(int(record.get('id', 0)) for record in records) + 1
    
    def save_to_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save data to CSV file"""
        record_id = self.get_next_id()
        data['id'] = record_id
        
        file_exists = os.path.isfile(self.csv_file)
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        
        logger.info(f"Saved record {record_id} to CSV")
        return data
    
    def save_to_google_sheets(self, data: Dict[str, Any]) -> bool:
        """Save data to Google Sheets"""
        try:
            spreadsheet = self.get_spreadsheet()
            if spreadsheet is None:
                logger.error("Could not access Google Spreadsheet")
                return False
            
            # Get or create the main data worksheet
            try:
                worksheet = spreadsheet.worksheet("Webhook Data")
            except gspread.WorksheetNotFound:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(title="Webhook Data", rows=1000, cols=20)
                # Add headers
                worksheet.append_row(self.csv_fields)
                logger.info("Created new worksheet: Webhook Data")
            
            # Prepare row data
            row_data = [
                data.get('id', ''),
                data.get('timestamp', ''),
                data.get('booking_intent', ''),
                data.get('counter_offer', ''),
                data.get('agreed_rate', ''),
                data.get('negotiation_attempts', ''),
                data.get('sentiment', ''),
                data.get('call_outcome', ''),
                data.get('raw_payload', '')
            ]
            
            # Append row to worksheet
            worksheet.append_row(row_data)
            logger.info(f"Saved record {data.get('id')} to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {str(e)}")
            return False
    
    def update_google_sheets_analytics(self):
        """Update analytics in Google Sheets"""
        try:
            spreadsheet = self.get_spreadsheet()
            if spreadsheet is None:
                return False
            
            # Get or create analytics worksheet
            try:
                analytics_worksheet = spreadsheet.worksheet("Analytics")
            except gspread.WorksheetNotFound:
                analytics_worksheet = spreadsheet.add_worksheet(title="Analytics", rows=100, cols=10)
                logger.info("Created new worksheet: Analytics")
            
            # Read CSV data for analytics
            if not os.path.exists(self.csv_file):
                return False
            
            df = pd.read_csv(self.csv_file)
            
            # Clear existing data
            analytics_worksheet.clear()
            
            # Add summary statistics
            analytics_data = [
                ["Summary Statistics"],
                ["", ""],
                ["Total Records", len(df)],
                ["Successful Bookings", len(df[df['booking_intent'] == 'yes']) if 'booking_intent' in df.columns else 0],
                ["Positive Sentiment", len(df[df['sentiment'] == 'positive']) if 'sentiment' in df.columns else 0],
                ["", ""],
                ["Average Negotiation Attempts", ""]
            ]
            
            # Calculate average negotiation attempts
            if 'negotiation_attempts' in df.columns:
                try:
                    negotiation_attempts = df['negotiation_attempts'].astype(str).str.extract(r'(\d+)').astype(float)
                    avg_negotiation = negotiation_attempts.mean()
                    avg_negotiation = round(avg_negotiation, 2) if not pd.isna(avg_negotiation) else 0
                    analytics_data[6][1] = avg_negotiation
                except:
                    analytics_data[6][1] = 0
            
            # Write analytics data
            for row in analytics_data:
                analytics_worksheet.append_row(row)
            
            logger.info("Updated Google Sheets analytics")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Google Sheets analytics: {str(e)}")
            return False
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records from CSV file"""
        if not os.path.exists(self.csv_file):
            return []
        
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def generate_charts(self):
        """Generate charts from the data"""
        if not os.path.exists(self.csv_file):
            return
        
        try:
            # Read data
            df = pd.read_csv(self.csv_file)
            
            if len(df) == 0:
                logger.info("No data available for chart generation")
                return
            
            # Set style
            plt.style.use('default')  # Use default style for better compatibility
            sns.set_palette("husl")
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('HappyRobot Webhook Data Analytics', fontsize=16, fontweight='bold')
            
            # 1. Booking Intent Distribution (Pie Chart)
            if 'booking_intent' in df.columns and len(df['booking_intent'].value_counts()) > 0:
                booking_counts = df['booking_intent'].value_counts()
                axes[0, 0].pie(booking_counts.values, labels=booking_counts.index, autopct='%1.1f%%', startangle=90)
                axes[0, 0].set_title('Booking Intent Distribution', fontweight='bold')
            else:
                axes[0, 0].text(0.5, 0.5, 'No booking intent data', ha='center', va='center', transform=axes[0, 0].transAxes)
                axes[0, 0].set_title('Booking Intent Distribution', fontweight='bold')
            
            # 2. Sentiment Analysis (Bar Chart)
            if 'sentiment' in df.columns and len(df['sentiment'].value_counts()) > 0:
                sentiment_counts = df['sentiment'].value_counts()
                colors = ['green', 'red', 'orange', 'blue', 'purple'][:len(sentiment_counts)]
                axes[0, 1].bar(sentiment_counts.index, sentiment_counts.values, color=colors)
                axes[0, 1].set_title('Sentiment Analysis', fontweight='bold')
                axes[0, 1].set_ylabel('Count')
            else:
                axes[0, 1].text(0.5, 0.5, 'No sentiment data', ha='center', va='center', transform=axes[0, 1].transAxes)
                axes[0, 1].set_title('Sentiment Analysis', fontweight='bold')
            
            # 3. Call Outcome Analysis (Horizontal Bar Chart)
            if 'call_outcome' in df.columns and len(df['call_outcome'].value_counts()) > 0:
                outcome_counts = df['call_outcome'].value_counts()
                axes[1, 0].barh(outcome_counts.index, outcome_counts.values, color='skyblue')
                axes[1, 0].set_title('Call Outcome Analysis', fontweight='bold')
                axes[1, 0].set_xlabel('Count')
            else:
                axes[1, 0].text(0.5, 0.5, 'No call outcome data', ha='center', va='center', transform=axes[1, 0].transAxes)
                axes[1, 0].set_title('Call Outcome Analysis', fontweight='bold')
            
            # 4. Negotiation Attempts Distribution (Histogram)
            if 'negotiation_attempts' in df.columns:
                try:
                    negotiation_attempts = df['negotiation_attempts'].astype(str).str.extract(r'(\d+)').astype(float)
                    valid_attempts = negotiation_attempts.dropna()
                    if len(valid_attempts) > 0:
                        axes[1, 1].hist(valid_attempts, bins=min(10, len(valid_attempts)), color='lightcoral', alpha=0.7, edgecolor='black')
                        axes[1, 1].set_title('Negotiation Attempts Distribution', fontweight='bold')
                        axes[1, 1].set_xlabel('Number of Attempts')
                        axes[1, 1].set_ylabel('Frequency')
                    else:
                        axes[1, 1].text(0.5, 0.5, 'No negotiation data', ha='center', va='center', transform=axes[1, 1].transAxes)
                        axes[1, 1].set_title('Negotiation Attempts Distribution', fontweight='bold')
                except:
                    axes[1, 1].text(0.5, 0.5, 'No negotiation data', ha='center', va='center', transform=axes[1, 1].transAxes)
                    axes[1, 1].set_title('Negotiation Attempts Distribution', fontweight='bold')
            else:
                axes[1, 1].text(0.5, 0.5, 'No negotiation data', ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('Negotiation Attempts Distribution', fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_file = os.path.join(self.charts_dir, f"webhook_analytics_{timestamp}.png")
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Generated charts: {chart_file}")
            
            # Generate additional detailed charts
            self.generate_detailed_charts(df, timestamp)
            
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
            # Don't raise exception, just log the error
    
    def generate_detailed_charts(self, df: pd.DataFrame, timestamp: str):
        """Generate additional detailed charts"""
        
        # 1. Rate Analysis Chart
        plt.figure(figsize=(12, 6))
        
        # Extract numeric values from rate columns
        counter_offers = df['counter_offer'].astype(str).str.extract(r'(\d+)').astype(float)
        agreed_rates = df['agreed_rate'].astype(str).str.extract(r'(\d+)').astype(float)
        
        # Create rate comparison
        valid_data = counter_offers.notna() & agreed_rates.notna()
        if valid_data.sum() > 0:
            plt.subplot(1, 2, 1)
            plt.scatter(counter_offers[valid_data], agreed_rates[valid_data], alpha=0.6, color='blue')
            plt.plot([counter_offers[valid_data].min(), counter_offers[valid_data].max()], 
                    [counter_offers[valid_data].min(), counter_offers[valid_data].max()], 
                    'r--', alpha=0.5, label='Perfect Match')
            plt.xlabel('Counter Offer')
            plt.ylabel('Agreed Rate')
            plt.title('Counter Offer vs Agreed Rate')
            plt.legend()
        
        # 2. Time Series Analysis
        plt.subplot(1, 2, 2)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        daily_bookings = df[df['booking_intent'] == 'yes'].groupby(df['timestamp'].dt.date).size()
        plt.plot(daily_bookings.index, daily_bookings.values, marker='o', linewidth=2, markersize=6)
        plt.xlabel('Date')
        plt.ylabel('Successful Bookings')
        plt.title('Daily Successful Bookings')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        detailed_chart_file = os.path.join(self.charts_dir, f"detailed_analytics_{timestamp}.png")
        plt.savefig(detailed_chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Generated detailed charts: {detailed_chart_file}")
        
        # Upload charts to Google Sheets
        self.upload_charts_to_sheets(timestamp)

    def upload_charts_to_sheets(self, timestamp: str):
        """Upload generated charts to Google Sheets"""
        try:
            client = self.get_google_client()
            if not client:
                return False
            
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            # Get or create "Charts" worksheet
            try:
                charts_worksheet = spreadsheet.worksheet("Charts")
            except gspread.WorksheetNotFound:
                charts_worksheet = spreadsheet.add_worksheet(title="Charts", rows=1000, cols=20)
                # Add headers
                headers = ["Chart Type", "Generated At", "Description", "File Path"]
                charts_worksheet.append_row(headers)
            
            # Add chart information to the worksheet
            chart_files = [
                f"webhook_analytics_{timestamp}.png",
                f"detailed_analytics_{timestamp}.png"
            ]
            
            chart_info = [
                ["Main Analytics Dashboard", timestamp, "Booking Intent, Sentiment, Call Outcome, and Negotiation Attempts", f"charts/webhook_analytics_{timestamp}.png"],
                ["Detailed Analytics", timestamp, "Rate Analysis and Time Series Analysis", f"charts/detailed_analytics_{timestamp}.png"]
            ]
            
            for info in chart_info:
                charts_worksheet.append_row(info)
            
            logger.info("Charts information uploaded to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading charts to Google Sheets: {str(e)}")
            return False

# Initialize data manager
data_manager = DataManager()

@app.get("/search", response_model=List[Load])
def search_loads(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    load_id: Optional[str] = Query(None),
    auth: None = Depends(verify_api_key)
):
    results = loads

    if load_id:
        results = [l for l in results if l["load_id"] == load_id]
    if origin:
        results = [l for l in results if origin.lower() in l["origin"].lower()]
    if destination:
        results = [l for l in results if destination.lower() in l["destination"].lower()]

    if not results:
        raise HTTPException(status_code=404, detail="No matching loads found")

    return results

@app.post("/webhook")
async def webhook_receiver(request: Request):
    """Receive webhook data from HappyRobot and store in CSV/Google Sheets with charts"""
    try:
        payload = await request.json()
        logger.info(f"Received webhook payload: {payload}")
        
        # Prepare data for storage
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "booking_intent": payload.get("booking_intent", ""),
            "counter_offer": payload.get("counter_offer", ""),
            "agreed_rate": payload.get("agreed_rate", ""),
            "negotiation_attempts": payload.get("negotiation_attempts", ""),
            "sentiment": payload.get("sentiment", ""),
            "call_outcome": payload.get("call_outcome", ""),
            "raw_payload": json.dumps(payload)
        }
        
        # Save to CSV
        saved_data = data_manager.save_to_csv(data)
        
        # Save to Google Sheets
        google_sheets_success = data_manager.save_to_google_sheets(saved_data)
        
        # Update Google Sheets analytics
        analytics_success = data_manager.update_google_sheets_analytics()
        
        # Generate charts
        data_manager.generate_charts()
        
        logger.info(f"Successfully processed webhook data with ID: {saved_data['id']}")
        return JSONResponse(
            content={
                "status": "success",
                "message": "Data stored successfully",
                "record_id": saved_data['id'],
                "timestamp": data["timestamp"],
                "files_updated": [CSV_FILE],
                "google_sheets_updated": google_sheets_success,
                "analytics_updated": analytics_success,
                "charts_generated": True,
                "google_sheets_url": GOOGLE_SHEETS_URL
            }, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@app.get("/dashboard")
async def get_dashboard_data(auth: None = Depends(verify_api_key)):
    """Retrieve all webhook data from CSV file for dashboard display"""
    try:
        records = data_manager.get_all_records()
        logger.info(f"Retrieved {len(records)} records for dashboard")
        return {
            "status": "success",
            "count": len(records),
            "data": records,
            "files": {
                "csv": CSV_FILE,
                "charts_directory": CHARTS_DIR,
                "google_sheets_url": GOOGLE_SHEETS_URL
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@app.get("/files")
async def get_files_info(auth: None = Depends(verify_api_key)):
    """Get information about generated files"""
    try:
        files_info = {
            "csv_file": {
                "path": CSV_FILE,
                "exists": os.path.exists(CSV_FILE),
                "size": os.path.getsize(CSV_FILE) if os.path.exists(CSV_FILE) else 0
            },
            "charts_directory": {
                "path": CHARTS_DIR,
                "exists": os.path.exists(CHARTS_DIR),
                "chart_count": len([f for f in os.listdir(CHARTS_DIR) if f.endswith('.png')]) if os.path.exists(CHARTS_DIR) else 0
            },
            "google_sheets": {
                "url": GOOGLE_SHEETS_URL,
                "spreadsheet_id": SPREADSHEET_ID,
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "credentials_exist": os.path.exists(GOOGLE_CREDENTIALS_FILE)
            }
        }
        return files_info
    except Exception as e:
        logger.error(f"Error getting files info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting files info: {str(e)}")

@app.get("/generate-charts")
async def generate_charts_endpoint(auth: None = Depends(verify_api_key)):
    """Manually trigger chart generation and upload to Google Sheets"""
    try:
        # Generate charts
        data_manager.generate_charts()
        
        logger.info("Charts generated and uploaded to Google Sheets successfully")
        return JSONResponse(
            content={
                "status": "success",
                "message": "Charts generated and uploaded to Google Sheets",
                "timestamp": datetime.utcnow().isoformat(),
                "google_sheets_url": GOOGLE_SHEETS_URL,
                "charts_worksheet": "Charts"
            }, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating charts: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)