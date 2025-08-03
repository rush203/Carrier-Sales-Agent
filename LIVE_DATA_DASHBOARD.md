# 📊 Live Data Dashboard

## 🔗 **Google Sheets Integration**

Your Carrier Sales Agent application is successfully integrated with Google Sheets for real-time data storage and analytics.

### **📊 Live Dashboard URL**

**[View Live HappyRobot Data](https://docs.google.com/spreadsheets/d/1Z2V3vJMgfDi71eYxU2-7iC0Yj8eE-vNseIssjiNUxA0/edit?gid=1898833320#gid=1898833320)**

---

## 📈 **Current Data Summary**

### **📊 Data Overview**
- **Total Records**: 13 entries
- **Latest Entry**: 2025-08-03T18:51:09.385626
- **Data Source**: HappyRobot AI webhook integration
- **Update Frequency**: Real-time

### **📋 Data Fields**

| Field | Description | Example Values |
|-------|-------------|----------------|
| **id** | Unique record identifier | 1, 2, 3, ... |
| **timestamp** | Data capture time | 2025-08-03T18:51:09.385626 |
| **booking_intent** | Customer booking intention | yes, no, maybe |
| **counter_offer** | Proposed rate | 2000, 2500, 3000 |
| **agreed_rate** | Final agreed rate | 2100, 2400, 1250 |
| **negotiation_attempts** | Number of negotiations | 1, 2, 3, 4 |
| **sentiment** | Call sentiment analysis | positive, neutral, negative |
| **call_outcome** | Final call result | booked, declined, pending |
| **raw_payload** | Complete webhook data | JSON format |

### **📊 Data Insights**

#### **Booking Intent Distribution**
- **Yes**: 6 records (46%)
- **No**: 4 records (31%)
- **Maybe**: 3 records (23%)

#### **Rate Analysis**
- **Minimum Rate**: $1,250
- **Maximum Rate**: $3,000
- **Average Rate**: $2,050
- **Rate Range**: $1,750

#### **Sentiment Analysis**
- **Positive**: 7 records (54%)
- **Neutral**: 3 records (23%)
- **Negative**: 3 records (23%)

#### **Call Outcomes**
- **Booked**: 6 records (46%)
- **Declined**: 4 records (31%)
- **Pending**: 3 records (23%)

---

## 🔄 **Real-Time Integration**

### **How It Works**
1. **HappyRobot AI** processes inbound carrier calls
2. **Webhook Data** sent to FastAPI server
3. **Data Processing** validates and formats information
4. **Google Sheets** receives real-time updates
5. **Analytics** generated automatically

### **Data Flow**
```
HappyRobot AI → FastAPI Server → Google Sheets → Analytics
```

---

## 📊 **Sample Data Entries**

| ID | Timestamp | Booking Intent | Counter Offer | Agreed Rate | Negotiations | Sentiment | Outcome |
|----|-----------|----------------|---------------|-------------|--------------|-----------|---------|
| 1 | 2025-08-02T23:16:57 | yes | 2000 | 2100 | 2 | positive | booked |
| 2 | 2025-08-02T23:17:08 | no | 2200 | - | 1 | negative | declined |
| 3 | 2025-08-02T23:17:15 | maybe | 2000 | 2000 | 2 | neutral | pending |
| 4 | 2025-08-02T23:18:45 | yes | 2500 | 2400 | 3 | positive | booked |
| 5 | 2025-08-02T23:19:06 | no | 3000 | - | 1 | negative | declined |

---

## 🎯 **Business Intelligence**

### **Key Metrics**
- **Booking Success Rate**: 46%
- **Average Negotiation Attempts**: 2.2
- **Positive Sentiment Rate**: 54%
- **Data Processing Speed**: Real-time

### **Trends Observed**
- Higher rates ($2,500+) show better booking success
- Multiple negotiation attempts correlate with positive outcomes
- Positive sentiment strongly predicts booking success

---

## 🔧 **Technical Details**

### **Integration Features**
- ✅ **Real-time Updates**: Instant data synchronization
- ✅ **Data Validation**: Automatic field validation
- ✅ **Error Handling**: Robust error management
- ✅ **Backup Storage**: CSV file backup
- ✅ **Analytics Generation**: Automated chart creation

### **Security**
- 🔐 **API Key Authentication**: Secure access control
- 🔒 **Google Sheets Permissions**: Service account access
- 🛡️ **Data Encryption**: HTTPS transmission
- 📝 **Audit Trail**: Complete data history

---

## 📞 **Support & Access**

### **Accessing the Dashboard**
1. **Direct Link**: [Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/1Z2V3vJMgfDi71eYxU2-7iC0Yj8eE-vNseIssjiNUxA0/edit?gid=1898833320#gid=1898833320)
2. **API Access**: Use `/dashboard` endpoint
3. **Manual Export**: Download as CSV

### **Permissions**
- **View Access**: Public (read-only)
- **Edit Access**: Service account only
- **Analytics**: Automated generation

---

## 🚀 **Next Steps**

### **Enhanced Analytics**
- [ ] **Real-time Charts**: Live dashboard visualization
- [ ] **Predictive Analytics**: ML-powered insights
- [ ] **Custom Reports**: Business-specific metrics
- [ ] **Alert System**: Automated notifications

### **Integration Expansion**
- [ ] **Database Migration**: PostgreSQL integration
- [ ] **Advanced Analytics**: Machine learning insights
- [ ] **Mobile Dashboard**: React Native app
- [ ] **API Enhancements**: Additional endpoints

---

**📊 Dashboard URL**: https://docs.google.com/spreadsheets/d/1Z2V3vJMgfDi71eYxU2-7iC0Yj8eE-vNseIssjiNUxA0/edit?gid=1898833320#gid=1898833320  
**Last Updated**: August 3, 2025  
**Status**: ✅ **Active & Operational** 