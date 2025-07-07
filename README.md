# SENSOR-NAME-EXTRACTOR
# 📦 Sensor Query Cleaner & Auto Tagger (Box Silvassa)

This Streamlit app extracts clean product queries from WhatsApp `.txt` chat exports — specifically from **Box Silvassa** customer messages. It removes irrelevant messages, detects product names (with models), quantities, and dates, and auto-tags the sensor type.

---

## ✅ Features

- 🧹 Cleans messy WhatsApp `.txt` chat files
- 📅 Extracts **date**, **product name**, and **quantity**
- 🏷️ Auto-tags **sensor type**:
  - Proximity
  - Reed Switch
  - Photoelectric
  - Capacitive
  - Inductive
  - Pressure
  - Temperature
- ❌ Removes conversational lines like:
  - “extra dalwa dena”
  - “check this”
  - “send photo”, etc.
- 📤 Download cleaned results in **Excel** format

---

## 📁 Input Format

Upload a **WhatsApp chat export (.txt)** with lines like:

