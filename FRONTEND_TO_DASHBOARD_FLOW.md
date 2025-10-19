# 🎯 **Frontend → Supabase Dashboard Flow**

## 📋 **Complete Journey of an Uploaded Resume**

```
USER UPLOADS RESUME
        ↓
[Streamlit Frontend]
   app_v2.py
        ↓
    HTTP POST
        ↓
[FastAPI Backend]
   documents/routes.py
        ↓
 get_storage() function
        ↓
[SupabaseStorage Handler]
   storage/handler.py
        ↓
  save_file() method
        ↓
[Supabase Cloud Storage]
   Bucket: aligncv-resumes
   Path: user_123/20231019_143052_resume.pdf
        ↓
✅ VISIBLE IN DASHBOARD!
```

---

## 👀 **How to See Files in Dashboard**

### **Step 1: Open Supabase Storage**
```
https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets
```

### **Step 2: Click on Bucket**
Click on: **`aligncv-resumes`**

### **Step 3: Browse Folders**
You'll see folders like:
```
📁 user_1/
   📄 20231018_105030_john_doe_resume.pdf
   📄 20231019_141523_jane_smith_cv.docx

📁 user_2/
   📄 20231019_093045_alex_resume.pdf

📁 user_999/  (← From our test!)
   📄 test_resume.txt
```

### **Step 4: View/Download Files**
- Click any file → Opens preview
- Click "Download" → Downloads to your computer
- Click "Delete" → Removes from storage

---

## 🧪 **Test the Flow**

### **1. Start Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.v2.app_v2:app_v2 --port 8001
```

### **2. Start Frontend (New Terminal):**
```powershell
cd frontend
streamlit run app_v2.py --server.port 8502
```

### **3. Upload Resume:**
1. Open: http://localhost:8502
2. Login/Register user
3. Go to "Documents" page
4. Click "Upload Resume"
5. Select a PDF/DOCX file
6. Click "Upload"

### **4. Check Supabase Dashboard:**
1. Open: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets/aligncv-resumes
2. Look for: `user_1/` (or whatever user ID you logged in as)
3. See your uploaded file! 🎉

---

## 🔍 **What You'll See in Dashboard**

### **Example:**

**Before Upload:**
```
Storage > aligncv-resumes
└── (empty or test files only)
```

**After Frontend Upload:**
```
Storage > aligncv-resumes
├── user_1/
│   └── 20231019_143052_my_resume.pdf  ← NEW FILE!
└── user_999/
    └── test_resume.txt  (← From test script)
```

---

## 📊 **File Naming Convention**

Files are stored as:
```
user_{USER_ID}/{TIMESTAMP}_{ORIGINAL_FILENAME}
```

**Example:**
- User ID: `1`
- Timestamp: `20231019_143052` (Oct 19, 2023 at 2:30:52 PM)
- Original filename: `john_resume.pdf`
- **Stored as:** `user_1/20231019_143052_john_resume.pdf`

---

## ✅ **Benefits of This Setup**

| Feature | Benefit |
|---------|---------|
| **User Folders** | Each user's files isolated |
| **Timestamps** | No filename conflicts |
| **Cloud Storage** | Files survive server restarts |
| **Dashboard Access** | View/manage files visually |
| **Direct Downloads** | Can download from dashboard |
| **Backup** | Supabase handles backups |

---

## 🚨 **Current Blocker**

**Issue:** API keys not working
**Fix:** Update keys in [`.env`](.env ) from: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/settings/api

**Once fixed:**
✅ Test script will pass
✅ Frontend uploads will work
✅ Files will appear in dashboard immediately!

---

## 📝 **Quick Verification Checklist**

After fixing API keys:

- [ ] Run `python test_supabase_storage.py` → Should pass all tests
- [ ] Start backend + frontend
- [ ] Upload a resume through frontend
- [ ] Check Supabase dashboard → File appears in `user_X/` folder
- [ ] Download file from dashboard → Matches uploaded file
- [ ] Delete file from dashboard → Disappears from storage

---

**TL;DR:** Once API keys are fixed, every resume uploaded through frontend will instantly appear in Supabase dashboard under `user_X/` folders! 🎉
